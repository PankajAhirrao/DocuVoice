"""
Prepare a fully offline IEEE analysis model.

Run this ONCE while you still have internet:

    cd backend
    .venv\Scripts\python.exe prepare_offline_model.py

It will download a small FLAN‑T5 model from Hugging Face and save it
under backend/models/ieee-flan-t5-small so that future runs do NOT
need network access, even on first startup.
"""
from pathlib import Path

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


def main() -> None:
    root = Path(__file__).resolve().parent
    model_dir = root / "models" / "ieee-flan-t5-small"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_name = "google/flan-t5-small"
    print(f"Downloading {model_name} to {model_dir} ...")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    tokenizer.save_pretrained(model_dir)
    model.save_pretrained(model_dir)

    print("Done. Model is now stored locally for fully offline use.")


if __name__ == "__main__":
    main()

