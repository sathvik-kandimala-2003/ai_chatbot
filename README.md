# Document QA Chatbot

This project is a Document Question Answering Chatbot built using Flask and OpenAI's GPT-3. It allows users to upload PDF documents, extract text from them, and ask questions related to the content of the documents.

## Project Structure

```
project_root/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── utils.py
│   ├── openai_handler.py
│   └── pdf_handler.py
├── uploads/
│   └── (Uploaded PDF files will be stored here)
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── .env
├── requirements.txt
├── app.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd project_root
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

3. Upload a PDF document using the provided interface.

4. Type your question in the textarea and click "Ask" to get answers based on the uploaded document.

## Features

- Upload PDF documents and extract text.
- Ask questions related to the content of the documents.
- Interactive web interface for user-friendly experience.

## License

This project is licensed under the MIT License.#   a i _ c h a t b o t  
 #   c h a t b o t _ f u l l  
 