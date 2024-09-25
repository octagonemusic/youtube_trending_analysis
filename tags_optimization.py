import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
import numpy as np
from gensim.models import Word2Vec

# Load the data from the Excel file
file_path = 'output/trending_videos_usa.xlsx'  # Update the file path as needed
df = pd.read_excel(file_path)

# Data Cleaning Function
def clean_text(text):
    """Clean the text for analysis."""
    text = text.lower()  # Convert to lowercase
    text = ''.join(c for c in text if c.isalnum() or c.isspace())  # Remove punctuation
    return text

# Clean titles and tags
df['Cleaned Title'] = df['Title'].apply(clean_text)
df['Cleaned Tags'] = df['Tags'].apply(lambda x: clean_text(x) if isinstance(x, str) else '')

# Combine cleaned titles and tags for TF-IDF
combined_text = df['Cleaned Title'] + ' ' + df['Cleaned Tags']

# Create TF-IDF Vectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(combined_text)

# Create a DataFrame from the TF-IDF matrix
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out())

# Concatenate performance metrics (like view count) with TF-IDF
performance_metrics = df[['View Count']]  # Add any other metrics if needed
final_df = pd.concat([performance_metrics, tfidf_df], axis=1)

# Linear Regression to find relationships
X = tfidf_df
y = final_df['View Count']

# Fit the model
model = LinearRegression()
model.fit(X, y)

# Get coefficients to identify important terms
coef = pd.Series(model.coef_, index=X.columns)
top_terms = coef.sort_values(ascending=False).head(10)
print("Top Terms for View Count Optimization:\n", top_terms)

# Title Generation Function
def generate_title(base_title, keywords):
    """Generate a suggested title based on a base title and keywords."""
    if not keywords:
        return base_title  # Return the base title if there are no keywords
    # Combine the base title with keywords
    new_title = f"{base_title}: {' | '.join(keywords)}"
    return new_title

# Example usage for title generation    
base_title = "Dragon Ball Sparkling Gameplay"
suggested_title = generate_title(base_title, top_terms.index.tolist())
print("Suggested Title:", suggested_title)

# Word2Vec Model for keywords analysis
tokenized_titles = [title.split() for title in df['Cleaned Title']]
tokenized_tags = [tag.split() for tag in df['Cleaned Tags'] if isinstance(tag, str)]

# Create a Word2Vec model
w2v_model = Word2Vec(sentences=tokenized_titles + tokenized_tags, vector_size=100, window=5, min_count=1)

# Example: Get similar words for a specific keyword
similar_words = w2v_model.wv.most_similar('video', topn=10)
print("Similar Words to 'video':", similar_words)

# Saving the model (optional)
# w2v_model.save("word2vec_model.model")
