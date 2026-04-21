import os
import logging
import re
import nltk
from nltk.tokenize import sent_tokenize

# Optional: for LegalBertSimplifier (only imported when class is instantiated)
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForPreTraining, pipeline
    _BERT_AVAILABLE = True
except ImportError:
    _BERT_AVAILABLE = False

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legal_bert_simplifier")


def _offline_summarize(text, level):
    """Offline fallback using extractive summarization."""
    from .summarizer import summarize_legal_document
    ratio = 0.4 if level == 1 else (0.3 if level == 2 else 0.2)
    return summarize_legal_document(text, ratio=ratio)


class LegalBertSimplifier:
    def __init__(self, device=None, max_length=512):
        """
        Initialize a legal text simplifier using InLegalBERT.
        Requires torch and transformers. Use summarize_text() for offline mode.

        Args:
            device (str): Computing device ('cpu', 'cuda', or None for auto-detection)
            max_length (int): Maximum sequence length for the model
        """
        if not _BERT_AVAILABLE:
            raise ImportError(
                "LegalBertSimplifier requires torch and transformers. "
                "Use summarize_text() for offline summarization."
            )
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Using device: {self.device}")

        try:
            logger.info("Loading InLegalBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained("law-ai/InLegalBERT")
            self.model = AutoModelForPreTraining.from_pretrained("law-ai/InLegalBERT")
            self.model.to(self.device)

            # Create fill-mask pipeline for term replacement
            self.fill_mask = pipeline(
                "fill-mask",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )

            # Load simplification dictionary for legal terms
            self.legal_terms = self._load_legal_terms()

            logger.info("Model loaded successfully")

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")

        self.max_length = max_length

    def _load_legal_terms(self):
        """Load common legal terms and their simpler equivalents."""
        return {
            "hereinafter": "from now on",
            "aforementioned": "mentioned earlier",
            "pursuant to": "according to",
            "in accordance with": "following",
            "notwithstanding": "despite",
            "whereby": "by which",
            "herein": "in this document",
            "therein": "in that",
            "heretofore": "until now",
            "party of the first part": "first party",
            "party of the second part": "second party",
            "shall": "will",
            "such": "this",
            "said": "the",
            "deemed to be": "considered as",
            # Add more legal terms as needed
        }

    def simplify_text(self, text, level=2):
        """
        Simplify legal text using InLegalBERT and rule-based techniques.

        Args:
            text (str): Legal text to simplify
            level (int): Simplification level (1=mild, 2=moderate, 3=extreme)

        Returns:
            str: Simplified text
        """
        if not text:
            return ""

        # Process the text in sentences to maintain structure
        sentences = sent_tokenize(text)
        simplified_sentences = []

        for sentence in sentences:
            # Apply different simplification techniques based on level
            simplified = sentence

            # Level 1: Basic term replacement
            if level >= 1:
                simplified = self._replace_legal_terms(simplified)

            # Level 2: Add structural simplification
            if level >= 2:
                simplified = self._simplify_structure(simplified)

            # Level 3: Use model to suggest simpler alternatives for complex phrases
            if level >= 3:
                simplified = self._model_based_simplification(simplified)

            simplified_sentences.append(simplified)

        # Join the simplified sentences
        result = ' '.join(simplified_sentences)

        # Clean up spacing and punctuation
        result = self.clean_text(result)

        return result

    def _replace_legal_terms(self, text):
        """Replace common legal terms with simpler equivalents."""
        for term, replacement in self.legal_terms.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def _simplify_structure(self, text):
        """Simplify the structure of legal sentences."""
        # Remove parenthetical expressions that are longer than 20 characters
        text = re.sub(r'\([^)]{20,}\)', '', text)

        # Replace semicolons with periods
        text = text.replace(';', '.')

        # Simplify "if and only if" constructions
        text = text.replace("if and only if", "only if")

        # Break up sentences with multiple clauses connected by "whereas"
        text = text.replace("WHEREAS,", ".")
        text = text.replace("whereas,", ".")

        # Simplify "for the purpose of"
        text = text.replace("for the purpose of", "to")

        return text

    def _model_based_simplification(self, text):
        """Use InLegalBERT to identify and simplify complex terms."""
        # This is a simplified implementation using the mask filling capability
        # We'll look for complex words (>7 characters) and try to find simpler alternatives

        words = text.split()
        simplified_words = []

        for word in words:
            # Skip short words, punctuation, and already processed terms
            if len(word) <= 7 or not word.isalpha() or word.lower() in self.legal_terms:
                simplified_words.append(word)
                continue

            # Try to find a simpler alternative using the model
            try:
                # Create a masked version of the text
                masked_text = text.replace(word, self.tokenizer.mask_token, 1)

                # Get model predictions
                predictions = self.fill_mask(masked_text)

                # Filter predictions to find simpler words
                simpler_alternatives = [
                    pred['token_str'] for pred in predictions
                    if len(pred['token_str']) < len(word) and pred['score'] > 0.05
                ]

                if simpler_alternatives:
                    # Use the highest-scoring simpler alternative
                    simplified_words.append(simpler_alternatives[0])
                else:
                    simplified_words.append(word)

            except Exception:
                # If there's any issue, keep the original word
                simplified_words.append(word)

        return ' '.join(simplified_words)

    def clean_text(self, text):
        """Clean up the simplified text."""
        # Fix spacing
        text = re.sub(r'\s+', ' ', text)

        # Fix punctuation spacing
        text = re.sub(r'\s([,.;:?!])', r'\1', text)

        # Ensure proper spacing after punctuation
        text = re.sub(r'([,.;:?!])([^\s])', r'\1 \2', text)

        # Fix multiple periods
        text = re.sub(r'\.{2,}', '.', text)

        # Fix cases where we replace beginning of sentence
        text = re.sub(r'\.\s+([a-z])', lambda m: f". {m.group(1).upper()}", text)

        return text.strip()

    def batch_simplify(self, documents, level=2):
        """
        Simplify multiple documents.

        Args:
            documents (list): List of text documents to simplify
            level (int): Simplification level

        Returns:
            list: List of simplified documents
        """
        return [self.simplify_text(doc, level) for doc in documents]


# Legal term replacements for simplification (offline)
LEGAL_TERMS = {
    "hereinafter": "from now on",
    "aforementioned": "mentioned earlier",
    "pursuant to": "according to",
    "in accordance with": "following",
    "notwithstanding": "despite",
    "whereby": "by which",
    "herein": "in this document",
    "therein": "in that",
    "shall": "will",
    "such": "this",
    "said": "the",
}


def _simplify_legal_terms(text):
    """Replace legal jargon with simpler words (offline)."""
    result = text
    for term, replacement in LEGAL_TERMS.items():
        pattern = r'\b' + re.escape(term) + r'\b'
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def summarize_text(text, level=2):
    """
    Offline summarization and simplification of legal text.
    Level 1: longer summary (40% of sentences), level 2: medium (30%), level 3: shorter (20%).
    """
    if not text or not text.strip():
        return ""

    # Use offline extractive summarization
    simplified_corpus = _offline_summarize(text, level)

    # Apply legal term simplification
    simplified_corpus = _simplify_legal_terms(simplified_corpus)

    # Clean up formatting
    simplified_corpus = simplified_corpus.replace("**", "").replace("*", "").strip()

    return simplified_corpus

