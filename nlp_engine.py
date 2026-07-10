

 
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
from database import get_connection
 
# Minimum similarity score (0-1) required to trust an FAQ match
SIMILARITY_THRESHOLD = 0.30
 
FALLBACK_RESPONSE = (
    "I'm sorry, I don't have an answer for that yet. "
    "Please contact the college support office, or try rephrasing your question. "
    "You can ask me about admissions, fees, exams, results, library, hostel, "
    "placements, scholarships, or leave applications."
)
 
 
def clean_text(text: str) -> str:
    """Lowercase and strip punctuation for better matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
 
 
def get_all_faqs():
    conn = get_connection()
    rows = conn.execute("SELECT FAQ_ID, Category, Question, Answer FROM FAQ").fetchall()
    conn.close()
    return rows
 
 
def get_response(user_query: str):
    """
    Core NLP matching function.
    Returns: (answer_text, matched_faq_id_or_None, matched_category_or_None, confidence)
    """
    faqs = get_all_faqs()
 
    if not faqs:
        return FALLBACK_RESPONSE, None, None, 0.0
 
    questions = [clean_text(row["Question"]) for row in faqs]
    cleaned_query = clean_text(user_query)
 
    # Build TF-IDF matrix over FAQ questions + the incoming query
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform(questions + [cleaned_query])
    except ValueError:
        # Happens if query is empty after cleaning
        return FALLBACK_RESPONSE, None, None, 0.0
 
    query_vector = tfidf_matrix[-1]
    faq_vectors = tfidf_matrix[:-1]
 
    similarities = cosine_similarity(query_vector, faq_vectors).flatten()
    best_index = similarities.argmax()
    best_score = float(similarities[best_index])
 
    if best_score >= SIMILARITY_THRESHOLD:
        best_faq = faqs[best_index]
        return best_faq["Answer"], best_faq["FAQ_ID"], best_faq["Category"], best_score
 
    return FALLBACK_RESPONSE, None, None, best_score
 
 
def get_llm_fallback_response(user_query: str, api_key: str = None):
    """
    Optional: Large Language Model fallback (as mentioned in the report's
    'AI/NLP: OpenAI API or Hugging Face Transformers' section).
 
    This is intentionally left as a plug-in point. If you have an OpenAI
    API key, you can wire it up here, e.g.:
 
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful student support assistant."},
                {"role": "user", "content": user_query},
            ],
        )
        return completion.choices[0].message.content
 
    Left disabled by default so the project runs fully offline.
    """
    return FALLBACK_RESPONSE
