import whisper
import os

# Load model once at module level or lazily
# Using "base" model for balance of speed and accuracy
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading Whisper model (base)... please wait.")
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio file to text using Whisper.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not available at {file_path}")

    model = get_model()
    result = model.transcribe(file_path)
    return result["text"].strip()
