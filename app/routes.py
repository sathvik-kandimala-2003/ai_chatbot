# Defines Flask routes for file upload (/upload) and question answering (/ask).
# Handles file saving, text extraction, and API communication.


from flask import Blueprint, render_template, request, jsonify
import os

from .openai_handler import answer_question
from .pdf_handler import extract_text

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

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