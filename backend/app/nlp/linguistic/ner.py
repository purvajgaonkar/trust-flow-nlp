"""
Named Entity Recognition (NER) module.
Extracts standard entities (PERSON, ORG, GPE, DATE, etc.) and
custom security entities (SYSTEM_PROMPT, API_KEY, PASSWORD, CREDENTIAL, DATABASE, SECRET, PERSONAL_DATA, CODE, COMMAND, INJECTION, URL, IP_ADDRESS, FILE_PATH).
"""

import re
from typing import List, Dict, Any, Optional

SECURITY_PATTERNS = [
    ("API_KEY", re.compile(r"\b[A-Za-z0-9_\-]{24,}\b")),
    ("PASSWORD", re.compile(r"\b(password\s*[:=]\s*\S+|passwd\s*[:=]\s*\S+)", re.IGNORECASE)),
    ("CREDENTIAL", re.compile(r"\b(bearer\s+[A-Za-z0-9\-\._~\+\/]+=*|access_token|api_secret)\b", re.IGNORECASE)),
    ("SYSTEM_PROMPT", re.compile(r"\b(system\s+prompt|developer\s+mode|instructions\s+above)\b", re.IGNORECASE)),
    ("INJECTION", re.compile(r"\b(ignore\s+(all\s+)?(previous|prior)\s+instructions|disregard\s+all)\b", re.IGNORECASE)),
    ("COMMAND", re.compile(r"\b(sudo\s+|rm\s+-rf|chmod\s+\d+|cat\s+/etc/passwd|powershell\s+-enc|cmd\.exe)\b", re.IGNORECASE)),
    ("URL", re.compile(r"https?://[^\s<>\"']+")),
    ("IP_ADDRESS", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("FILE_PATH", re.compile(r"(/[a-zA-Z0-9_\-\.]+)+|[A-Za-z]:\\[a-zA-Z0-9_\-\\ ]+")),
    ("DATABASE", re.compile(r"\b(select\s+.*\s+from|insert\s+into|drop\s+table|information_schema)\b", re.IGNORECASE)),
    ("SECRET", re.compile(r"\b(private_key|id_rsa|BEGIN\s+RSA\s+PRIVATE\s+KEY)\b", re.IGNORECASE)),
    ("PERSONAL_DATA", re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")),
    ("CODE", re.compile(r"```[\s\S]*?```|\b(function|def|eval\(|exec\()")),
]

ENTITY_DESCRIPTIONS = {
    "PERSON": "Named person",
    "ORG": "Organization or enterprise",
    "GPE": "Geopolitical entity (country, city, state)",
    "DATE": "Absolute or relative date or period",
    "MONEY": "Monetary value including currency unit",
    "PRODUCT": "Object, vehicle, type of food, or software",
    "API_KEY": "Authentication key or high-entropy token",
    "SYSTEM_PROMPT": "Reference to system prompt or LLM instructions",
    "PASSWORD": "User password or plaintext credentials",
    "CREDENTIAL": "API token, OAuth bearer, or session secret",
    "DATABASE": "SQL queries or database manipulation statements",
    "SECRET": "Cryptographic key or private identifier",
    "PERSONAL_DATA": "PII including SSN, email, or identity records",
    "CODE": "Source code block or executable snippet",
    "COMMAND": "System shell command or privileged action",
    "INJECTION": "Prompt injection phrase or bypass payload",
    "URL": "Web address or protocol hyperlink",
    "IP_ADDRESS": "IPv4 address reference",
    "FILE_PATH": "Operating system file path",
}

def extract_entities(text: str, spacy_doc=None) -> List[Dict[str, Any]]:
    """
    Extract standard and security entities.
    """
    entities = []
    seen_spans = set()

    # 1. Custom Security Entities (Regex)
    for label, pattern in SECURITY_PATTERNS:
        for match in pattern.finditer(text):
            span = (match.start(), match.end())
            if span not in seen_spans:
                seen_spans.add(span)
                matched_text = match.group(0)
                entities.append({
                    "text": matched_text,
                    "label": label,
                    "start": match.start(),
                    "end": match.end(),
                    "category": "security",
                    "description": ENTITY_DESCRIPTIONS.get(label, label),
                })

    # 2. Standard Linguistic Entities (spaCy)
    if spacy_doc is not None:
        for ent in spacy_doc.ents:
            span = (ent.start_char, ent.end_char)
            # Avoid duplicate overlapping security entities
            if not any(s <= ent.start_char and ent.end_char <= e for (s, e) in seen_spans):
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "category": "linguistic",
                    "description": ENTITY_DESCRIPTIONS.get(ent.label_, ent.label_),
                })

    entities.sort(key=lambda x: x["start"])
    return entities
