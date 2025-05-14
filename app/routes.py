# Defines Flask routes for file upload (/upload), question answering (/ask), and serving static files.
# Handles file saving, text extraction, and API communication.

from flask import Blueprint, send_from_directory, jsonify, request
import os
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from .pdf_handler import extract_text
from .openai_handler import answer_question
from .text_comparator import compare_texts
from .utils import get_weather_data, get_llm_response, handle_general_question, perform_duckduckgo_search, analyze_document_content

main = Blueprint('main', __name__)

scheduler = BackgroundScheduler()
scheduler.start()

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
    file = request.files.get('file')
    if not file:
        return jsonify({"status": "error", "message": "No file uploaded."})

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    return jsonify({"status": "success", "file_path": file_path})

@main.route('/ask', methods=['POST'])
def ask():
    """
    Handles user questions about the uploaded document and integrates risk detection.
    """
    data = request.get_json()
    question = data.get('question')
    file_path = data.get('file_path')  # Path to the uploaded document

    if not question:
        return jsonify({"status": "error", "message": "No question provided."})

    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No document uploaded or file not found."})

    try:
        # Extract text from the uploaded document
        file_extension = file_path.split('.')[-1].lower()
        text = extract_text(file_path, file_extension)

        # Answer the user's question using the document content
        context = text
        answer = answer_question(context, question)

        # Prepare a follow-up prompt for risk detection
        follow_up_prompt = (
            "Should I tell you about risks in your resume? "
            "Click on Yes, and I will provide you with the risk factors. "
            "If you click No, I recommend checking the risk factors of your resume."
        )

        return jsonify({
            "status": "success",
            "answer": answer,
            "follow_up_prompt": follow_up_prompt
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

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

@main.route('/set-reminder', methods=['POST'])
def set_reminder():
    data = request.get_json()
    task = data.get('task')
    reminder_time = data.get('time')
    email = data.get('email')

    def send_email():
        sender_email = "ksathvikf@gmail.com"
        sender_password = "mrmo hagv tbjq jlwu "
        recipient_email = email
        subject = "Reminder Notification"
        body = f"Reminder: {task}"

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

    reminder_datetime = datetime.strptime(reminder_time, "%Y-%m-%dT%H:%M")
    scheduler.add_job(send_email, 'date', run_date=reminder_datetime)

    return jsonify({"message": "Reminder set successfully!"})

@main.route('/read-news', methods=['GET'])
def read_news():
    news = perform_duckduckgo_search("latest news")
    return jsonify({"articles": [news]})

@main.route('/analyze-document', methods=['POST'])
def analyze_document():
    """
    Analyze uploaded documents for risks, inconsistencies, and areas of improvement.
    """
    file = request.files.get('file')
    if not file:
        return jsonify({"status": "error", "message": "No file uploaded."})

    # Save the uploaded file
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Determine the file type
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in ["pdf", "docx", "pptx"]:
        return jsonify({"status": "error", "message": "Unsupported file type."})

    try:
        # Extract text from the document
        text = extract_text(file_path, file_extension)

        # Analyze the document using the LLM
        analysis = analyze_document_content(text)

        # Return the analysis results
        return jsonify({"status": "success", "analysis": analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@main.route('/detect-risks', methods=['POST'])
def detect_risks():
    """
    Handles risk detection for the uploaded document.
    """
    data = request.get_json()
    file_path = data.get('file_path')  # Path to the uploaded document

    if not file_path or not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "No document uploaded or file not found."})

    try:
        # Extract text from the uploaded document
        file_extension = file_path.split('.')[-1].lower()
        text = extract_text(file_path, file_extension)

        # Analyze the document for risks
        analysis = analyze_document_content(text)

        return jsonify({"status": "success", "analysis": analysis})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})