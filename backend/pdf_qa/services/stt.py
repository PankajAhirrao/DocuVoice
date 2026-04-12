import os
import tempfile
from pathlib import Path


def transcribe(audio_path: str | Path) -> str:
    path = Path(audio_path)
    vosk_dir = os.environ.get("VOSK_MODEL_PATH", "").strip()
    if vosk_dir and Path(vosk_dir).is_dir():
        return _transcribe_vosk(path, vosk_dir)
    return _transcribe_whisper(path)


def _transcribe_whisper(path: Path) -> str:
    from faster_whisper import WhisperModel

    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(path), language="en")
    return " ".join(s.text for s in segments).strip()


def _transcribe_vosk(path: Path, model_dir: str) -> str:
    import json
    import wave

    from pydub import AudioSegment
    from vosk import KaldiRecognizer, Model

    wav_fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(wav_fd)
    try:
        seg = AudioSegment.from_file(str(path))
        seg = seg.set_channels(1).set_frame_rate(16000)
        seg.export(wav_path, format="wav")
        wf = wave.open(wav_path, "rb")
        try:
            model = Model(model_dir)
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(False)
            text_parts = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    j = json.loads(rec.Result())
                    if j.get("text"):
                        text_parts.append(j["text"])
            j = json.loads(rec.FinalResult())
            if j.get("text"):
                text_parts.append(j["text"])
        finally:
            wf.close()
        return " ".join(text_parts).strip()
    finally:
        try:
            os.unlink(wav_path)
        except OSError:
            pass
