import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class NLPProcessor:
    """Natural Language Processing for financial chatbot"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.financial_keywords = {
            'budget': ['budget', 'spending', 'limit', 'allocation'],
            'savings': ['save', 'savings', 'goal', 'target', 'accumulate'],
            'spending': ['spent', 'expense', 'cost', 'purchase', 'buy'],
            'income': ['income', 'salary', 'earnings', 'revenue'],
            'report': ['report', 'summary', 'overview', 'analysis'],
            'category': ['category', 'type', 'classification'],
            'time': ['month', 'week', 'year', 'daily', 'weekly', 'monthly']
        }
    
    def process_query(self, user_input):
        """Process user input and extract intent and entities"""
        
        # Preprocess text
        cleaned_text = self._preprocess_text(user_input)
        
        # Extract intent
        intent = self._extract_intent(cleaned_text)
        
        # Extract entities
        entities = self._extract_entities(cleaned_text)
        
        return {
            'original_query': user_input,
            'cleaned_text': cleaned_text,
            'intent': intent,
            'entities': entities,
            'confidence': self._calculate_confidence(intent, entities)
        }
    
    def _preprocess_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        
        return ' '.join(tokens)
    
    def _extract_intent(self, text):
        """Extract user intent from text"""
        intents = {
            'get_spending_summary': any(word in text for word in ['spent', 'spending', 'expense']),
            'get_budget_status': any(word in text for word in ['budget', 'limit']),
            'get_savings_advice': any(word in text for word in ['save', 'savings', 'goal']),
            'get_income_report': any(word in text for word in ['income', 'salary', 'earn']),
            'get_financial_report': any(word in text for word in ['report', 'summary', 'overview']),
            'categorize_spending': any(word in text for word in ['category', 'type', 'classification'])
        }
        
        # Return the first matching intent
        for intent, matches in intents.items():
            if matches:
                return intent
        
        return 'general_query'
    
    def _extract_entities(self, text):
        """Extract entities like time periods, categories, amounts"""
        entities = {}
        
        # Extract time period
        time_patterns = {
            'month': r'\b(month|monthly)\b',
            'week': r'\b(week|weekly)\b',
            'year': r'\b(year|yearly|annual)\b',
            'today': r'\b(today)\b',
            'yesterday': r'\b(yesterday)\b'
        }
        
        for period, pattern in time_patterns.items():
            if re.search(pattern, text):
                entities['time_period'] = period
                break
        
        # Extract amounts (simplified)
        amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', text)
        if amount_match:
            entities['amount'] = float(amount_match.group(1))
        
        # Extract categories
        for category, keywords in self.financial_keywords.items():
            if any(keyword in text for keyword in keywords):
                entities['category'] = category
                break
        
        return entities
    
    def _calculate_confidence(self, intent, entities):
        """Calculate confidence score for the extracted intent"""
        base_confidence = 0.5
        
        # Increase confidence if we have relevant entities
        if entities:
            base_confidence += 0.3
        
        # Specific intent confidence boost
        if intent != 'general_query':
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)