"""
IEEE Research Paper AI Analysis with optional local transformer model.
Provides contributions, keywords, QA, methodology insights, and citations extraction.

If the local model directory is unavailable, summarization gracefully falls back to
a deterministic lightweight summary without crashing.
"""
import os
import re
from pathlib import Path
from typing import List

try:
    import torch
except Exception:  # pragma: no cover - runtime environment dependent
    torch = None

try:
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
except Exception:  # pragma: no cover - runtime environment dependent
    AutoModelForSeq2SeqLM = None
    AutoTokenizer = None

os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

_MODEL = None
_TOKENIZER = None
_MODEL_ERROR = None


def _get_model_dir() -> Path:
    root = Path(__file__).resolve().parents[2]  # backend root
    env_dir = os.getenv("LOCAL_IEEE_MODEL_DIR")
    if env_dir:
        return Path(env_dir)
    return root / "models" / "ieee-flan-t5-small"


def _load_model() -> None:
    global _MODEL, _TOKENIZER, _MODEL_ERROR
    if _MODEL is not None or _MODEL_ERROR is not None:
        return
    if AutoTokenizer is None or AutoModelForSeq2SeqLM is None:
        _MODEL_ERROR = RuntimeError("transformers package is not available")
        return
    model_dir = _get_model_dir()
    try:
        _TOKENIZER = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_dir, local_files_only=True)
        _MODEL.eval()
    except Exception as exc:
        _MODEL_ERROR = exc


def _generate(prompt: str, max_new_tokens: int = 180, min_new_tokens: int = 32) -> str:
    _load_model()
    if _MODEL is None or _TOKENIZER is None:
        raise RuntimeError("Offline summarization model unavailable") from _MODEL_ERROR

    if torch is None:
        raise RuntimeError("torch package is not available")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _MODEL.to(device)

    inputs = _TOKENIZER(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    ).to(device)

    with torch.no_grad():
        outputs = _MODEL.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            num_beams=2,
            do_sample=False,
            no_repeat_ngram_size=2,
            repetition_penalty=1.15,
            length_penalty=1.0,
            early_stopping=True,
        )
    text = _TOKENIZER.decode(outputs[0], skip_special_tokens=True)
    return text.strip()


def _split_text_into_chunks(text: str, max_words: int = 700, max_chunks: int = 3) -> List[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]

    chunks = []
    start = 0
    total = len(words)
    while start < total:
        end = min(start + max_words, total)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end
    if len(chunks) <= max_chunks:
        return chunks
    mid = len(chunks) // 2
    return [chunks[0], chunks[mid], chunks[-1]]


def _clean_source_text_for_summary(text: str) -> str:
    """Remove noisy bibliography/citation artifacts before summarization."""
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return ""

    # Remove URLs/links and ORCID identifiers.
    clean = re.sub(r"https?://\S+|www\.\S+", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\borcid\b[:\s]*\S+", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", " ", clean, flags=re.IGNORECASE)

    # Remove common copyright and publisher notices.
    clean = re.sub(r"\b(copyright|all rights reserved|personal use is permitted|ieee)\b[^.]{0,180}\.", " ", clean, flags=re.IGNORECASE)

    # Drop everything after References/Bibliography for full-paper summaries.
    clean = re.split(r"\b(?:references|bibliography)\b", clean, flags=re.IGNORECASE)[0]

    # Fix OCR line-break hyphenation like "Sys- tematic" -> "Systematic".
    clean = re.sub(r"(?<=\w)\s*-\s+(?=\w)", "", clean)

    # Remove citation-only fragments like [12], [3,4], (Smith et al., 2020)
    clean = re.sub(r"\[\s*\d+(?:\s*[-,]\s*\d+)*\s*\]", " ", clean)
    clean = re.sub(r"\([A-Z][a-z]+(?:\s+et\s+al\.?)?,\s*\d{4}\)", " ", clean)
    clean = re.sub(r"\([A-Za-z][A-Za-z\s.&-]+,\s*\d{4}[a-z]?\)", " ", clean)

    # Remove excessive author-title citation style fragments.
    clean = re.sub(r"\b[A-Z][a-z]+,\s*[A-Z]\.\s*(?:and|&)\s*[A-Z][a-z]+,\s*[A-Z]\.\b", " ", clean)

    # Remove page numbers and section numbering markers (I., II., III., 1., 2., ...).
    clean = re.sub(r"(?<!\w)\d{1,4}(?!\w)", " ", clean)
    clean = re.sub(r"\b(?:[IVX]{1,6}|[A-Z])\.\s+", " ", clean)
    clean = re.sub(r"(?:(?<=\s)|^)\d+\.\s+", " ", clean)

    # Remove common OCR artifacts / broken symbols.
    clean = re.sub(r"[^\x20-\x7E]", " ", clean)  # non-ASCII
    clean = re.sub(r"[|`~^_=<>]{2,}", " ", clean)
    clean = re.sub(r"\b[a-zA-Z]{1,2}\s*-\s*[a-zA-Z]{1,2}\b", " ", clean)
    clean = re.sub(r"\b(?:isbn|inproceedings|proceedings|volume|pages)\b[^.]{0,120}\.", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"/\d{6,}", " ", clean)
    clean = re.sub(r"\b\d{6,}\b", " ", clean)
    clean = re.sub(r"\b(?:fig\.?|figure|table)\s*\d+\b[^.]{0,180}\.", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\b(?:appendix|acknowledg(?:e)?ments?)\b[^.]{0,180}\.", " ", clean, flags=re.IGNORECASE)
    clean = re.sub(r"\b(?:author|affiliation|corresponding author)\b[^.]{0,180}\.", " ", clean, flags=re.IGNORECASE)

    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _approx_tokens_for_words(word_count: int) -> int:
    # Rough conversion for English text generation: ~0.75 words per token.
    return max(64, int(word_count / 0.75))


def _trim_to_word_budget(text: str, target_words: int) -> str:
    words = (text or "").split()
    if len(words) <= target_words:
        return text
    return " ".join(words[:target_words]).strip()


def _parse_bullets(text: str) -> List[str]:
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    points: List[str] = []
    for ln in lines:
        ln = re.sub(r"^[\-\*\u2022\d\.\)\s]+", "", ln).strip()
        if len(ln) < 8:
            continue
        if ln.lower().startswith(("key points", "clean summary", "summary")):
            continue
        points.append(ln)
    # de-duplicate while preserving order
    seen = set()
    out = []
    for p in points:
        k = p.lower()
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out[:8]


def _sanitize_point_text(point: str) -> str:
    s = re.sub(r"\s+", " ", (point or "")).strip(" -;:,.")
    s = re.sub(r"https?://\S+|www\.\S+", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(
        r"\b(?:isbn|inproceedings|proceedings|volume|pages|iceis)\b[^.]{0,80}",
        "",
        s,
        flags=re.IGNORECASE,
    ).strip()
    s = re.sub(r"\bindex terms?\b[:\-]?\s*[^.]{0,80}", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(r"^(?:my\s+)+", "", s, flags=re.IGNORECASE).strip()
    s = re.sub(
        r"^(?:introduction|related work|methodology|experimental setup|results|conclusion)\s*[:\-]?\s*",
        "",
        s,
        flags=re.IGNORECASE,
    ).strip()
    if _is_noisy_sentence(s):
        return ""
    return s.strip(" -;:,.")


def _deterministic_summary_from_points(points: List[str], target_words: int) -> str:
    cleaned: List[str] = []
    seen = set()
    for p in points:
        cp = _sanitize_point_text(p)
        if not cp:
            continue
        key = cp.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(cp)

    if not cleaned:
        return ""

    sentences = []
    for p in cleaned:
        if len(p.split()) < 5:
            continue
        sentences.append(p.rstrip(".") + ".")

    summary = " ".join(sentences).strip()
    summary = _ensure_complete_sentences(summary)
    summary = _trim_to_word_budget(summary, int(target_words * 1.1))
    return summary


def _extract_key_ideas(source: str) -> dict:
    sents = [s for s in _split_sentences(source) if not _is_noisy_sentence(s)]
    categories = {
        "problem": ["problem", "challenge", "difficult", "misinformation", "complex"],
        "objective": ["objective", "aim", "goal", "this paper", "we propose", "we present", "introduce"],
        "methodology": ["method", "approach", "dataset", "collect", "graph", "classification", "model"],
        "findings": ["result", "findings", "contribution", "improve", "performance", "baseline"],
        "limitations": ["limitation", "challenge", "lack", "constraint", "future work"],
        "impact": ["conclusion", "impact", "implication", "support", "enable"],
    }
    ideas = {}
    for key, cues in categories.items():
        best = ""
        best_score = 0
        for sent in sents:
            low = sent.lower()
            score = sum(1 for c in cues if c in low)
            if "figure" in low or "table" in low or "index terms" in low:
                score -= 2
            if score > best_score:
                best_score = score
                best = sent
        if best and best_score > 0:
            ideas[key] = _sanitize_point_text(best)
    return ideas


def _template_summary_from_ideas(ideas: dict, target_words: int) -> str:
    ordered = ["problem", "objective", "methodology", "findings", "limitations", "impact"]
    prefix = {
        "problem": "The paper addresses",
        "objective": "Its main objective is",
        "methodology": "The methodology uses",
        "findings": "The main findings show",
        "limitations": "The study also notes",
        "impact": "Overall, the work contributes by",
    }
    lines = []
    seen_lines = set()
    for key in ordered:
        value = (ideas.get(key) or "").strip().rstrip(".")
        if not value:
            continue
        if value.lower().startswith(("the paper", "this paper", "we ")):
            line = value[0].upper() + value[1:] + "."
        else:
            line = f"{prefix[key]} {value}."
        norm = re.sub(r"\s+", " ", line.lower()).strip()
        if norm in seen_lines:
            continue
        seen_lines.add(norm)
        lines.append(line)
    if not lines:
        return ""
    summary = " ".join(lines)
    summary = _ensure_complete_sentences(summary)
    return _trim_to_word_budget(summary, int(target_words * 1.1))


def _normalize_clause(text: str) -> str:
    t = re.sub(r"\s+", " ", (text or "")).strip().rstrip(".")
    t = re.sub(
        r"^(?:this paper|the paper|we|authors?)\s+(?:introduce|present|propose|show|evaluate|discuss)\s+",
        "",
        t,
        flags=re.IGNORECASE,
    )
    t = re.sub(r"^(?:introduction|related work|methodology|results|conclusion)\s*[:\-]?\s*", "", t, flags=re.IGNORECASE)
    return t.strip(" ,;:-")


def _build_proportional_summary(ideas: dict, source: str, target_words: int) -> str:
    """
    Build a readable summary with dynamic length based on target_words.
    """
    ordered = ["problem", "objective", "methodology", "findings", "limitations", "impact"]
    starters = {
        "problem": "The study addresses",
        "objective": "Its objective is",
        "methodology": "To achieve this, the authors use",
        "findings": "The main findings indicate",
        "limitations": "The work also reports",
        "impact": "Overall, the paper contributes by",
    }

    sentences: List[str] = []
    seen = set()
    for key in ordered:
        raw = _normalize_clause(ideas.get(key, ""))
        if not raw:
            continue
        sent = f"{starters[key]} {raw}."
        norm = re.sub(r"\s+", " ", sent.lower()).strip()
        if norm in seen:
            continue
        seen.add(norm)
        sentences.append(sent)

    # Expand proportionally with additional high-importance sentences when needed.
    if len(" ".join(sentences).split()) < int(target_words * 0.8):
        extras = _split_sentences(_select_important_content(source, ratio=0.45))
        for ex in extras:
            ex = _sanitize_point_text(ex)
            ex = _normalize_clause(ex)
            if not ex:
                continue
            sent = f"The paper additionally highlights that {ex[0].lower() + ex[1:] if len(ex) > 1 else ex}."
            norm = re.sub(r"\s+", " ", sent.lower()).strip()
            if norm in seen:
                continue
            if _is_noisy_sentence(sent):
                continue
            sentences.append(sent)
            seen.add(norm)
            if len(" ".join(sentences).split()) >= target_words:
                break

    summary = _ensure_complete_sentences(" ".join(sentences))

    # Lightweight rewrite to improve flow while staying on extracted ideas.
    rewrite_prompt = (
        "Rewrite the following draft into fluent academic English.\n"
        "Keep meaning unchanged. Do not add new facts.\n"
        "Do not include links, citations, names, or headings.\n\n"
        f"Draft:\n{summary}\n\n"
        "Rewritten summary:"
    )
    rewritten = _sanitize_summary_text(
        _generate(
            rewrite_prompt,
            max_new_tokens=min(520, _approx_tokens_for_words(target_words + 40)),
            min_new_tokens=max(90, _approx_tokens_for_words(max(80, int(target_words * 0.6)))),
        )
    )
    cleaned = _filter_bad_summary_sentences(rewritten)
    cleaned = _ensure_complete_sentences(cleaned)
    if len(cleaned.split()) < max(50, int(target_words * 0.5)):
        cleaned = summary

    return _trim_to_word_budget(cleaned, int(target_words * 1.05))


def _to_concept_phrase(text: str, max_words: int = 12) -> str:
    s = _sanitize_point_text(text)
    s = _normalize_clause(s)
    if not s:
        return ""
    # Keep concise content words.
    tokens = re.findall(r"[A-Za-z0-9\-]+", s.lower())
    stop = {
        "the", "a", "an", "and", "or", "to", "of", "for", "with", "in", "on", "from",
        "that", "this", "these", "those", "is", "are", "was", "were", "be", "been",
        "it", "its", "their", "our", "by", "as", "at", "into", "using", "use",
    }
    filtered = [t for t in tokens if t not in stop]
    if not filtered:
        filtered = tokens
    phrase = " ".join(filtered[:max_words]).strip()
    return phrase


def _extract_key_concepts(source: str, max_concepts: int = 5) -> List[str]:
    ideas = _extract_key_ideas(source)
    ordered_keys = ["problem", "objective", "methodology", "findings", "impact", "limitations"]
    concepts: List[str] = []
    seen = set()

    for key in ordered_keys:
        if not ideas.get(key):
            continue
        c = _to_concept_phrase(ideas[key], max_words=12)
        if not c:
            continue
        if c in seen:
            continue
        seen.add(c)
        concepts.append(c)
        if len(concepts) >= max_concepts:
            break

    if len(concepts) < max_concepts:
        extras = _split_sentences(_select_important_content(source, ratio=0.40))
        for ex in extras:
            c = _to_concept_phrase(ex, max_words=12)
            if not c or c in seen:
                continue
            seen.add(c)
            concepts.append(c)
            if len(concepts) >= max_concepts:
                break

    return concepts[:max_concepts]


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _full_paper_concept_summary(clean_text: str) -> str:
    concepts = _extract_key_concepts(clean_text, max_concepts=5)
    if not concepts:
        concepts = ["research problem and objective", "methodological design and dataset", "main findings and impact"]

    concept_block = "\n".join(f"- {c}" for c in concepts)

    summary_prompt = (
        "You are an expert academic paper summarizer.\n"
        "Write one coherent academic paragraph using ONLY the concepts below.\n"
        "Do not copy source sentences. Do not include authors, title, links, or citations.\n"
        "Target length: 150 to 180 words.\n\n"
        f"Concepts:\n{concept_block}\n\n"
        "Summary:"
    )
    generated = _sanitize_summary_text(
        _generate(
            summary_prompt,
            max_new_tokens=300,
            min_new_tokens=190,
        )
    )
    generated = _filter_bad_summary_sentences(generated)
    generated = _ensure_complete_sentences(generated)

    wc = _count_words(generated)
    if wc < 120 or wc > 210 or _is_low_quality_summary(generated):
        # Deterministic fallback paragraph from concepts.
        base = (
            f"This paper addresses {concepts[0]} and focuses on {concepts[1] if len(concepts) > 1 else 'a clear research objective'}. "
            f"The study develops a methodology centered on {concepts[2] if len(concepts) > 2 else 'a structured analytical approach'} "
            "to investigate the target problem in a reproducible manner. "
            f"It reports findings related to {concepts[3] if len(concepts) > 3 else 'model behavior and empirical outcomes'}, "
            "showing how the proposed setup supports practical analysis. "
            f"The work also emphasizes {concepts[4] if len(concepts) > 4 else 'broader research impact and applicability'}, "
            "which helps position the contribution within ongoing academic and applied research. "
            "Overall, the paper presents a coherent framework that links problem definition, method design, and empirical validation, "
            "offering a useful foundation for future extensions and comparative evaluation."
        )
        generated = base

    words = re.findall(r"\S+", generated)
    if len(words) > 180:
        generated = " ".join(words[:180]).strip()
        generated = _ensure_complete_sentences(generated)
    if len(words) < 150:
        # Soft extension to reach requested range without adding noise.
        generated = (
            generated
            + " The analysis also clarifies how the selected methodology, data representation, and evaluation choices interact, "
            "which improves interpretability and supports replication in related studies."
        )
        words = re.findall(r"\S+", generated)
        if len(words) > 180:
            generated = " ".join(words[:180]).strip()
            generated = _ensure_complete_sentences(generated)

    return (
        "Section: Full Paper\n\n"
        f"Key Concepts:\n{concept_block}\n\n"
        f"Clean Summary:\n{generated.strip()}"
    ).strip()


def _select_representative_chunks(text: str, chunk_words: int = 520, max_chunks: int = 5) -> List[str]:
    words = text.split()
    if len(words) <= chunk_words:
        return [text]

    chunks = []
    for i in range(0, len(words), chunk_words):
        chunks.append(" ".join(words[i : i + chunk_words]))

    if len(chunks) <= max_chunks:
        return chunks

    # Evenly sample across full document so we don't bias to introduction only.
    selected = []
    for idx in range(max_chunks):
        pos = round(idx * (len(chunks) - 1) / (max_chunks - 1))
        selected.append(chunks[pos])
    return selected


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if s and s.strip()]


def _is_noisy_sentence(s: str) -> bool:
    if not s or len(s) < 25:
        return True
    low = s.lower()
    noisy_patterns = [
        "http://",
        "https://",
        "www.",
        "isbn",
        "inproceedings",
        "proceedings",
        "conference on",
        "iceis",
        "all rights reserved",
    ]
    if any(p in low for p in noisy_patterns):
        return True
    if re.search(r"[^\x00-\x7F]", s):
        return True
    if re.search(r"(?:[A-Z]\.){4,}", s):
        return True
    if re.search(r"[*/_=<>]{3,}", s):
        return True
    return False


def _select_important_content(text: str, ratio: float = 0.35) -> str:
    """
    Select top informative sentences and keep about `ratio` of the source words.
    Deterministic fallback to avoid model-generated garbage.
    """
    sentences = _split_sentences(text)
    clean_sentences = [s for s in sentences if not _is_noisy_sentence(s)]
    if not clean_sentences:
        return text

    # Build simple word-frequency importance model.
    words = re.findall(r"[A-Za-z]{3,}", " ".join(clean_sentences).lower())
    freq = {}
    for w in words:
        if w in {
            "the", "and", "for", "with", "this", "that", "from", "were", "have", "has",
            "into", "their", "using", "used", "also", "been", "are", "was", "can", "may",
        }:
            continue
        freq[w] = freq.get(w, 0) + 1

    cue_terms = [
        "problem", "objective", "method", "approach", "dataset", "experiment", "result",
        "contribution", "challenge", "limitation", "conclusion", "impact",
    ]

    scored = []
    for idx, s in enumerate(clean_sentences):
        toks = re.findall(r"[A-Za-z]{3,}", s.lower())
        base = sum(freq.get(t, 0) for t in toks) / max(1, len(toks))
        cue = sum(1 for c in cue_terms if c in s.lower())
        length_penalty = 0.0 if len(toks) <= 45 else -0.5
        score = base + (0.8 * cue) + length_penalty
        scored.append((idx, s, score))

    scored.sort(key=lambda x: x[2], reverse=True)
    target_words = max(120, int(len(text.split()) * ratio))
    picked = []
    used_words = 0
    for idx, s, _ in scored:
        w = len(s.split())
        if used_words >= target_words:
            break
        picked.append((idx, s))
        used_words += w

    picked.sort(key=lambda x: x[0])
    return " ".join(s for _, s in picked).strip()


def _extract_key_points_deterministic(source: str, max_points: int = 8) -> List[str]:
    sentences = _split_sentences(source)
    clean_sentences = [s for s in sentences if not _is_noisy_sentence(s)]
    if not clean_sentences:
        return []

    cue_map = [
        ("problem", ["problem", "challenge", "complex", "difficulty"]),
        ("objective", ["objective", "aim", "goal", "this paper"]),
        ("method", ["method", "approach", "review", "dataset", "experiment"]),
        ("findings", ["result", "findings", "contribution", "improve", "performance"]),
        ("limitations", ["limitation", "threat", "issue", "lack"]),
        ("impact", ["conclusion", "impact", "implication", "future work"]),
    ]

    selected: List[str] = []
    used = set()
    for _, cues in cue_map:
        best = None
        best_score = -1
        for s in clean_sentences:
            low = s.lower()
            if low in used:
                continue
            score = sum(1 for c in cues if c in low)
            score += min(3, len(s.split()) // 12)
            if "index terms" in low:
                score -= 2
            if score > best_score:
                best_score = score
                best = s
        if best and best_score > 0:
            used.add(best.lower())
            selected.append(best)
            if len(selected) >= max_points:
                break

    # fill remaining with informative sentences
    if len(selected) < max_points:
        important = _split_sentences(_select_important_content(source, ratio=0.40))
        for s in important:
            low = s.lower()
            if low in used or _is_noisy_sentence(s):
                continue
            used.add(low)
            selected.append(s)
            if len(selected) >= max_points:
                break

    out = []
    for s in selected:
        s = _sanitize_point_text(s)
        if not s:
            continue
        s = re.sub(r"\bindex terms?\b[:\-]?\s*", "", s, flags=re.IGNORECASE).strip()
        out.append(s)
    return out[:max_points]


def _extract_key_points_multi_chunk(source: str, section_label: str) -> List[str]:
    chunks = _select_representative_chunks(source, chunk_words=520, max_chunks=5)
    merged_points: List[str] = []

    for idx, chunk in enumerate(chunks, start=1):
        prompt = (
            "You are an expert research paper summarizer.\n"
            f"Section scope: {section_label}.\n"
            "From this text chunk, extract concise key ideas as bullets for:\n"
            "- research problem\n"
            "- objective\n"
            "- methodology\n"
            "- findings/contributions\n"
            "- challenges/limitations\n"
            "- conclusion/impact\n"
            "Do not include links, references, conference metadata, or author names.\n\n"
            f"Chunk {idx}/{len(chunks)}:\n{chunk}\n\n"
            "Key Points:"
        )
        raw = _generate(prompt, max_new_tokens=180, min_new_tokens=70)
        pts = _parse_bullets(_sanitize_summary_text(raw))
        merged_points.extend(pts)

    # De-duplicate and remove noisy points.
    cleaned: List[str] = []
    seen = set()
    noisy_markers = [
        "inproceedings",
        "isbn",
        "conference",
        "volume",
        "pages",
        "iceis",
        "http",
        "www.",
    ]
    for p in merged_points:
        low = p.lower()
        if any(m in low for m in noisy_markers):
            continue
        if len(p.split()) < 5:
            continue
        key = re.sub(r"\s+", " ", low).strip()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(p)
        if len(cleaned) >= 12:
            break

    return cleaned


def _filter_bad_summary_sentences(text: str) -> str:
    if not text:
        return ""
    banned = [
        "key points",
        "clean summary",
        "do not copy",
        "rewrite fully",
        "target length",
        "http://",
        "https://",
        "www.",
        "disclaimer",
        "click the link",
        "published in",
        "this article was originally",
        "inproceedings",
        "proceedings of",
        "isbn",
        "conference on enterprise information systems",
        "volume",
        "pages",
        "this paper presents the following structure",
        "section concludes",
        "iceis",
        "in this paper, we seek to understand",
        "this paper presents the following structure",
        "index terms",
    ]
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    kept: List[str] = []
    for p in parts:
        s = p.strip()
        if len(s) < 20:
            continue
        l = s.lower()
        if any(b in l for b in banned):
            continue
        if re.search(r"[^\x00-\x7F]", s):
            continue
        if re.search(r"(?:[A-Z]\.){4,}", s):
            continue
        # Drop sentences with too much symbol noise
        noise = sum(1 for ch in s if not (ch.isalnum() or ch.isspace() or ch in ".,;:!?()-"))
        if noise > 6:
            continue
        kept.append(s)
    return " ".join(kept).strip()


def _ensure_complete_sentences(text: str) -> str:
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    complete = [p.strip() for p in parts if p.strip().endswith((".", "!", "?"))]
    if complete:
        return " ".join(complete)
    # Fallback: cut at last sentence terminator if present
    m = re.search(r"^(.+[.!?])[^.!?]*$", text.strip())
    return (m.group(1) if m else text.strip()).strip()


def _finalize_clean_summary(summary: str, source: str, target_words: int, bullet_block: str) -> str:
    out = _filter_bad_summary_sentences(_sanitize_summary_text(summary))
    out = _ensure_complete_sentences(out)
    out = _trim_to_word_budget(out, int(target_words * 1.1))

    # Deterministic safe fallback if model remains noisy.
    if len(out.split()) < 70 or _is_low_quality_summary(out):
        out = _trim_to_word_budget(_select_important_content(source, ratio=0.35), int(target_words * 1.1))
        out = _ensure_complete_sentences(out)

    return out


def _two_step_academic_summary(text: str, section_label: str, target_words: int) -> str:
    source = _clean_source_text_for_summary(text)
    if not source:
        return ""
    focused_source = _select_important_content(source, ratio=0.35)
    if focused_source:
        source = focused_source

    # STEP 1 — Deterministic key-idea extraction across cleaned content.
    ideas = _extract_key_ideas(source)
    points = [ideas[k] for k in ["problem", "objective", "methodology", "findings", "limitations", "impact"] if ideas.get(k)]

    # Fallback if model fails to produce clean bullets
    if len(points) < 4:
        extra = _split_sentences(_select_important_content(source, ratio=0.40))
        points = [_sanitize_point_text(s) for s in extra if _sanitize_point_text(s)]
        points = points[:8]

    if not points:
        points = ["The paper discusses a research problem, method, findings, and implications."]

    bullet_block = "\n".join(f"- {p}" for p in points)
    deterministic_summary = _build_proportional_summary(ideas, source, target_words)
    if not deterministic_summary:
        deterministic_summary = _deterministic_summary_from_points(points, target_words)

    # STEP 2 — Build clean summary from key points (deterministic to avoid garbage).
    summary = deterministic_summary

    final_summary = _finalize_clean_summary(summary or deterministic_summary, source, target_words, bullet_block).strip()
    if not final_summary or _is_low_quality_summary(final_summary):
        final_summary = deterministic_summary

    return (
        f"Section: {section_label}\n\n"
        f"Key Points:\n{bullet_block}\n\n"
        f"Clean Summary:\n{final_summary}"
    ).strip()


def _sanitize_summary_text(text: str) -> str:
    if not text:
        return ""

    cleaned = re.sub(r"\s+", " ", text).strip()
    banned_markers = [
        "abstractive summary",
        "intermediate summaries",
        "chunk ",
        "paraphrase fully",
        "do not copy exact lines",
        "write 5-7",
        "write 7-10",
        "write 8-12",
        "final abstractive summary",
        "expanded summary",
        "objective, method",
    ]

    # Split into sentence-like parts and remove instruction leakage.
    candidates = re.split(r"(?<=[.!?])\s+", cleaned)
    kept = []
    for sent in candidates:
        s = sent.strip(" -:\n\t")
        if len(s) < 28:
            continue
        lowered = s.lower()
        if any(marker in lowered for marker in banned_markers):
            continue
        # Keep only text with enough alphabetic content
        alpha = sum(ch.isalpha() for ch in s)
        if alpha < 18:
            continue
        kept.append(s)

    if kept:
        return " ".join(kept)
    return cleaned


def _is_low_quality_summary(text: str) -> bool:
    lowered = (text or "").lower()
    if len((text or "").split()) < 35:
        return True
    markers = [
        "intermediate summaries",
        "chunk 1/",
        "abstractive summary for",
        "write 7-10",
        "do not copy exact lines",
        "index terms",
        "inproceedings",
        "http://",
        "https://",
        "www.",
        "conference on enterprise information systems",
    ]
    return any(m in lowered for m in markers)


def _polish_summary(summary_text: str, source_text: str, section_label: str) -> str:
    cleaned = _sanitize_summary_text(summary_text)
    if not cleaned:
        return ""

    prompt = (
        "Improve the following draft summary for clarity, grammar, and completeness.\n"
        "Keep it factual and grounded in the source. Do not add new facts.\n"
        f"Write a coherent {section_label} summary in 5-8 sentences covering:\n"
        "motivation, method, key findings, and practical implication.\n\n"
        f"Source:\n{source_text[:3200]}\n\n"
        f"Draft summary:\n{cleaned}\n\n"
        "Improved summary:"
    )
    improved = _sanitize_summary_text(
        _generate(prompt, max_new_tokens=320, min_new_tokens=130)
    )
    if not improved:
        return cleaned
    return improved


def _summarize_abstractive(text: str, section_label: str) -> str:
    clean_text = _clean_source_text_for_summary(text)
    if not clean_text:
        return ""
    src_words = len(clean_text.split())
    min_words, max_words = _section_word_bounds(section_label)
    target_words = max(min_words, min(int(src_words * 0.35), max_words))
    target_words = min(target_words, max(20, int(src_words * 0.9)))
    return _two_step_academic_summary(clean_text, section_label, target_words)[:4500]


def _summarize_full_paper(text: str) -> str:
    clean_text = _clean_source_text_for_summary(text)
    if not clean_text:
        return ""
    return _full_paper_concept_summary(clean_text)[:5200]


def _section_word_bounds(section_key: str) -> tuple[int, int]:
    key = (section_key or "").strip().lower().replace(" ", "_")
    if key == "abstract":
        return (40, 80)
    if key == "introduction":
        return (80, 120)
    if key in ("methodology", "dataset", "dataset_experimental_setup"):
        return (80, 150)
    if key in ("results", "experiments"):
        return (60, 120)
    if key == "conclusion":
        return (40, 80)
    if key == "full_paper":
        return (150, 200)
    return (80, 140)


def _clean_bullets(lines: List[str]) -> List[str]:
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^[\-\•\d\.\)\s]+", "", line)
        if line:
            cleaned.append(line)
    return cleaned


def extract_contributions(text: str):
    """Return up to 5 concise contribution points (<20 words each)."""
    source = _clean_source_text_for_summary(text or "")
    if not source or len(source.split()) < 30:
        return []

    ideas = _extract_key_ideas(source)
    points = []
    candidates = [
        ideas.get("objective", ""),
        ideas.get("methodology", ""),
        ideas.get("findings", ""),
        ideas.get("impact", ""),
        ideas.get("problem", ""),
    ]
    for c in candidates:
        p = _to_concept_phrase(c, max_words=18)
        if p:
            points.append(p)

    # Fill from important content if needed.
    if len(points) < 5:
        for s in _split_sentences(_select_important_content(source, ratio=0.35)):
            p = _to_concept_phrase(s, max_words=18)
            if p and p not in points:
                points.append(p)
            if len(points) >= 5:
                break

    return points[:5]


def extract_keywords(text: str):
    """Extract 8-12 domain-relevant technical keywords only."""
    source = _clean_source_text_for_summary(text or "")
    if not source or len(source.split()) < 20:
        return []

    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]{1,}", source.lower())
    stop = {
        "a", "an", "and", "are", "as", "at", "be", "been", "being", "by", "can", "could",
        "did", "do", "does", "done", "for", "from", "had", "has", "have", "if", "in", "into",
        "is", "it", "its", "may", "might", "of", "on", "or", "our", "s", "such", "than",
        "that", "the", "their", "them", "there", "these", "this", "those", "to", "was", "we",
        "were", "what", "when", "where", "which", "while", "who", "why", "with", "would",
        "paper", "study", "approach", "result", "results", "method", "methods", "introduction",
        "conclusion", "related", "work", "using", "based", "analysis", "research", "problem",
        "objective", "proposed", "system", "performance", "section", "index", "terms", "figure",
        "table", "number", "original", "dataset"  # keep as generic unless part of a phrase
    }
    generic = {
        "paper", "study", "approach", "analysis", "research", "problem", "objective", "performance",
        "system", "section", "number", "original"
    }
    domain_hints = {
        "machine", "learning", "software", "engineering", "classification", "clustering",
        "graph", "neural", "network", "misinformation", "conspiracy", "twitter",
        "evaluation", "baseline", "features", "dataset", "modeling", "detection",
        "prediction", "pico", "literature", "review", "retweet", "subgraph"
    }

    # keep only clean content tokens
    seq = []
    for t in tokens:
        if len(t) < 3:
            continue
        if t in stop:
            continue
        if not re.fullmatch(r"[a-z0-9\-]+", t):
            continue
        seq.append(t)

    if not seq:
        return []

    # score n-grams (1-3) by frequency and domain relevance
    cand_scores = {}
    for i in range(len(seq)):
        for n in (1, 2, 3):
            if i + n > len(seq):
                continue
            gram_tokens = seq[i : i + n]
            # reject repeated tokens and too generic candidates
            if len(set(gram_tokens)) < len(gram_tokens):
                continue
            if all(t in generic for t in gram_tokens):
                continue
            gram = " ".join(gram_tokens)
            freq_bonus = 1.0
            domain_bonus = 1.5 if any(t in domain_hints for t in gram_tokens) else 0.0
            length_bonus = 0.4 * (n - 1)
            cand_scores[gram] = cand_scores.get(gram, 0.0) + freq_bonus + domain_bonus + length_bonus

    ranked = sorted(cand_scores.items(), key=lambda x: x[1], reverse=True)

    out = []
    seen = set()
    for gram, _ in ranked:
        toks = gram.split()
        if len(toks) == 1 and toks[0] not in domain_hints:
            continue
        # Ensure at least one technical token
        if not any(t in domain_hints for t in toks):
            continue
        norm = gram.strip().lower()
        if norm in seen:
            continue
        # avoid near duplicates by token subset
        if any(set(norm.split()).issubset(set(o.split())) or set(o.split()).issubset(set(norm.split())) for o in seen):
            continue
        seen.add(norm)
        out.append(norm)
        if len(out) >= 12:
            break

    # If still short, backfill with domain hints that appear in text.
    if len(out) < 8:
        present_hints = [h for h in sorted(domain_hints) if re.search(rf"\b{re.escape(h)}\b", source.lower())]
        for h in present_hints:
            if h not in seen:
                out.append(h)
                seen.add(h)
            if len(out) >= 8:
                break

    return [k.title() for k in out[:12]]


def generate_questions(text: str):
    """Generate exactly 5 non-yes/no comprehension questions."""
    source = _clean_source_text_for_summary(text or "")
    if not source or len(source.split()) < 30:
        return []

    ideas = _extract_key_ideas(source)
    method = _to_concept_phrase(ideas.get("methodology", ""), max_words=10) or "the methodology"
    findings = _to_concept_phrase(ideas.get("findings", ""), max_words=10) or "the key findings"
    problem = _to_concept_phrase(ideas.get("problem", ""), max_words=10) or "the research problem"
    impact = _to_concept_phrase(ideas.get("impact", ""), max_words=10) or "the practical impact"
    objective = _to_concept_phrase(ideas.get("objective", ""), max_words=10) or "the study objective"

    questions = [
        f"How does the paper frame {problem} in its research context?",
        f"What design choices define {method} in this study?",
        f"Which evidence best supports {findings} reported by the authors?",
        f"In what ways does {impact} influence future research or applications?",
        f"How could the approach be extended to better satisfy {objective}?",
    ]
    return questions


def get_methodology_insights(text: str):
    """Return 4-6 methodology bullets focused on data, modeling, evaluation."""
    source = _clean_source_text_for_summary(text or "")
    if not source or len(source.split()) < 30:
        return []

    sents = [s for s in _split_sentences(source) if not _is_noisy_sentence(s)]
    method_cues = ["dataset", "data", "collect", "preprocess", "model", "training", "evaluate", "baseline", "experiment", "metric"]
    scored = []
    for s in sents:
        low = s.lower()
        score = sum(1 for c in method_cues if c in low)
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)

    out = []
    seen = set()
    for _, s in scored:
        p = _to_concept_phrase(s, max_words=18)
        if not p:
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
        if len(out) >= 6:
            break

    return out[:6] if len(out) >= 4 else out


def extract_citations(text: str):
    """Extract up to 10 citations in `Author, Year` format."""
    if not text:
        return []
    raw = re.findall(
        r"\(([A-Z][A-Za-z\-]+)(?:\s+et\s+al\.?)?,\s*(\d{4}[a-z]?)\)",
        text,
    )
    out = []
    seen = set()
    for author, year in raw:
        item = f"{author}, {year}"
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
        if len(out) >= 10:
            break
    return out


def summarize_section(text: str, section_key: str | None = None) -> str:
    """
    Abstractive summary of a section using the local transformer model.

    Produces a short, paraphrased summary (3–4 sentences) in simple language.
    """
    return summarize_section_with_meta(text, section_key).get("summary", "")


def _fallback_summary_text(text: str, max_chars: int = 800) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "")).strip()
    if not cleaned:
        return ""
    return cleaned[:max_chars].strip()


def summarize_section_with_meta(text: str, section_key: str | None = None) -> dict:
    """
    Safe summarization wrapper.
    Never raises; always returns a metadata-rich summary payload.
    """
    if not text or not text.strip():
        return {
            "success": True,
            "summary": "",
            "message": "No text available to summarize",
            "fallback_used": True,
        }

    normalized_key = (section_key or "full_paper").strip().lower()
    section_label = normalized_key.replace("_", " ").title()
    model_dir = _get_model_dir()
    model_available = model_dir.exists() and model_dir.is_dir()

    if not model_available:
        print("Model not found, using fallback summary")
        return {
            "success": True,
            "summary": _fallback_summary_text(text, max_chars=900),
            "message": "Fallback summary used",
            "fallback_used": True,
        }

    try:
        summary = (
            _summarize_full_paper(text)
            if normalized_key == "full_paper"
            else _summarize_abstractive(text, section_label)
        )
        summary = (summary or "").strip()
        if not summary:
            print("Model returned empty summary, using fallback summary")
            return {
                "success": True,
                "summary": _fallback_summary_text(text, max_chars=900),
                "message": "Fallback summary used",
                "fallback_used": True,
            }
        return {
            "success": True,
            "summary": summary,
            "message": "Summary generated successfully",
            "fallback_used": False,
        }
    except Exception as exc:
        print("Model not found, using fallback summary")
        print(f"Summarization error: {exc}")
        return {
            "success": True,
            "summary": _fallback_summary_text(text, max_chars=900),
            "message": "Fallback summary used",
            "fallback_used": True,
        }

