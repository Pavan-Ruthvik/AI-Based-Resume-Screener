import pandas as pd
import numpy as np # <-- FIXED: Added missing import
import re
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_recall_fscore_support
import joblib

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    return ' '.join(text.split())

def train():
    print("Loading data...")
    df = pd.read_csv('data/UpdatedResumeDataset.csv')
    df['cleaned_resume'] = df['Resume'].apply(clean_text)

    le = LabelEncoder()
    y = le.fit_transform(df['Category'])
    
    X_train, X_test, y_train, y_test = train_test_split(df['cleaned_resume'], y, test_size=0.2, random_state=42, stratify=y)
    
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training SVM...")
    model = SVC(kernel='linear', probability=True, random_state=42)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/svm_model.pkl')
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
    joblib.dump(le, 'models/label_encoder.pkl')

    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average=None)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    feature_names = vectorizer.get_feature_names_out()
    
    # <-- FIXED: Safely extracting weights from sparse matrix
    if hasattr(model, 'coef_'):
        # Convert the sparse matrix row to a flat, dense numpy array before taking absolute values
        importances = np.abs(model.coef_[0].toarray().flatten()) 
    elif hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_ 
    else:
        importances = np.zeros(len(feature_names))
        
    # Get top 10
    top_indices = importances.argsort()[-10:][::-1]
    top_keywords = [feature_names[i] for i in top_indices]
    top_weights = importances[top_indices].tolist()
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'total_resumes_trained': len(X_train), 
        'test_size': len(X_test),
        'categories': le.classes_.tolist(), # <-- FIXED: Uses LabelEncoder to get real text names
        'f1': f1.tolist(),
        'precision': precision.tolist(),       
        'recall': recall.tolist(),             
        'confusion_matrix': cm,                
        'top_keywords': top_keywords,  
        'top_weights': top_weights     
    }
    
    with open('models/model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
    print("Training complete. Models and metrics saved.")

if __name__ == '__main__':
    train()