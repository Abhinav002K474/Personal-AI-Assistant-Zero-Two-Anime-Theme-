# Personal-AI-Assistant-Zero-Two-Anime-Theme-
# 🤖 Zero Two – Python Voice Assistant

import sounddevice as sd
import numpy as np
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import tempfile
import soundfile as sf

ENVIRONMENT VARIABLES ==================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

 SAFE SPEAK FUNCTION ==================

def speak(text):
    """
    Offline-safe TTS placeholder.
    Replace with any TTS engine (pyttsx3, ElevenLabs, etc.)
    """
    print("Zero Two:", text)

 SPEECH INPUT ==================

def take_command(duration=8):
    r = sr.Recognizer()
    fs = 44100
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    audio_data = sr.AudioData(audio.tobytes(), fs, 2)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio_data, language="en-in")
        print(f"You said: {query}")
        return query.lower()
    except:
        return "none"

 GREETING ==================

def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning Abhinav!")
    elif hour < 18:
        speak("Good Afternoon Abhinav!")
    else:
        speak("Good Evening Abhinav!")
    speak("I am Zero Two. How can I help you?")

 CHAT PLACEHOLDER ==================


def chat_with_ai(prompt):
    """
    API-free placeholder.
    Replace with OpenAI, local LLM, or any chatbot engine.
    """
    return "Chat feature is disabled in public version."

 NEWS PLACEHOLDER ==================
def get_news():
    return [
        "News service is disabled in public version.",
        "Add your own API key to enable it."
    ]

 ANIME NEWS PLACEHOLDER ==================
def get_anime_news(anime_name):
    return [f"Anime news for {anime_name} is disabled in public version."]

 OPEN APPS ==================

ef open_app(app_name):
    user_path = os.path.expanduser("~")

    if "discord" in app_name:
        speak("Opening Discord...")
        webbrowser.open("https://discord.com")

    elif "whatsapp" in app_name:
        speak("Opening WhatsApp...")
        webbrowser.open("https://web.whatsapp.com")

    elif "drive" in app_name:
        speak("Opening Google Drive...")
        webbrowser.open("https://drive.google.com")

    elif "linkedin" in app_name:
        speak("Opening LinkedIn...")
        webbrowser.open("https://linkedin.com")

    elif "google" in app_name:
        speak("Opening Google...")
        webbrowser.open("https://google.com")

    elif "youtube" in app_name:
        speak("Opening YouTube...")
        webbrowser.open("https://youtube.com")

    else:
        speak("Application not recognized.")

 MAIN LOOP ==================
def main():
    wish_me()

    while True:
        query = take_command()

        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            try:
                topic = query.replace("wikipedia", "").strip()
                result = wikipedia.summary(topic, sentences=2)
                speak(result)
            except:
                speak("Could not find anything on Wikipedia.")

        elif "youtube search" in query:
            search_term = query.replace("youtube search", "").strip()
            speak(f"Searching YouTube for {search_term}")
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={search_term}"
            )

        elif "news" in query:
            for h in get_news():
                speak(h)

        elif "anime news" in query:
            anime = query.replace("anime news", "").strip()
            for h in get_anime_news(anime):
                speak(h)

        elif "chat" in query:
            reply = chat_with_ai(query.replace("chat", ""))
            speak(reply)

        elif "time" in query:
            time_now = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {time_now}")

        elif "open" in query:
            open_app(query.replace("open", "").strip())

        elif "sayonara" in query:
            speak("Sayonara Abhinav. Shutting down Zero Two.")
            break

        else:
            speak("Sorry, I did not understand that.")

# ================== ENTRY POINT ==================
if __name__ == "__main__":
    main()
