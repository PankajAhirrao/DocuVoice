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
    print(f"[upload_pdf] incoming files: {list(request.FILES.keys())}")
    f = request.FILES.get("pdf")
    if not f or not str(f.name).lower().endswith(".pdf"):
        return JsonResponse({"success": False, "error": "pdf file required"}, status=400)
    print("File received:", f.name)
    doc_id = str(uuid.uuid4())
    d = _doc_dir(doc_id)
    d.mkdir(parents=True, exist_ok=True)
    dest = d / "source.pdf"
    with open(dest, "wb") as out:
        for chunk in f.chunks():
            out.write(chunk)
    try:
        text = rag.extract_pdf_text(dest)
        print("Extracted text length:", len(text or ""))
        if not (text or "").strip():
            raise ValueError("No extractable text found in PDF")
        n = rag.build_store(d, text)
        print(f"[upload_pdf] document_id={doc_id}, chunks={n}")
    except ValueError as e:
        print(f"[upload_pdf] bad input error: {e}")
        shutil.rmtree(d, ignore_errors=True)
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        print(f"[upload_pdf] unexpected error: {e}", flush=True)
        shutil.rmtree(d, ignore_errors=True)
        return JsonResponse({"success": False, "error": f"upload failed: {e}"}, status=500)
    return JsonResponse(
        {
            "success": True,
            "document_id": doc_id,
            "message": "PDF processed successfully",
            "chunks": n,
        }
    )


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def ask_question(request):
    print(f"[ask_question] incoming data keys: {list(request.data.keys())}")
    doc_id = request.data.get("document_id")
    doc_id = str(doc_id).strip() if doc_id is not None else ""
    if not doc_id:
        return JsonResponse({"success": False, "error": "document_id required"}, status=400)
    d = _doc_dir(str(doc_id))
    if not (d / "index.faiss").is_file():
        return JsonResponse({"success": False, "error": "unknown document_id"}, status=404)

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
        return JsonResponse({"success": False, "error": "question or audio required"}, status=400)

    try:
        context = rag.retrieve_context(d, question)
        print(f"[ask_question] context_length={len(context or '')}, question={question[:200]}")
        answer = generate_answer(context, question)
        print(f"[ask_question] answer_length={len(answer or '')}")
        audio_url = None
        try:
            audio_rel = f"pdf_qa/{doc_id}/answer.wav"
            audio_path = Path(settings.MEDIA_ROOT) / audio_rel
            tts.synthesize_wav((answer or "")[:8000], audio_path)
            audio_url = request.build_absolute_uri(settings.MEDIA_URL + audio_rel)
        except Exception as audio_err:
            print(f"[ask_question] tts error: {audio_err}")
    except requests.RequestException as e:
        print(f"[ask_question] ollama request error: {e}")
        return JsonResponse({"success": False, "error": f"Ollama error: {e}"}, status=500)
    except ValueError as e:
        print(f"[ask_question] bad input error: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        print(f"[ask_question] unexpected error: {e}", flush=True)
        return JsonResponse({"success": False, "error": f"ask failed: {e}"}, status=500)

    return JsonResponse(
        {
            "success": True,
            "answer": answer or "",
            "audio": audio_url,
            "audio_url": audio_url,
            "question_used": question,
        }
    )
