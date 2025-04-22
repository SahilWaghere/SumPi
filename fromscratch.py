import numpy as np
import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

# Download required NLTK resources (only needed for first-time execution)
nltk.download('punkt')

def clean_text(text):
    """Cleans text by removing special characters and converting to lowercase."""
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove punctuation and numbers
    return text.lower()

def get_word_frequencies(text):
    """Computes word frequency distribution."""
    words = word_tokenize(text)
    word_frequencies = Counter(words)
    return word_frequencies

def score_sentences(text, word_frequencies):
    """Scores sentences based on word frequency importance."""
    sentences = sent_tokenize(text)
    sentence_scores = {}

    for sentence in sentences:
        words = word_tokenize(sentence)
        score = sum(word_frequencies.get(word, 0) for word in words)  # Sum of word scores
        sentence_scores[sentence] = score / len(words)  # Normalize by sentence length

    return sentence_scores
def build_similarity_matrix(sentences):
    """Creates a sentence similarity matrix using word overlap."""
    vectorized_sentences = [set(word_tokenize(sentence)) for sentence in sentences]
    sim_matrix = np.zeros((len(sentences), len(sentences)))

    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                common_words = vectorized_sentences[i].intersection(vectorized_sentences[j])
                sim_matrix[i][j] = len(common_words) / (len(vectorized_sentences[i]) + len(vectorized_sentences[j]))

    return sim_matrix

def summarize_text(text, num_sentences=3):
    """Summarizes text using word frequency and TextRank algorithm."""
    # Clean and tokenize text
    cleaned_text = clean_text(text)
    sentences = sent_tokenize(text)

    # Compute word frequencies
    word_frequencies = get_word_frequencies(cleaned_text)

    # Score sentences based on word importance
    sentence_scores = score_sentences(text, word_frequencies)

    # Rank sentences using TextRank (Graph-Based Algorithm)
    sim_matrix = build_similarity_matrix(sentences)
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(nx_graph)

    # Combine both scores: Frequency Score + TextRank Score
    combined_scores = {sent: sentence_scores.get(sent, 0) + scores.get(i, 0) for i, sent in enumerate(sentences)}

    # Select top N sentences as summary
    ranked_sentences = sorted(combined_scores, key=combined_scores.get, reverse=True)
    summary = " ".join(ranked_sentences[:num_sentences])

    return summary

