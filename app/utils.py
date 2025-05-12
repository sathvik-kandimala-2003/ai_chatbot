import os
import requests

def compare_texts(text1, text2):
    text1_lines = set(text1.splitlines())
    text2_lines = set(text2.splitlines())

    similarities = list(text1_lines & text2_lines)  # Common lines
    differences = list(text1_lines ^ text2_lines)  # Different lines

    return similarities, differences

def get_weather_data(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temp}°C."
    else:
        return "Unable to fetch weather data."

def get_llm_response(prompt):
    """
    Use the Gemini API for LLM-based responses.
    """
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        candidates = response.json().get("candidates", [])
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"].strip()
        else:
            return "No response found."
    else:
        return f"Error: {response.status_code}, {response.text}"

def perform_duckduckgo_search(query):
    """
    Perform a search using DuckDuckGo Instant Answer API.
    """
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract the abstract or related topics
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            return data["RelatedTopics"][0].get("Text", "No relevant information found.")
        else:
            return "No relevant information found."
    else:
        return f"Error fetching search results: {response.status_code}"

def handle_general_question(question, last_response=None):
    """
    Handle any general question using DuckDuckGo API for real-time data or Gemini API for reasoning.
    """
    # Keywords to determine if a real-time API should be used
    real_time_keywords = ["today", "latest", "real-time", "current", "news"]

    if any(keyword in question.lower() for keyword in real_time_keywords):
        # Use DuckDuckGo for real-time queries
        duckduckgo_response = perform_duckduckgo_search(question)
        if duckduckgo_response != "No relevant information found.":
            return duckduckgo_response
        else:
            # Fallback to Gemini if DuckDuckGo fails
            gemini_prompt = f"As of today, {question}. If you don't know, say so."
            gemini_response = get_llm_response(gemini_prompt)
            if "I don't know" in gemini_response or "no publicly available information" in gemini_response:
                return "I couldn't find any real-time information about this. Please check the latest news online."
            return gemini_response
    else:
        # Use Gemini API for other questions
        return get_llm_response(question)