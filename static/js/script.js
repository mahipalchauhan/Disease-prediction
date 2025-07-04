document.addEventListener('DOMContentLoaded', function() {
    // Add active class to current page in navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav ul li a');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPath || (currentPath.includes(linkPath) && linkPath !== '/')) {
            link.classList.add('active');
        }
    });

    // Image fallback handling
    const fallbackImages = document.querySelectorAll('.fallback-image');
    const defaultImageUrl = "{{ url_for('static', filename='images/default.png') }}"; 
    fallbackImages.forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/images/default.png';
        });
    });

    // Chatbot functionality
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotClose = document.querySelector('.chatbot-close');
    const chatbotSend = document.querySelector('.chatbot-send');
    const chatbotText = document.querySelector('.chatbot-text');
    const chatbotMessages = document.querySelector('.chatbot-messages');
    
    const responses = {
        "hello": "Hello! I'm WellnessWise Assistant. How can I help you with medical information today?",
        "hi": "Hi there! I can help you find disease information, use our symptom checker, or explain treatment protocols.",
        "help": "I can assist with:<br>- Finding disease information<br>- Using the symptom checker<br>- Understanding treatment protocols<br>- Navigating the website<br>What do you need help with?",
        "features": "Our medical features include:<br>- Comprehensive disease database<br>- Symptom checker with demographic filters<br>- Detailed treatment protocols<br>- Medication safety information<br>- Comorbidity considerations",
        "symptoms": `To use our symptom checker:<br>1. Go to <a href="${window.location.origin}/symptom_search">Symptom Checker</a><br>2. Select your symptoms<br>3. Provide demographic info<br>4. Get personalized results`,
        "search": "Search for diseases by:<br>- Name (e.g., 'Diabetes')<br>- Symptom (e.g., 'headache')<br>- Category (e.g., 'Cardiology')",
        "categories": "Our medical categories include:<br>- Cardiology<br>- Neurology<br>- Endocrinology<br>- Gastroenterology<br>- Pulmonology<br>Browse them on our homepage.",
        "contact": "For medical inquiries:<br>Email: info@wellnesswise.com<br>Phone: (123) 456-7890<br>Hours: Mon-Fri 9AM-5PM",
        "about": "WellnessWISE provides evidence-based medical information for healthcare professionals and patients, with data from trusted clinical sources.",
        "treatment": "Each disease page includes:<br>- First-line medications<br>- Alternative treatments<br>- Lifestyle recommendations<br>- Comorbidity considerations",
        "emergency": "For medical emergencies, please call your local emergency number immediately. This service is for informational purposes only.",
        "medication": "Medication information includes:<br>- First-line treatments<br>- Pregnancy safety<br>- Cost tiers<br>- Accessibility<br>Find these on disease pages.",
        "protocol": "Treatment protocols are based on:<br>- Clinical guidelines<br>- Real-world effectiveness<br>- Patient demographics<br>Access them via disease pages.",
        "default": "I'm a WellnessWise assistant. Try asking about:<br>- Specific diseases<br>- Symptom checking<br>- Treatment options<br>- Website features"
    };

    if (chatbotToggle && chatbotContainer) {
        chatbotToggle.addEventListener('click', () => {
            chatbotContainer.classList.add('active');
            chatbotToggle.style.display = 'none';
            if (chatbotMessages && chatbotMessages.children.length === 0) {
                addBotMessage(responses.hello);
            }
        });

        if (chatbotClose) {
            chatbotClose.addEventListener('click', () => {
                chatbotContainer.classList.remove('active');
                chatbotToggle.style.display = 'block';
            });
        }

        if (chatbotSend && chatbotText && chatbotMessages) {
            chatbotSend.addEventListener('click', sendMessage);
            chatbotText.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        }

        function sendMessage() {
            const message = chatbotText.value.trim();
            if (message) {
                addUserMessage(message);
                chatbotText.value = '';
                setTimeout(() => respondToMessage(message.toLowerCase()), 500);
            }
        }

        function addUserMessage(text) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('chatbot-message', 'user');
            messageDiv.textContent = text;
            chatbotMessages.appendChild(messageDiv);
            scrollToBottom();
        }

        function addBotMessage(text) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('chatbot-message', 'bot');
            messageDiv.innerHTML = text;
            chatbotMessages.appendChild(messageDiv);
            scrollToBottom();
        }

        function scrollToBottom() {
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        }

        function respondToMessage(message) {
            let response = responses.default;
            if (/hello|hi|hey/.test(message)) response = responses.hello;
            else if (/help|support|assist/.test(message)) response = responses.help;
            else if (/feature|function|tool/.test(message)) response = responses.features;
            else if (/symptom|sign|indication/.test(message)) response = responses.symptoms;
            else if (/search|find|look up/.test(message)) response = responses.search;
            else if (/category|specialty|department/.test(message)) response = responses.categories;
            else if (/contact|reach|email|phone/.test(message)) response = responses.contact;
            else if (/about|mission|purpose/.test(message)) response = responses.about;
            else if (/treatment|therapy|medication|drug/.test(message)) response = responses.treatment;
            else if (/emergency|urgent|911/.test(message)) response = responses.emergency;
            else if (/protocol|guideline|procedure/.test(message)) response = responses.protocol;
            addBotMessage(response);
        }
    }

    // Symptom select enhancements (only for pages with symptom selects)
    const symptomSelects = document.querySelectorAll('.symptom-select');
    if (symptomSelects.length > 0) {
        symptomSelects.forEach((select) => {
            select.addEventListener('focus', function() {
                this.size = 5;
                this.style.width = '100%';
            });
            
            select.addEventListener('blur', function() {
                this.size = 1;
                this.style.width = '';
            });
            
            select.addEventListener('keyup', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                Array.from(this.options).forEach(option => {
                    const optionText = option.text.toLowerCase();
                    option.style.display = optionText.includes(searchTerm) ? '' : 'none';
                });
            });
        });
    }

    // Symptom form handling (only for symptom_search.html)
    const symptomForm = document.getElementById('symptomForm');
    if (symptomForm) {
        const genderSelect = document.getElementById('gender');
        const pregnancyField = document.querySelector('.pregnancy-toggle');
        const resetButton = document.getElementById('resetButton');

        if (genderSelect && pregnancyField) {
            genderSelect.addEventListener('change', function() {
                pregnancyField.classList.toggle('hidden', this.value !== 'female');
            });
            // Set initial state
            pregnancyField.classList.toggle('hidden', genderSelect.value !== 'female');
        }

        if (resetButton) {
            resetButton.addEventListener('click', function(e) {
                e.preventDefault();
                symptomForm.reset();
                if (pregnancyField) pregnancyField.classList.add('hidden');
            });
        }
    }
});
document.addEventListener('DOMContentLoaded', function() {
    // Generate Receipt Button
    const generateReceiptBtn = document.getElementById('generate-receipt');
    const receiptModal = document.getElementById('receipt-modal');
    const closeModal = document.querySelector('.close-modal');
    const printBtn = document.getElementById('print-receipt');
    const downloadBtn = document.getElementById('download-receipt');

    // Set current date
    const now = new Date();
    document.getElementById('report-date').textContent = now.toLocaleDateString() + ' ' + now.toLocaleTimeString();

    // Open modal
    generateReceiptBtn.addEventListener('click', function() {
        receiptModal.style.display = 'block';
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        receiptModal.style.display = 'none';
    });

    // Close when clicking outside modal
    window.addEventListener('click', function(event) {
        if (event.target === receiptModal) {
            receiptModal.style.display = 'none';
        }
    });

    // Print functionality
    printBtn.addEventListener('click', function() {
        window.print();
    });

    // Download as PDF (using html2canvas)
    downloadBtn.addEventListener('click', function() {
        const receiptContent = document.getElementById('receipt-content');
        
        html2canvas(receiptContent).then(canvas => {
            const link = document.createElement('a');
            link.download = 'WellnessWise-Report-' + new Date().toISOString().slice(0, 10) + '.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        });
    });
});
