"""
IEEE Research Paper Section Extractor.
Extracts specific sections from IEEE-style academic papers for targeted analysis.
"""
import re
from .text_extractor import extract_text


# Mapping of frontend section values to extraction logic
SECTION_KEYS = [
    "full_paper",
    "title",
    "abstract",
    "introduction",
    "related_work",
    "methodology",
    "dataset_experimental_setup",
    "results",
    "discussion",
    "conclusion",
    "references",
    "citations",
    "figures_tables",
]


def _normalize_text(text):
    """Normalize whitespace and clean text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def _find_section_boundaries(text, section_patterns):
    """
    Find start and end positions of a section.
    section_patterns: list of regex patterns that can start this section (in order of specificity).
    Returns (start_idx, end_idx) or (None, None) if not found.
    """
    text_lower = text.lower()
    best_start = None
    best_end = len(text)

    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            start = match.start()
            if best_start is None or start < best_start:
                best_start = start

    if best_start is None:
        return None, None

    return best_start, best_end


def _extract_between_sections(text, start_patterns, end_patterns):
    """
    Extract content between start_patterns and end_patterns.
    Returns the first matching block.
    """
    start_match = None
    for pat in start_patterns:
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if m:
            start_match = m
            break
    if not start_match:
        return ""

    content_start = start_match.end()
    content_end = len(text)
    for pat in end_patterns:
        m = re.search(pat, text[content_start:], re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if m:
            content_end = content_start + m.start()
            break

    return _normalize_text(text[content_start:content_end])


def extract_title(full_text):
    """Extract title - typically first non-empty line or before Abstract."""
    lines = [ln.strip() for ln in full_text.split("\n") if ln.strip()]
    if not lines:
        return ""
    # Title is usually before "Abstract" or the first substantial line
    title_parts = []
    for line in lines:
        if re.match(r"^(abstract|introduction|index terms|keywords)\s*[-—:]?\s*$", line, re.I):
            break
        if len(line) > 10 and not re.match(r"^\d+\.?\s", line):
            title_parts.append(line)
            if len(title_parts) >= 2:  # Sometimes title wraps to 2 lines
                break
    return _normalize_text(" ".join(title_parts)) if title_parts else _normalize_text(lines[0])


def extract_abstract(full_text):
    """Extract Abstract section."""
    start_patterns = [
        r"^abstract\s*[-—:]?\s*",
        r"\nabstract\s*[-—:]?\s*",
        r"^\s*abstract\s*\n",
    ]
    end_patterns = [
        r"\n\s*(?:index terms|keywords|introduction|i\.?\s*introduction|1\.?\s*introduction)\s*[-—:]?\s*",
        r"\n\s*(?:i\.?\s+introduction|1\.?\s+introduction)\b",
        r"\n\s*1\s+introduction\b",
        r"\nintroduction\s*[-—:]?\s*",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_introduction(full_text):
    """Extract Introduction section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:i\.?\s*)?introduction\s*[-—:]?\s*",
        r"(?:^|\n)\s*1\.?\s*introduction\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:ii\.?|2\.?)\s*(?:related\s+work|background|literature\s+review)\s*[-—:]?\s*",
        r"\n\s*(?:related\s+work|background)\s*[-—:]?\s*",
        r"\n\s*2\.?\s*related\s+work\b",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_related_work(full_text):
    """Extract Related Work / Background section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:ii\.?|2\.?)\s*(?:related\s+work|background|literature\s+review)\s*[-—:]?\s*",
        r"(?:^|\n)\s*related\s+work\s*[-—:]?\s*",
        r"(?:^|\n)\s*2\.?\s*related\s+work\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:iii\.?|3\.?)\s*(?:methodology|method|proposed\s+approach)\s*[-—:]?\s*",
        r"\n\s*(?:methodology|method)\s*[-—:]?\s*",
        r"\n\s*3\.?\s*(?:methodology|method)\b",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_methodology(full_text):
    """Extract Methodology / Method section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:iii\.?|3\.?)\s*(?:methodology|method|proposed\s+approach)\s*[-—:]?\s*",
        r"(?:^|\n)\s*(?:methodology|method)\s*[-—:]?\s*",
        r"(?:^|\n)\s*3\.?\s*(?:methodology|method)\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:iv\.?|4\.?)\s*(?:experimental|experiments|dataset|results)\s*[-—:]?\s*",
        r"\n\s*(?:experimental\s+setup|dataset|results)\s*[-—:]?\s*",
        r"\n\s*4\.?\s*(?:experimental|experiments|results)\b",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_dataset_experimental_setup(full_text):
    """Extract Dataset / Experimental Setup section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:iv\.?|4\.?)\s*(?:experimental\s+setup|dataset|experiments)\s*[-—:]?\s*",
        r"(?:^|\n)\s*(?:experimental\s+setup|dataset\s+and\s+experiments)\s*[-—:]?\s*",
        r"(?:^|\n)\s*4\.?\s*(?:experimental|dataset)\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:v\.?|5\.?)\s*results\s*[-—:]?\s*",
        r"\n\s*results\s*[-—:]?\s*",
        r"\n\s*5\.?\s*results\b",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_results(full_text):
    """Extract Results section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:v\.?|5\.?)\s*results\s*[-—:]?\s*",
        r"(?:^|\n)\s*results\s*[-—:]?\s*",
        r"(?:^|\n)\s*5\.?\s*results\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:vi\.?|6\.?)\s*discussion\s*[-—:]?\s*",
        r"\n\s*discussion\s*[-—:]?\s*",
        r"\n\s*(?:vi\.?|6\.?)\s*conclusion\s*[-—:]?\s*",
        r"\n\s*6\.?\s*(?:discussion|conclusion)\b",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_discussion(full_text):
    """Extract Discussion section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:vi\.?|6\.?)\s*discussion\s*[-—:]?\s*",
        r"(?:^|\n)\s*discussion\s*[-—:]?\s*",
        r"(?:^|\n)\s*6\.?\s*discussion\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*(?:vii\.?|7\.?)\s*conclusion\s*[-—:]?\s*",
        r"\n\s*conclusion\s*[-—:]?\s*",
        r"\n\s*7\.?\s*conclusion\b",
        r"\n\s*references\s*[-—:]?\s*",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_conclusion(full_text):
    """Extract Conclusion section."""
    start_patterns = [
        r"(?:^|\n)\s*(?:vii\.?|6\.?|7\.?)\s*conclusion\s*[-—:]?\s*",
        r"(?:^|\n)\s*conclusion\s*[-—:]?\s*",
        r"(?:^|\n)\s*7\.?\s*conclusion\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*references\s*[-—:]?\s*",
        r"\n\s*\[?\s*references\s*\]?\s*\n",
        r"\n\s*acknowledg(e)?ments?\s*[-—:]?\s*",
        r"\n\s*appendix\s*[-—:]?\s*",
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_references(full_text):
    """Extract References / Bibliography section."""
    start_patterns = [
        r"(?:^|\n)\s*references\s*[-—:]?\s*",
        r"(?:^|\n)\s*\[?\s*references\s*\]?\s*\n",
        r"(?:^|\n)\s*bibliography\s*[-—:]?\s*",
    ]
    end_patterns = [
        r"\n\s*acknowledg(e)?ments?\s*[-—:]?\s*",
        r"\n\s*appendix\s*[-—:]?\s*",
        r"\n\s*author\s+biograph",
        r"\n\s*\[?\d+\]?\s*[A-Z][a-z]+\s+[A-Z][a-z]+.*\n\n\s*$",  # End of refs
    ]
    return _extract_between_sections(full_text, start_patterns, end_patterns)


def extract_citations(full_text):
    """Extract inline citations (e.g., [1], [2-4], (Author, Year))."""
    # In-text citations like [1], [2,3], [4-6], (Smith et al., 2020)
    bracket_refs = re.findall(r"\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]", full_text)
    paren_refs = re.findall(r"\([A-Z][a-z]+(?:\s+et\s+al\.?)?(?:\s*,\s*\d{4})?\)", full_text)
    combined = bracket_refs + paren_refs
    return _normalize_text(" | ".join(combined)) if combined else ""


def extract_figures_tables(full_text):
    """Extract figure and table captions/mentions."""
    patterns = [
        r"(?:Fig\.|Figure)\s*\d+[^.]*\.\s*[^.]+(?=\.|$)",
        r"(?:Table)\s*\d+[^.]*\.\s*[^.]+(?=\.|$)",
        r"(?:Fig\.|Figure)\s*\d+[^.\n]{5,100}",
        r"Table\s*\d+[^.\n]{5,100}",
    ]
    results = []
    for pat in patterns:
        for m in re.finditer(pat, full_text, re.IGNORECASE):
            results.append(m.group(0).strip())
    return "\n".join(results) if results else ""


def extract_ieee_section(full_text, section_key):
    """
    Extract a specific section from IEEE-style paper text.

    Args:
        full_text: Full document text
        section_key: One of full_paper, title, abstract, introduction, related_work,
                     methodology, dataset_experimental_setup, results, discussion,
                     conclusion, references, citations, figures_tables

    Returns:
        str: Extracted section content
    """
    if not full_text or not full_text.strip():
        return ""

    section_key = (section_key or "full_paper").strip().lower()

    if section_key == "full_paper":
        return _normalize_text(full_text)

    extractors = {
        "title": extract_title,
        "abstract": extract_abstract,
        "introduction": extract_introduction,
        "related_work": extract_related_work,
        "methodology": extract_methodology,
        "dataset_experimental_setup": extract_dataset_experimental_setup,
        "results": extract_results,
        "discussion": extract_discussion,
        "conclusion": extract_conclusion,
        "references": extract_references,
        "citations": extract_citations,
        "figures_tables": extract_figures_tables,
    }

    if section_key not in extractors:
        return _normalize_text(full_text)

    content = extractors[section_key](full_text)
    return content if content else _normalize_text(full_text[:2000])  # Fallback to beginning


def extract_and_analyze_section(file_path, section_key):
    """
    Extract full text from file, then extract the requested section.

    Args:
        file_path: Path to PDF/DOCX file
        section_key: Section to extract (from frontend dropdown)

    Returns:
        tuple: (full_text, extracted_section_text)
    """
    full_text = extract_text(file_path)
    section_text = extract_ieee_section(full_text, section_key)
    return full_text, section_text
