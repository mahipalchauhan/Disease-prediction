from flask import Flask, render_template, request, redirect, url_for, session, flash
from model import enhanced_search
from models import db, User
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'  # Will Replace this in Future Production

db.init_app(app)

with app.app_context():
    db.create_all()

# Show dashboard if logged in, else go to login
@app.route('/')
def root():
    if 'user_id' in session:
        flash('Welcome back!', 'success')
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access your dashboard', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

# Main page after login
@app.route('/index')
def index():
    if 'user_id' not in session:
        flash('Please login to access this page', 'warning')
        return redirect(url_for('login'))
    
    categories = sorted({row['Category'] for _, row in enhanced_search.df.iterrows() if pd.notna(row['Category'])})
    featured_diseases = [row.to_dict() for _, row in enhanced_search.df.head(6).iterrows()]
    return render_template('index.html', categories=categories, featured_diseases=featured_diseases)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('signup.html', layout='no_layout')

        new_user = User(
            username=username,
            password=password,
            email=email,
            age=age,
            gender=gender
        )
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Account created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html', layout='no_layout')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return render_template('login.html', layout='no_layout')

    return render_template('login.html', layout='no_layout')

# Logout route
@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# Symptom checker
@app.route('/symptom_search', methods=['GET', 'POST'])
def symptom_search():
    if 'user_id' not in session:
        flash('Please login to use the symptom checker', 'warning')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    all_symptoms = sorted({symptom.strip().lower()
                          for _, row in enhanced_search.df.iterrows()
                          for symptom in str(row['Symptoms']).split(',')
                          if symptom.strip()})

    if request.method == 'POST':
        selected_symptoms = [request.form.get(f'symptom{i}') for i in range(1, 5)]
        selected_symptoms = [s for s in selected_symptoms if s]
        selected_symptoms = list(set([s.lower().strip() for s in selected_symptoms]))
        gender = request.form.get('gender', '')
        age_group = request.form.get('age_group', '')
        pregnancy = request.form.get('pregnancy', '')

        if not selected_symptoms:
            flash('Please select at least one symptom', 'error')
            return render_template('symptom_search.html', all_symptoms=all_symptoms)

        age_mapping = {
            'neonatal': '0',
            'pediatric': '5',
            'teens': '15',
            'adult': '40',
            'elderly': '70'
        }
        age = age_mapping.get(age_group.lower()) if age_group else None

        results = enhanced_search.search(
            selected_symptoms,
            age=age,
            gender=gender,
            pregnancy_status=pregnancy
        )

        formatted_results = []
        for r in results:
            formatted_results.append({
                'disease': {
                    'name': r['name'],
                    'category': r['category'],
                    'symptoms': r['symptoms'],
                    'first_line_meds': r['first_line_meds'],
                    'real_world_protocol': r['real_world_protocol'],
                    'gender': r['gender'],
                    'age_group': r['age_group'],
                    'pregnancy_safety': r['pregnancy_safety'],
                    'cost_tier': r['cost_tier'],
                    'comorbidities': r['comorbidities'],
                    'precautions': r['precautions'],
                    'diet': r['diet'],
                    'workout': r['workout']
                },
                'match_percentage': min(99, max(1, round(r['match_score'] * 100)))
            })

        return render_template('symptom_results.html',
                             selected_symptoms=selected_symptoms,
                             results=formatted_results,
                             selected_gender=gender,
                             selected_age_group=age_group,
                             pregnancy=pregnancy,
                             user=user)

    return render_template('symptom_search.html', all_symptoms=all_symptoms)

# Category view

@app.route('/category/<category_name>')
def category(category_name):
    if 'user_id' not in session:
        flash('Please login to browse categories', 'warning')
        return redirect(url_for('login'))

    # Filter only matching category
    filtered_df = enhanced_search.df[
        enhanced_search.df['Category'].str.lower() == category_name.lower()
    ]

    # Drop duplicate diseases (by name)
    unique_diseases_df = filtered_df.drop_duplicates(subset='Disease')

    # Sorting the diseases
    unique_diseases_df = unique_diseases_df.sort_values(by='Disease')

    # For debugging — print number of diseases in console
    print(f"Found {len(unique_diseases_df)} unique diseases in category: {category_name}")

    # Convert to dicts
    category_diseases = unique_diseases_df.to_dict(orient='records')

    return render_template('category.html',
                         category_name=category_name,
                         diseases=category_diseases)


# Disease details
@app.route('/disease/<disease_name>')
def disease(disease_name):
    if 'user_id' not in session:
        flash('Please login to view disease details', 'warning')
        return redirect(url_for('login'))

    disease_data = next((row.to_dict() for _, row in enhanced_search.df.iterrows()
                        if str(row['Disease']).lower() == disease_name.lower()), None)
    if not disease_data:
        flash('Disease not found', 'error')
        return redirect(url_for('index'))

    fields_to_check = ['Comorbidities', 'Precautions', 'Diet', 'Workout']
    for field in fields_to_check:
        disease_data[field] = disease_data.get(field, 'N/A')
        if pd.isna(disease_data[field]):
            disease_data[field] = 'N/A'

    if isinstance(disease_data['Comorbidities'], str) and disease_data['Comorbidities'] != 'N/A':
        disease_data['Comorbidities'] = disease_data['Comorbidities'].split(', ')

    related = []
    current_symptoms = set(str(disease_data['Symptoms']).lower().split(', '))
    for _, row in enhanced_search.df.iterrows():
        if str(row['Disease']).lower() != disease_name.lower():
            other_symptoms = set(str(row['Symptoms']).lower().split(', '))
            if current_symptoms & other_symptoms:
                related.append(row['Disease'])

    return render_template('disease.html',
                         disease=disease_data,
                         related_diseases=related[:5])

# Static pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')


if __name__ == '__main__':
    app.run(debug=True)