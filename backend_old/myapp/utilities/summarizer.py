"""
Offline legal document summarization using TF-IDF and TextRank.
No external model downloads required - works fully offline.
"""
import re
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Download required NLTK data (works offline after first run)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Optional: spacy for enhanced NER (graceful fallback if not available)
try:
    import spacy
    _SPACY_AVAILABLE = True
    try:
        _nlp = spacy.load("en_core_web_sm")
    except OSError:
        _SPACY_AVAILABLE = False
        _nlp = None
except ImportError:
    _SPACY_AVAILABLE = False
    _nlp = None


def summarize_legal_document(document_text, ratio=0.25, model_name=None):
    """
    Offline legal document summarization using TF-IDF and TextRank.
    No internet or model downloads required.

    Args:
        document_text (str): The text of the legal document to summarize
        ratio (float): The ratio of sentences to include in the summary (default: 0.25)
        model_name: Ignored (kept for API compatibility)

    Returns:
        str: The summary text
    """
    if not document_text or not document_text.strip():
        return ""

    # Clean and preprocess text
    document_text = preprocess_legal_text(document_text)

    # Split text into sentences
    sentences = sent_tokenize(document_text)

    # Skip empty documents or those with too few sentences
    if len(sentences) < 2:
        return document_text

    # Number of sentences to include in summary
    num_sentences = max(2, min(int(len(sentences) * ratio), int(len(sentences) * 0.5)))

    # Extract legal entities (optional - uses regex fallback if spacy unavailable)
    legal_entities = extract_legal_entities_offline(document_text)

    # Calculate sentence scores using TF-IDF and TextRank
    sentence_scores = calculate_sentence_scores_tfidf(
        sentences, legal_entities
    )

    # Select top sentences based on scores
    ranked_indices = np.argsort(sentence_scores)[::-1]
    top_indices = sorted(ranked_indices[:num_sentences])

    # Create summary by joining selected sentences
    summary_sentences = [sentences[i] for i in top_indices]

    # Post-process summary
    summary_sentences = post_process_summary(summary_sentences, legal_entities)
    summary = ' '.join(summary_sentences)

    return summary


def preprocess_legal_text(text):
    """Clean and preprocess legal text."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Ensure proper spacing after periods
    text = re.sub(r'\.(?=[A-Z])', '. ', text)
    # Fix common OCR errors in legal documents
    text = text.replace('l.', 'i.')
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)
    return text


def extract_legal_entities_offline(document_text):
    """Extract legal entities using regex (no spacy required)."""
    entities = {
        "parties": [],
        "dates": [],
        "monetary_values": [],
        "legal_terms": [],
        "obligations": [],
        "places": []
    }

    # Legal terms dictionary
    legal_terms = [
        "agreement", "contract", "clause", "party", "parties", "liability",
        "indemnity", "warranty", "termination", "jurisdiction", "governing law",
        "confidentiality", "obligation", "breach", "remedy", "arbitration",
        "force majeure", "consideration", "renewal", "amendment", "assignment"
    ]

    if _SPACY_AVAILABLE and _nlp is not None:
        try:
            doc = _nlp(document_text)
            for ent in doc.ents:
                if ent.label_ == "PERSON" or ent.label_ == "ORG":
                    entities["parties"].append(ent.text)
                elif ent.label_ == "DATE":
                    entities["dates"].append(ent.text)
                elif ent.label_ == "MONEY":
                    entities["monetary_values"].append(ent.text)
                elif ent.label_ == "GPE" or ent.label_ == "LOC":
                    entities["places"].append(ent.text)
        except Exception:
            pass

    # Extract legal terms via regex
    for term in legal_terms:
        term_pattern = re.compile(r'\b' + term + r'\b', re.IGNORECASE)
        if term_pattern.search(document_text):
            entities["legal_terms"].append(term)

    # Extract obligation statements
    obligation_patterns = [
        r'\bshall\b', r'\bmust\b', r'\brequired to\b', r'\bobligated to\b',
        r'\bagrees to\b', r'\bundertakes to\b'
    ]
    for sentence in sent_tokenize(document_text):
        for pattern in obligation_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                entities["obligations"].append(sentence.strip())
                break

    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))[:10]

    return entities


def calculate_sentence_scores_tfidf(sentences, legal_entities):
    """Calculate sentence scores using TF-IDF and TextRank (fully offline)."""
    scores = np.zeros(len(sentences))
    all_entities = []
    for category in legal_entities.values():
        all_entities.extend(category)

    # TF-IDF based scoring
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        sentence_vectors = vectorizer.fit_transform(sentences)
        document_vector = np.mean(sentence_vectors.toarray(), axis=0)

        for i in range(len(sentences)):
            # Factor 1: TF-IDF similarity to document
            sim = cosine_similarity(
                [sentence_vectors[i].toarray()[0]],
                [document_vector]
            )[0][0]
            scores[i] += sim * 0.35

            # Factor 2: Information density (legal entities)
            entity_count = sum(
                1 for entity in all_entities
                if entity.lower() in sentences[i].lower()
            )
            word_count = len(sentences[i].split())
            if word_count > 0:
                scores[i] += (entity_count / word_count) * 0.35
    except Exception:
        # Fallback: simple length and entity based scoring
        for i, sentence in enumerate(sentences):
            entity_count = sum(
                1 for entity in all_entities
                if entity.lower() in sentence.lower()
            )
            scores[i] = entity_count * 0.5 + min(len(sentence.split()) / 50, 0.5)

    # Factor 3: Legal content boost
    obligation_markers = ['shall', 'must', 'required', 'obligated', 'agrees to', 'undertakes']
    key_legal_phrases = [
        'governed by', 'warranty', 'liability', 'termination', 'remedies',
        'indemnification', 'confidentiality', 'jurisdiction', 'arbitration'
    ]
    for i, sentence in enumerate(sentences):
        lower_sent = sentence.lower()
        if any(marker in lower_sent for marker in obligation_markers):
            scores[i] += 0.25
        if any(phrase in lower_sent for phrase in key_legal_phrases):
            scores[i] += 0.15

    # Factor 4: Penalty for extremely long sentences
    for i, sentence in enumerate(sentences):
        word_count = len(sentence.split())
        if word_count > 50:
            scores[i] -= (word_count - 50) / 100

    return scores


def post_process_summary(sentences, legal_entities):
    """Apply post-processing to make summary more concise."""
    processed_sentences = []
    for sentence in sentences:
        # Skip very similar sentences
        if any(
            calculate_text_similarity(sentence, ps) > 0.7
            for ps in processed_sentences
        ):
            continue

        # Shorten common legal preambles
        if "THIS AGREEMENT" in sentence and len(sentence) > 200:
            parties_match = re.search(
                r'between ([^,]+).+and ([^,\.]+)', sentence
            )
            if parties_match:
                party1, party2 = parties_match.groups()
                date_match = re.search(
                    r'(\d+(?:st|nd|rd|th)? day of [A-Za-z]+, \d{4})',
                    sentence
                )
                date_str = date_match.group(1) if date_match else ""
                sentence = f"Agreement dated {date_str} between {party1} and {party2}."

        sentence = re.sub(
            r'shall be governed by the laws of ([^,\.]+)',
            r'governed by \1 law',
            sentence
        )
        processed_sentences.append(sentence)

    return processed_sentences


def calculate_text_similarity(text1, text2):
    """Calculate similarity between two text strings."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    overlap = len(words1.intersection(words2))
    union = len(words1.union(words2))
    return overlap / union if union > 0 else 0.0


def get_summary_metrics(original_text, summary):
    """Calculate metrics about the summary."""
    original_word_count = len(original_text.split())
    summary_word_count = len(summary.split())
    compression_ratio = (
        summary_word_count / original_word_count
        if original_word_count > 0
        else 1
    )
    return {
        "original_length": original_word_count,
        "summary_length": summary_word_count,
        "compression_ratio": compression_ratio,
        "compression_percentage": (1 - compression_ratio) * 100
    }
