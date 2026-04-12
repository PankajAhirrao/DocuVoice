import os
import shutil
import tempfile
import uuid
from pathlib import Path

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from pdf_qa.services import rag, stt, tts
from pdf_qa.services.ollama_client import generate_answer


def _doc_dir(doc_id: str) -> Path:
    return Path(settings.MEDIA_ROOT) / "pdf_qa" / doc_id


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upload_pdf(request):
    f = request.FILES.get("pdf")
    if not f or not str(f.name).lower().endswith(".pdf"):
        return JsonResponse({"error": "pdf file required"}, status=400)
    doc_id = str(uuid.uuid4())
    d = _doc_dir(doc_id)
    d.mkdir(parents=True, exist_ok=True)
    dest = d / "source.pdf"
    with open(dest, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)
    try:
        text = rag.extract_pdf_text(dest)
        n = rag.build_store(d, text)
    except Exception as e:
        shutil.rmtree(d, ignore_errors=True)
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"document_id": doc_id, "chunks": n})


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def ask_question(request):
    doc_id = request.data.get("document_id")
    if not doc_id:
        return JsonResponse({"error": "document_id required"}, status=400)
    d = _doc_dir(str(doc_id))
    if not (d / "index.faiss").is_file():
        return JsonResponse({"error": "unknown document_id"}, status=404)

    question = (request.data.get("question") or "").strip()
    audio = request.FILES.get("audio")
    if audio and not question:
        suffix = Path(audio.name).suffix or ".webm"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            for chunk in audio.chunks():
                tmp.write(chunk)
            tmp.close()
            question = stt.transcribe(tmp.name)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass

    if not question:
        return JsonResponse({"error": "question or audio required"}, status=400)

    try:
        context = rag.retrieve_context(d, question)
        answer = generate_answer(context, question)
        audio_rel = f"pdf_qa/{doc_id}/answer.wav"
        audio_path = Path(settings.MEDIA_ROOT) / audio_rel
        tts.synthesize_wav(answer[:8000], audio_path)
    except requests.RequestException as e:
        return JsonResponse({"error": f"Ollama error: {e}"}, status=503)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    audio_url = request.build_absolute_uri(settings.MEDIA_URL + audio_rel)
    return JsonResponse(
        {"answer": answer, "audio_url": audio_url, "question_used": question}
    )
