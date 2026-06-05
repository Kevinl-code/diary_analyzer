from textblob import TextBlob
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

def analyze_sentiment(text):

    polarity = TextBlob(
        str(text)
    ).sentiment.polarity

    if polarity > 0:
        return "Positive"

    elif polarity < 0:
        return "Negative"

    else:
        return "Neutral"

def generate_embeddings(texts):

    embeddings = model.encode(texts)

    return embeddings

def calculate_similarity(embeddings):

    similarity_matrix = cosine_similarity(
        embeddings
    )

    avg_similarity = similarity_matrix.mean()

    return avg_similarity

def calculate_metrics(df):

    positive_count = len(
        df[df["sentiment"] == "Positive"]
    )

    negative_count = len(
        df[df["sentiment"] == "Negative"]
    )

    neutral_count = len(
        df[df["sentiment"] == "Neutral"]
    )

    mental_energy = round(
        (positive_count / len(df)) * 100,
        2
    )

    return (
        positive_count,
        negative_count,
        neutral_count,
        mental_energy
    )