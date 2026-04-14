import requests


def generate_answer(context: str, question: str) -> str:
    context = context or ""
    question = (question or "").strip()
    if not question:
        raise ValueError("question is required")

    prompt = (
        "You answer strictly from the provided context. If the context does not contain the answer, "
        'reply exactly: "I cannot find this information in the document."\n\n'
        f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
    }
    print(f"[ollama.generate_answer] request_prompt_length={len(prompt)}")
    r = requests.post(
        url,
        json=payload,
        timeout=180,
    )
    r.raise_for_status()
    data = r.json() if r.content else {}
    print(f"[ollama.generate_answer] response_json={data}")
    return (data.get("response", "") or "").strip()
