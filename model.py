import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB

class EnhancedDiseaseSearch:
    def __init__(self, disease_data):
        self.df = disease_data

        # TF-IDF for symptom similarity
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            analyzer='word'
        )
        self.df['Processed_Symptoms'] = self.df['Symptoms'].apply(
            lambda x: ' '.join(str(x).replace(',', ' ').split()))
        self.symptom_matrix = self.vectorizer.fit_transform(self.df['Processed_Symptoms'])

        # CountVectorizer + Naive Bayes
        self.nb_vectorizer = CountVectorizer()
        self.nb_X = self.nb_vectorizer.fit_transform(self.df['Symptoms'])
        self.nb_model = MultinomialNB()
        self.nb_model.fit(self.nb_X, self.df['Disease'])

    def search(self, symptoms, age=None, gender=None, pregnancy_status=None, top_n=5):
        # Normalize and clean input symptoms
        input_symptoms = [str(s).strip().lower() for s in symptoms if s]
        input_text = ' '.join(input_symptoms)
        input_vector = self.vectorizer.transform([input_text])

        similarities = cosine_similarity(input_vector, self.symptom_matrix).flatten()

        results = []
        seen_diseases = set()  # To track diseases we've already added
        
        for i, sim in enumerate(similarities):
            if sim > 0.01:
                disease_row = self.df.iloc[i]
                disease_name = disease_row['Disease']
                
                # Skip if we've already added this disease
                if disease_name in seen_diseases:
                    continue
                    
                seen_diseases.add(disease_name)

                # Gender filtering: Skip if gender doesn't match
                disease_gender = str(disease_row['Gender']).lower()
                if gender and disease_gender != 'all':
                    input_gender = gender.lower()
                    if input_gender == 'male' and ('f' in disease_gender or 'female' in disease_gender):
                        continue  # Skip female-specific diseases for males
                    if input_gender == 'female' and ('m' in disease_gender or 'male' in disease_gender) and not ('f' in disease_gender or 'female' in disease_gender or 'all' in disease_gender):
                        continue  # Skip male-specific diseases for females

                age_match = self._check_age_match(disease_row['AgeGroup'], age)
                gender_match = self._check_gender_match(disease_row['Gender'], gender)
                pregnancy_safe = self._check_pregnancy_safety(
                    disease_row['PregnancySafety'], gender, pregnancy_status
                )

                # Calculate exact symptom matches
                disease_symptoms = set(str(disease_row['Symptoms']).lower().split(', '))
                exact_matches = len(disease_symptoms & set(input_symptoms))
                total_symptoms = len(input_symptoms)

                adjusted_sim = min(1.0, max(0.0, float(sim)))
                if exact_matches > 0:
                    adjusted_sim = min(1.0, adjusted_sim + (exact_matches/total_symptoms * 0.3))
                if age_match:
                    adjusted_sim = min(1.0, adjusted_sim + 0.05)
                if gender_match:
                    adjusted_sim = min(1.0, adjusted_sim + 0.03)
                if gender == 'female' and pregnancy_status and not pregnancy_safe:
                    adjusted_sim = max(0, adjusted_sim - 0.1)

                result = {
                    'name': disease_name,
                    'category': disease_row['Category'],
                    'symptoms': list(disease_symptoms),
                    'first_line_meds': disease_row['FirstLineMeds'],
                    'real_world_protocol': disease_row['Protocol'],
                    'gender': disease_row['Gender'],
                    'age_group': disease_row['AgeGroup'],
                    'pregnancy_safety': str(disease_row['PregnancySafety']),
                    'cost_tier': disease_row['CostTier'],
                    'comorbidities': disease_row.get('Comorbidities', 'None listed').split(', ') if pd.notna(disease_row.get('Comorbidities')) else ['None listed'],
                    'precautions': disease_row.get('Precautions', 'N/A'),
                    'diet': disease_row.get('Diet', 'N/A'),
                    'workout': disease_row.get('Workout', 'N/A'),
                    'match_score': adjusted_sim
                }
                results.append(result)

        return sorted(results, key=lambda x: x['match_score'], reverse=True)[:top_n]

    def predict_with_naive_bayes(self, symptoms, top_n=3):
        input_text = ' '.join(symptoms).lower()
        input_vector = self.nb_vectorizer.transform([input_text])
        probs = self.nb_model.predict_proba(input_vector)[0]
        top_indices = probs.argsort()[::-1][:top_n]
        classes = self.nb_model.classes_
        return [(classes[i], probs[i]) for i in top_indices]

    def _check_age_match(self, age_group, age):
        if not age or pd.isna(age_group):
            return False
        age = int(age)
        age_group = str(age_group).lower()

        if 'all' in age_group or '0-120' in age_group:
            return True
        if 'neonatal' in age_group and age <= 1:
            return True
        if 'pediatric' in age_group and 1 < age <= 12:
            return True
        if 'teens' in age_group and 13 <= age <= 19:
            return True
        if 'adult' in age_group and 20 <= age <= 64:
            return True
        if 'elderly' in age_group and age >= 65:
            return True
        return False

    def _check_gender_match(self, disease_gender, gender):
        if not gender or pd.isna(disease_gender):
            return False
        gender = gender.lower()
        disease_gender = str(disease_gender).lower()
        return gender in disease_gender or 'all' in disease_gender

    def _check_pregnancy_safety(self, safety, gender, pregnancy_status):
        if gender != 'female' or not pregnancy_status or pd.isna(safety):
            return True
        safety = str(safety).upper()
        if pregnancy_status == 'pregnant' and 'D' in safety:
            return False
        if pregnancy_status == 'planning' and 'X' in safety:
            return False
        return True

def load_data():
    df = pd.read_csv('augmented_diseases_extended.csv', encoding='utf-8')

    symptom_columns = ['Symptom1', 'Symptom2', 'Symptom3', 'Symptom4']
    df['Symptoms'] = df[symptom_columns].apply(
        lambda row: ', '.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    protocol_columns = ['ProtocolStep1', 'ProtocolStep2', 'ProtocolStep3']
    df['Protocol'] = df[protocol_columns].apply(
        lambda row: '\n'.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    comorbidity_columns = ['Comorbidity1', 'Comorbidity2']
    df['Comorbidities'] = df[comorbidity_columns].apply(
        lambda row: ', '.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    precaution_columns = ['Precaution1', 'Precaution2']
    df['Precautions'] = df[precaution_columns].apply(
        lambda row: ', '.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    diet_columns = ['DietRecommendation1', 'DietRecommendation2']
    df['Diet'] = df[diet_columns].apply(
        lambda row: ', '.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    workout_columns = ['WorkoutRecommendation1', 'WorkoutRecommendation2']
    df['Workout'] = df[workout_columns].apply(
        lambda row: ', '.join(str(x).strip() for x in row if pd.notna(x)), axis=1)

    df['Comorbidities'] = df['Comorbidities'].fillna('None listed')
    df['Precautions'] = df['Precautions'].fillna('N/A')
    df['Diet'] = df['Diet'].fillna('N/A')
    df['Workout'] = df['Workout'].fillna('N/A')

    return df[df['Symptoms'] != '']

enhanced_search = EnhancedDiseaseSearch(load_data())