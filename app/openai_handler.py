
# Sends the extracted text and user question to the Gemini API.
# Parses the API response to extract the answer.


import os
import requests

GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY

def answer_question(context, question):
    headers = {
        "Content-Type": "application/json"
    }
    # Update the payload structure based on the Gemini API documentation
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Context: {context}\n\nQuestion: {question}"}
                ]
            }
        ]
    }
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    print(response.text)
    if response.status_code == 200:
        # Extract the text from the response
        candidates = response.json().get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"].strip()
        else:
            return "No answer found in the response."
    else:
        return f"Error: {response.status_code}, {response.text}"