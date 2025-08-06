from flask import Flask, request, jsonify
import whisper
import os
import wave
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = whisper.load_model("base")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files["audio"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        with wave.open(filepath, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
    except:
        duration = 0

    try:
        result = model.transcribe(filepath)
        transcript = result["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


    word_count = len(transcript.split())
    wpm = word_count / (duration / 60) if duration > 0 else 0

    grammar_score = 4.1 
    fluency_score = 3.8 

    return jsonify({
        "transcript": transcript,
        "duration": round(duration, 2),
        "word_count": word_count,
        "wpm": round(wpm, 2),
        "grammar_score": grammar_score,
        "fluency_score": fluency_score
    })

if __name__ == "__main__":
    app.run(debug=True)
