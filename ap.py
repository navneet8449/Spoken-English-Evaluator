from flask import Flask, request, jsonify
import whisper
import tempfile
import os

app = Flask(__name__)

model = whisper.load_model("base")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        audio_file.save(temp_audio.name)
        result = model.transcribe(temp_audio.name)
        os.remove(temp_audio.name)

    transcript = result["text"]
    duration = result["segments"][-1]["end"] if result["segments"] else 1.0
    word_count = len(transcript.split())
    wpm = word_count / (duration / 60)

    return jsonify({
        "transcript": transcript,
        "duration": duration,
        "word_count": word_count,
        "wpm": wpm
    })

if __name__ == '__main__':
    app.run(debug=True)
