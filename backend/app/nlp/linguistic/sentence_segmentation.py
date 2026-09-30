"""
Sentence segmentation module.
Splits text into syntactic sentences.
"""

import re
from typing import List, Dict, Any, Optional

def segment_sentences(text: str, spacy_doc=None) -> List[Dict[str, Any]]:
    """
    Split text into individual sentences with span offsets.
    """
    sentences = []
    if spacy_doc is not None:
        for sent in spacy_doc.sents:
            cleaned = sent.text.strip()
            if cleaned:
                sentences.append({
                    "text": cleaned,
                    "start": sent.start_char,
                    "end": sent.end_char,
                    "length": len(cleaned),
                })
        return sentences

    # Regex sentence splitter fallback
    pattern = re.compile(r'[^.!?]+[.!?]*', re.MULTILINE)
    for match in pattern.finditer(text):
        cleaned = match.group(0).strip()
        if cleaned:
            sentences.append({
                "text": cleaned,
                "start": match.start(),
                "end": match.end(),
                "length": len(cleaned),
            })

    if not sentences and text.strip():
        sentences.append({
            "text": text.strip(),
            "start": 0,
            "end": len(text.strip()),
            "length": len(text.strip()),
        })

    return sentences
