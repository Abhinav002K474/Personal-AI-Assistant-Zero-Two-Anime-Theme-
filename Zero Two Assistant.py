import sounddevice as sd
import numpy as np
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import requests
import tempfile
import soundfile as sf
import base64
from gtts import gTTS
import pygame
import pyttsx3

try:
    pygame.mixer.init()
except Exception:
    pass

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if "Zira" in voice.name or "Female" in voice.name:
            engine.setProperty('voice', voice.id)
            break
except Exception:
    engine = None

from dotenv import load_dotenv
load_dotenv()

# ------------------- API KEYS -------------------
OPENAI_API_KEY = os.environ.get("GEMINI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "")
ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

# ------------------- SPOTIFY API -------------------
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

SPOTIFY_TOKEN = None

def get_spotify_token():
    global SPOTIFY_TOKEN
    if SPOTIFY_TOKEN:
        return SPOTIFY_TOKEN
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    data = {"grant_type": "client_credentials"}
    response = requests.post(auth_url, headers=headers, data=data, timeout=10)
    if response.status_code == 200:
        SPOTIFY_TOKEN = response.json()["access_token"]
        return SPOTIFY_TOKEN
    else:
        print("Spotify Auth Error:", response.text)
        return None

def search_spotify_track(track_name):
    token = get_spotify_token()
    if not token:
        return None
    url = f"https://api.spotify.com/v1/search?q={track_name}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=10).json()
    tracks = response.get("tracks", {}).get("items", [])
    if tracks:
        track_url = tracks[0]["external_urls"]["spotify"]
        track_name = tracks[0]["name"]
        artist = tracks[0]["artists"][0]["name"]
        return f"{track_name} by {artist}", track_url
    return None, None

# ------------------- SPEAK FUNCTION (Hybrid) -------------------
def speak_local(text):
    print("Zero Two (Local):", text)
    if engine:
        engine.say(text)
        engine.runAndWait()

def speak_google(text):
    print("Zero Two (Google):", text)
    try:
        tts = gTTS(text=text, lang='en')
        file = "voice_google.mp3"
        tts.save(file)
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except Exception as e:
        print("Google TTS Error:", e)
        speak_local(text)

def speak_elevenlabs(text):
    print("Zero Two (ElevenLabs):", text)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "voice_settings": {"stability": 0.6, "similarity_boost": 0.85}}
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code != 200:
            raise Exception(response.text)
            
        file = "voice_elevenlabs.mp3"
        with open(file, "wb") as f:
            f.write(response.content)
            
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    except Exception as e:
        raise e

def speak(text, mode="eleven"):
    if mode == "google":
        speak_google(text)
    elif mode == "local":
        speak_local(text)
    else:
        try:
            speak_elevenlabs(text)
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}. Falling back to Google TTS.")
            speak_google(text)

# ------------------- SPEECH INPUT -------------------
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
        return None

# ------------------- GREETING -------------------
def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning Abhinav!")
    elif 12 <= hour < 18:
        speak("Good Afternoon Abhinav!")
    else:
        speak("Good Evening Abhinav!")
    speak("I am Zero Two. How can I help you?")

# ------------------- CHAT GPT -------------------
def chat_with_gpt(prompt):
    try:
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are Zero Two, a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------- GENERAL NEWS -------------------
def get_news():
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url, timeout=10).json()
        articles = response.get("articles", [])
        return [a["title"] for a in articles[:5]] if articles else ["No news found."]
    except:
        return ["Error fetching news."]

# ------------------- ANIME NEWS -------------------
def get_anime_news(anime_name):
    try:
        search_url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        search_response = requests.get(search_url, timeout=10).json()
        if not search_response.get("data"):
            return [f"Could not find anime: {anime_name}"]
        anime_id = search_response["data"][0]["mal_id"]
        news_url = f"https://api.jikan.moe/v4/anime/{anime_id}/news"
        news_response = requests.get(news_url, timeout=10).json()
        articles = news_response.get("data", [])
        return [a["title"] for a in articles[:5]] if articles else [f"No recent news for {anime_name}."]
    except:
        return ["Error fetching anime news."]

# ------------------- OPEN APPS -------------------
def open_app(app_name):
    user_path = os.path.expanduser("~")
    if "discord" in app_name:
        speak("Opening Discord...")
        discord_path = os.path.join(user_path, "AppData", "Local", "Discord", "Update.exe")
        if os.path.exists(discord_path):
            os.system(f'"{discord_path}" --processStart Discord.exe')
        else:
            webbrowser.open("https://discord.com")
    elif "whatsapp" in app_name:
        speak("Opening WhatsApp...")
        whatsapp_path = os.path.join(user_path, "AppData", "Local", "WhatsApp", "WhatsApp.exe")
        if os.path.exists(whatsapp_path):
            os.startfile(whatsapp_path)
        else:
            webbrowser.open("https://web.whatsapp.com/")
    elif "drive" in app_name:
        speak("Opening Google Drive...")
        webbrowser.open("https://drive.google.com")
    elif "linkedin" in app_name:
        speak("Opening LinkedIn...")
        webbrowser.open("https://linkedin.com")
    elif "photos" in app_name:
        speak("Opening Photos...")
        photos_path = os.path.join(user_path, "Pictures")
        if os.path.exists(photos_path):
            os.startfile(photos_path)
        else:
            speak("Photos folder not found.")
    elif "google" in app_name:
        speak("Opening Google...")
        webbrowser.open("https://google.com")
    elif "youtube" in app_name:
        speak("Opening YouTube...")
        webbrowser.open("https://youtube.com")
    else:
        speak(f"App {app_name} not recognized.")

# ------------------- MAIN LOOP -------------------
def main():
    wish_me()
    while True:
        query = take_command()
        if not query:
            continue

        if "wikipedia" in query:
            speak("Searching Wikipedia...")
            try:
                query_clean = query.replace("wikipedia", "").strip()
                results = wikipedia.summary(query_clean, sentences=2)
                speak("According to Wikipedia")
                speak(results)
            except:
                speak("Sorry, I could not find anything on Wikipedia.")

        # ------------------- FIXED YOUTUBE SEARCH -------------------
        elif "youtube" in query and "search" in query:
            search_term = query.replace("youtube", "").replace("search", "").strip()
            if search_term == "":
                speak("What do you want me to search on YouTube?")
            else:
                speak(f"Searching YouTube for {search_term}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")

        elif "news" in query or "headlines" in query:
            speak("Fetching the latest news...")
            headlines = get_news()
            speak("Here are the top headlines.")
            speak(". ".join(headlines))

        elif "anime news" in query:
            anime_name = query.replace("anime news", "").strip()
            if anime_name == "":
                speak("Which anime do you want news about?")
            else:
                speak(f"Fetching latest news for {anime_name}")
                headlines = get_anime_news(anime_name)
                speak(f"Here is the anime news for {anime_name}.")
                speak(". ".join(headlines))

        elif "play" in query and "spotify" in query:
            track_name = query.replace("play", "").replace("on spotify", "").strip()
            if track_name:
                track_info, track_url = search_spotify_track(track_name)
                if track_url:
                    speak(f"Playing {track_info} on Spotify")
                    webbrowser.open(track_url)
                else:
                    speak(f"Could not find {track_name} on Spotify")
            else:
                speak("Please tell me which song to play on Spotify")

        elif "chat" in query:
            query_clean = query.replace("chat", "").strip()
            reply = chat_with_gpt(query_clean)
            speak(reply)

        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"The time is {strTime}")

        elif "open" in query:
            app_name = query.replace("open", "").strip()
            open_app(app_name)

        # ------------------- SAYONARA EXIT -------------------
        elif "sayonara" in query:
            speak("Sayonara Abhinav, shutting down Zero Two.")
            speak("Sayonara")
            break

        else:
            speak("Sorry, I did not understand that.")

if __name__ == "__main__":
    main()
