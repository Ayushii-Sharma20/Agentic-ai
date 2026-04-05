# backend/app/utils/text_processor.py
import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize raw text from web pages or PDFs.
    - Remove HTML tags
    - Normalize unicode
    - Collapse whitespace
    - Remove non-printable characters
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)

    # Normalize unicode (e.g. smart quotes → ASCII)
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', ' ', text)

    # Collapse multiple newlines/spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using a rule-based approach.
    Handles common abbreviations to avoid false splits.
    """
    # Protect common abbreviations
    abbreviations = ['Mr.', 'Mrs.', 'Dr.', 'Prof.', 'Inc.', 'Ltd.', 'Corp.', 'vs.', 'etc.', 'e.g.', 'i.e.']
    protected = text
    for abbr in abbreviations:
        placeholder = abbr.replace('.', '<DOT>')
        protected = protected.replace(abbr, placeholder)

    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', protected)

    # Restore abbreviations
    sentences = [s.replace('<DOT>', '.') for s in sentences]

    # Filter very short or empty
    return [s.strip() for s in sentences if len(s.strip()) > 15]


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks by character count,
    preferring to break at sentence boundaries.
    """
    sentences = split_into_sentences(text)
    chunks = []
    current = ''

    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= chunk_size:
            current += (' ' if current else '') + sentence
        else:
            if current:
                chunks.append(current.strip())
            # Start new chunk with overlap from previous
            if len(current) > overlap:
                overlap_text = current[-overlap:]
                current = overlap_text + ' ' + sentence
            else:
                current = sentence

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 50]


def extract_sections(text: str) -> dict:
    """
    Attempt to identify named sections in a T&C document.
    Returns dict of {section_name: section_text}.
    """
    # Match numbered or titled sections like "1. Data Collection" or "DATA COLLECTION"
    pattern = re.compile(
        r'(?:^|\n)(?:(\d+\.?\s+)|([A-Z][A-Z\s]{3,}))([^\n]+)\n',
        re.MULTILINE
    )

    sections = {}
    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):
        title = match.group(0).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if content:
            sections[title] = content

    return sections


def estimate_reading_level(text: str) -> dict:
    """
    Estimate approximate reading complexity using simple metrics.
    Returns: avg_sentence_length, avg_word_length, estimated_grade
    """
    sentences = split_into_sentences(text)
    words = text.split()

    if not sentences or not words:
        return {'avg_sentence_length': 0, 'avg_word_length': 0, 'estimated_grade': 0}

    avg_sentence_length = len(words) / len(sentences)
    avg_word_length = sum(len(w) for w in words) / len(words)

    # Simplified Flesch-Kincaid estimate
    grade = 0.39 * avg_sentence_length + 11.8 * avg_word_length - 15.59
    grade = max(1, min(20, round(grade, 1)))

    return {
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_word_length': round(avg_word_length, 2),
        'estimated_grade': grade,
        'word_count': len(words),
        'sentence_count': len(sentences),
    }