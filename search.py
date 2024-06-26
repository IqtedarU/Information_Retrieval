import math
import pickle
from nltk import word_tokenize, PorterStemmer
from nltk.corpus import stopwords

def preprocess(text):
    tokens = word_tokenize(text.lower())  # Tokenization and lowercase
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]  # Remove stopwords and non-alphanumeric characters
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]  # Stemming
    return tokens


def load_index(index_file):
    with open(index_file, "rb") as f:
        inverted_index = pickle.load(f)
    return inverted_index


def calculate_query_vector(query_terms, inverted_index):
    query_vector = {}
    total_docs = len(inverted_index)  # Total number of documents

    for term in query_terms:
        if term in inverted_index:
            idf_score = math.log(total_docs / len(inverted_index[term]))
            query_vector[term] = idf_score
        else:
            query_vector[term] = 0  # Set IDF score to 0 if term not found in inverted index

    return query_vector

def search_query(query, inverted_index):
    # Preprocess the query
    preprocessed_query = preprocess(query)
    query_vector = calculate_query_vector(preprocessed_query, inverted_index)

    document_scores = {}  # Dictionary to store document scores
    document_titles = {}  # Dictionary to store document titles

    # Calculate dot product for each document
    for term, query_score in query_vector.items():
        if term in inverted_index:
            for doc_id, title, doc_score in inverted_index[term]:
                if doc_id not in document_scores:
                    document_scores[doc_id] = 0
                # Calculate dot product
                document_scores[doc_id] += query_score * doc_score
                document_titles[doc_id] = title

    # Calculate magnitudes of query vector
    query_magnitude = math.sqrt(sum(score ** 2 for score in query_vector.values()))

    # Normalize dot products by dividing by document vector lengths and query vector length
    for doc_id in document_scores:
        # Calculate magnitude of document vector
        doc_magnitude = math.sqrt(sum(score ** 2 for term_scores in inverted_index.values() for doc_id_, _, score in term_scores if doc_id_ == doc_id))
        # Calculate cosine similarity score
        document_scores[doc_id] /= (query_magnitude * doc_magnitude) if doc_magnitude != 0 else 1

    # Sort documents by cosine similarity scores
    sorted_documents = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

    return [(doc_id, document_titles[doc_id], score) for doc_id, score in sorted_documents]
