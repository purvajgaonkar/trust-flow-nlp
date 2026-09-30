"""
Main NLP Analyzer – runs full linguistic pipeline via spaCy.
"""

import time
import logging
from typing import Any, Dict, List, Optional

from app.nlp.preprocessing.language import detect_language
from app.nlp.preprocessing.normalization import normalize_text
from app.nlp.preprocessing.validation import validate_input
from app.nlp.preprocessing.tokenization import simple_tokenize, spacy_tokenize, bert_tokenize

logger = logging.getLogger(__name__)

# Custom security entities (rule-based)
SECURITY_ENTITY_PATTERNS = [
    {"label": "API_KEY", "pattern": [{"TEXT": {"REGEX": r"[A-Za-z0-9\-_]{20,}"}}]},
    {"label": "SYSTEM_PROMPT", "pattern": [{"LOWER": "system"}, {"LOWER": "prompt"}]},
    {"label": "PASSWORD", "pattern": [{"LOWER": {"IN": ["password", "passwd", "pwd"]}}]},
    {"label": "CREDENTIAL", "pattern": [{"LOWER": {"IN": ["credential", "credentials", "token", "secret"]}}]},
    {"label": "INJECTION", "pattern": [{"LOWER": "injection"}]},
    {"label": "COMMAND", "pattern": [{"TEXT": {"REGEX": r"(sudo|bash|sh|cmd|powershell|exec|eval)\b"}}]},
]

# Entity type descriptions
ENTITY_DESCRIPTIONS = {
    "PERSON": "Named person",
    "ORG": "Organization or company",
    "GPE": "Geopolitical entity (country, city)",
    "DATE": "Date or time reference",
    "MONEY": "Monetary value",
    "PRODUCT": "Product or service name",
    "API_KEY": "Possible API key or token",
    "SYSTEM_PROMPT": "Reference to system prompt",
    "PASSWORD": "Password or credential reference",
    "CREDENTIAL": "Authentication credential",
    "INJECTION": "Injection keyword",
    "COMMAND": "Shell or system command",
    "URL": "Web URL",
    "IP_ADDRESS": "IP address",
    "FILE_PATH": "File system path",
}


class NLPAnalyzer:
    """
    Full NLP analysis pipeline using spaCy + optional BERT tokenizer.
    Falls back gracefully when spaCy model is unavailable.
    """

    def __init__(self):
        self.nlp = None
        self.bert_tokenizer = None
        self._load_models()

    def _load_models(self):
        # spaCy
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            # Add custom entity ruler
            if "entity_ruler" not in self.nlp.pipe_names:
                ruler = self.nlp.add_pipe("entity_ruler", before="ner")
                ruler.add_patterns(SECURITY_ENTITY_PATTERNS)
            logger.info("spaCy model loaded: en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy model unavailable: {e}")

        # BERT tokenizer
        try:
            from transformers import AutoTokenizer
            self.bert_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            logger.info("BERT tokenizer loaded")
        except Exception as e:
            logger.warning(f"BERT tokenizer unavailable: {e}")

    def analyze(self, text: str) -> dict:
        """
        Run full NLP analysis on text.
        Returns dict compatible with NLPAnalysisResult schema.
        """
        start = time.perf_counter()

        # Validation
        is_valid, errors, warnings = validate_input(text)
        if not is_valid:
            raise ValueError(f"Invalid input: {'; '.join(errors)}")

        # Language detection
        language, lang_conf = detect_language(text)

        # Normalization (for display, keep original; for security, normalize)
        normalized = normalize_text(text)

        # Tokenizers
        simple_tokens = simple_tokenize(text)
        spacy_tokens = spacy_tokenize(text, self.nlp)
        bert_tokens = bert_tokenize(text, self.bert_tokenizer)

        # Run spaCy pipeline
        tokens = []
        entities = []
        sentences = []
        dependencies = []
        pos_distribution: Dict[str, int] = {}
        entity_distribution: Dict[str, int] = {}

        if self.nlp:
            try:
                doc = self.nlp(text[:10000])

                # Tokens
                for tok in doc:
                    tokens.append({
                        "text": tok.text,
                        "lemma": tok.lemma_,
                        "pos": tok.pos_,
                        "tag": tok.tag_,
                        "dep": tok.dep_,
                        "is_stop": tok.is_stop,
                        "is_punct": tok.is_punct,
                        "idx": tok.idx,
                    })
                    if tok.pos_ not in ("SPACE", "PUNCT"):
                        pos_distribution[tok.pos_] = pos_distribution.get(tok.pos_, 0) + 1

                # Entities
                for ent in doc.ents:
                    entities.append({
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "description": ENTITY_DESCRIPTIONS.get(ent.label_, ent.label_),
                        "confidence": 0.85,
                    })
                    entity_distribution[ent.label_] = entity_distribution.get(ent.label_, 0) + 1

                # Sentences
                for sent in doc.sents:
                    sent_tokens = []
                    for tok in sent:
                        sent_tokens.append({
                            "text": tok.text,
                            "lemma": tok.lemma_,
                            "pos": tok.pos_,
                            "tag": tok.tag_,
                            "dep": tok.dep_,
                            "is_stop": tok.is_stop,
                            "is_punct": tok.is_punct,
                            "idx": tok.idx,
                        })
                    sentences.append({
                        "text": sent.text,
                        "start": sent.start_char,
                        "end": sent.end_char,
                        "tokens": sent_tokens,
                    })

                # Dependencies
                for tok in doc:
                    if tok.dep_ != "ROOT" and tok.head != tok:
                        dependencies.append({
                            "governor": tok.head.text,
                            "dependent": tok.text,
                            "relation": tok.dep_,
                            "gov_idx": tok.head.i,
                            "dep_idx": tok.i,
                        })

            except Exception as e:
                logger.warning(f"spaCy processing failed: {e}")

        # Fall back: basic token objects from simple tokenizer
        if not tokens:
            for i, tok_text in enumerate(simple_tokens[:500]):
                tokens.append({
                    "text": tok_text,
                    "lemma": tok_text.lower(),
                    "pos": "NOUN",
                    "tag": "NN",
                    "dep": "dep",
                    "is_stop": False,
                    "is_punct": not tok_text.isalnum(),
                    "idx": i,
                })

        elapsed = (time.perf_counter() - start) * 1000

        return {
            "text": text,
            "language": language,
            "language_confidence": lang_conf,
            "tokens": tokens,
            "entities": entities,
            "sentences": sentences,
            "dependencies": dependencies,
            "tokenizer_comparison": {
                "simple_tokens": simple_tokens[:100],
                "spacy_tokens": spacy_tokens[:100],
                "bert_tokens": bert_tokens[:100],
                "simple_count": len(simple_tokens),
                "spacy_count": len(spacy_tokens),
                "bert_count": len(bert_tokens),
            },
            "pos_distribution": pos_distribution,
            "entity_distribution": entity_distribution,
            "processing_time_ms": round(elapsed, 2),
        }


# Singleton
nlp_analyzer = NLPAnalyzer()
