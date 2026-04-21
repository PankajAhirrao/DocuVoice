"""
IEEE Research Paper Analyzer.
Analyzes extracted sections from IEEE-style academic papers.
Replaces legal-document summarization with research-paper focused analysis.
"""
import re
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


def preprocess_ieee_text(text):
    """Clean and preprocess research paper text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\.(?=[A-Z])", ". ", text)
    return text


def _extract_research_indicators(text):
    """Extract research-relevant terms for scoring."""
    indicators = {
        "methods": ["proposed", "algorithm", "approach", "framework", "model", "method"],
        "results": ["result", "accuracy", "performance", "experiment", "evaluation", "dataset"],
        "contributions": ["contribute", "contribution", "novel", "first", "improve", "achieve"],
    }
    found = []
    lower = text.lower()
    for terms in indicators.values():
        for t in terms:
            if re.search(r"\b" + re.escape(t) + r"\b", lower):
                found.append(t)
    return found


def analyze_ieee_section(text, section_key="full_paper", max_sentences=15):
    """
    Analyze an IEEE paper section: summarize and highlight key content.

    Args:
        text: Extracted section text
        section_key: Which section is being analyzed (for context)
        max_sentences: Max sentences in summary

    Returns:
        str: Summary/analysis of the section
    """
    if not text or not text.strip():
        return "No content available for this section."

    text = preprocess_ieee_text(text)
    sentences = sent_tokenize(text)

    if len(sentences) <= 2:
        return text

    # Shorter sections (abstract, title, citations) - return as-is or lightly summarized
    if section_key in ("title", "citations", "figures_tables"):
        return text[:1500] if len(text) > 1500 else text

    # For abstract, use high ratio (most of it is important)
    if section_key == "abstract":
        ratio = 0.8
    else:
        ratio = 0.35

    num_sentences = max(2, min(int(len(sentences) * ratio), max_sentences))

    # TF-IDF + research-term scoring
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=3000)
        vectors = vectorizer.fit_transform(sentences)
        doc_vector = np.mean(vectors.toarray(), axis=0)

        scores = np.zeros(len(sentences))
        indicators = _extract_research_indicators(text)

        for i in range(len(sentences)):
            sim = cosine_similarity(
                [vectors[i].toarray()[0]],
                [doc_vector],
            )[0][0]
            scores[i] += sim * 0.4

            lower_sent = sentences[i].lower()
            for term in indicators:
                if term in lower_sent:
                    scores[i] += 0.15

            if any(
                w in lower_sent
                for w in ["proposed", "novel", "achieve", "result", "accuracy"]
            ):
                scores[i] += 0.2

        ranked = np.argsort(scores)[::-1]
        top_indices = sorted(ranked[:num_sentences])
        summary_sentences = [sentences[i] for i in top_indices]

    except Exception:
        # Fallback: take first and last sentences
        summary_sentences = (
            sentences[: num_sentences // 2]
            + sentences[-max(1, num_sentences - num_sentences // 2) :]
        )

    return " ".join(summary_sentences)
