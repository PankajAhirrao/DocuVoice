import json
from pathlib import Path

import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

_embedder = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder


def extract_pdf_text(pdf_path: str | Path) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        parts = []
        for page in reader.pages:
            parts.append((page.extract_text() or "").strip())
        text = "\n".join(parts).strip()
        print(f"[rag.extract_pdf_text] path={pdf_path}, text_length={len(text)}")
        return text
    except Exception as e:
        print(f"[rag.extract_pdf_text] error: {e}", flush=True)
        raise ValueError(f"Failed to extract PDF text: {e}") from e


def chunk_text(text: str, size: int = 500, overlap: int = 100) -> list[str]:
    text = text.replace("\x00", " ").strip()
    if not text:
        return []
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        chunks.append(text[i : i + size].strip())
        i += max(1, size - overlap)
    return [c for c in chunks if c]


def build_store(doc_dir: Path, text: str) -> int:
    chunks = chunk_text(text or "")
    if not chunks:
        print("[rag.build_store] no chunks generated")
        raise ValueError("No extractable text in PDF")
    model = get_embedder()
    emb = model.encode(chunks, normalize_embeddings=True, show_progress_bar=False)
    dim = int(emb.shape[1])
    index = faiss.IndexFlatIP(dim)
    index.add(emb.astype("float32"))
    doc_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(doc_dir / "index.faiss"))
    (doc_dir / "chunks.json").write_text(json.dumps(chunks), encoding="utf-8")
    return len(chunks)


def load_store(doc_dir: Path):
    index_path = doc_dir / "index.faiss"
    chunks_path = doc_dir / "chunks.json"
    if not index_path.is_file() or not chunks_path.is_file():
        raise ValueError("Document index files are missing")
    index = faiss.read_index(str(index_path))
    chunks = json.loads(chunks_path.read_text(encoding="utf-8"))
    return index, chunks


def retrieve_context(doc_dir: Path, question: str, k: int = 5) -> str:
    question = (question or "").strip()
    if not question:
        return ""
    model = get_embedder()
    q = model.encode([question], normalize_embeddings=True, show_progress_bar=False).astype("float32")
    index, chunks = load_store(doc_dir)
    k = min(k, len(chunks))
    if k < 1:
        return ""
    scores, idxs = index.search(q, k)
    picked = []
    for i in idxs[0]:
        if 0 <= i < len(chunks):
            picked.append(chunks[i])
    return "\n\n".join(picked)
