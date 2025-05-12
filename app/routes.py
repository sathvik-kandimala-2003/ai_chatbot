# Defines Flask routes for file upload (/upload), question answering (/ask), and serving static files.
# Handles file saving, text extraction, and API communication.

from flask import Blueprint, send_from_directory, jsonify, request
import os

from .pdf_handler import extract_text
from .openai_handler import answer_question
from .text_comparator import compare_texts
from .utils import get_weather_data, get_llm_response, handle_general_question, handle_general_question

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return send_from_directory('frontend', 'index.html')  # Corrected path

@main.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('frontend/css', filename)  # Corrected path

@main.route('/js/<path:filename>')
def js(filename):
    return send_from_directory('frontend/js', filename)  # Corrected path

@main.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filepath = os.path.join('uploads', file.filename)
        file.save(filepath)
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension in ["pdf", "docx", "pptx"]:
            try:
                text = extract_text(filepath, file_extension)
                return jsonify({"status": "success", "text": text})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
        else:
            return jsonify({"status": "error", "message": "Unsupported file type"})
    return jsonify({"status": "error", "message": "No file uploaded"})

@main.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    context = data['context']
    question = data['question']
    answer = answer_question(context, question)
    return jsonify({"answer": answer})

@main.route('/compare', methods=['POST'])
def compare():
    first_doc = request.files.get('firstDoc')
    second_doc = request.files.get('secondDoc')

    if not first_doc or not second_doc:
        return jsonify({"status": "error", "message": "Both documents are required!"})

    first_path = os.path.join('uploads', first_doc.filename)
    second_path = os.path.join('uploads', second_doc.filename)

    first_doc.save(first_path)
    second_doc.save(second_path)

    # Extract text from both documents
    first_text = extract_text(first_path, first_doc.filename.split('.')[-1].lower())
    second_text = extract_text(second_path, second_doc.filename.split('.')[-1].lower())

    # Compare the documents
    similarities, differences = compare_texts(first_text, second_text)

    # Separate differences into 1st and 2nd document
    first_doc_differences = [line for line in differences if line in first_text.splitlines()]
    second_doc_differences = [line for line in differences if line in second_text.splitlines()]

    return jsonify({
        "status": "success",
        "similarities": similarities,
        "differences": {
            "firstDoc": first_doc_differences,
            "secondDoc": second_doc_differences
        }
    })

@main.route('/transcribe', methods=['POST'])
def transcribe_audio():
    audio_file = request.files.get('audio')

    if not audio_file:
        return jsonify({"status": "error", "message": "No audio file provided."})

    # Save the audio file temporarily
    audio_path = os.path.join('uploads', 'temp_audio.webm')
    audio_file.save(audio_path)

    if not os.path.exists(audio_path):
        return jsonify({"status": "error", "message": "Audio file not saved correctly."})

    try:
        # Use Whisper to transcribe the audio
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcription = result['text']

        return jsonify({"status": "success", "transcription": transcription})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        # Clean up the temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

last_response = None  # Store the last response globally

@main.route('/general-question', methods=['POST'])
def general_question():
    global last_response
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"status": "error", "message": "No question provided."})

    try:
        # Use the updated handler for general questions
        answer = handle_general_question(question, last_response)
        last_response = answer  # Update the last response
        return jsonify({"status": "success", "answer": answer})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@main.route('/ask-anything')
def ask_anything():
    return send_from_directory('frontend', 'ask_anything.html')