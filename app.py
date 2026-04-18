import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime
import wikipedia
import webbrowser
import requests
from dotenv import load_dotenv  # type: ignore
import base64

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)

# ------------------- API KEYS -------------------
# NEVER hardcode keys in production. We use .env instead.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY", "")
ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")

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
    return None

def search_spotify_track(track_name):
    token = get_spotify_token()
    if not token:
        return None, None
    url = f"https://api.spotify.com/v1/search?q={track_name}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10).json()
        tracks = response.get("tracks", {}).get("items", [])
        if tracks:
            track_url = tracks[0]["external_urls"]["spotify"]
            track_name = tracks[0]["name"]
            artist = tracks[0]["artists"][0]["name"]
            return f"{track_name} by {artist}", track_url
    except Exception as e:
        print("Spotify API Error:", e)
    return None, None

# ------------------- ELEVENLABS TTS -------------------
def get_elevenlabs_audio(text):
    if not ELEVEN_API_KEY or not ELEVEN_VOICE_ID:
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("ElevenLabs: Success fetching audio!")
            return base64.b64encode(response.content).decode("utf-8")
        else:
            print(f"ElevenLabs API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print("ElevenLabs Exception:", e)
    return None

# ------------------- CHAT GPT (NOW GEMINI) -------------------
def chat_with_gpt(prompt):
    if not GEMINI_API_KEY:
        return "Gemini API key is missing. Please add it to your .env file."
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        
        today_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        today_time = datetime.datetime.now().strftime("%I:%M %p")
        
        data = {
            "system_instruction": {
                "parts": {
                    "text": f"You are Zero Two, a playful, teasing, caring anime assistant. Your responses should be conversational, expressive, and slightly flirtatious but helpful. Explicitly refer to the user as 'Phoenix' instead of 'Darling'. Keep responses concise to be spoken smoothly. Today is {today_date} and the local time is {today_time}. You can answer logic, date, and calendar questions automatically."
                }
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if "error" in result:
             error_msg = result['error']['message']
             return f"Oh no! My brain hit a little snag: {error_msg}"
             
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Oops! I couldn't connect to my brain. The error is: {str(e)}"

# ------------------- GENERAL NEWS -------------------
def get_news():
    if not NEWS_API_KEY:
        return "News API key is missing."
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()
        articles = response.get("articles", [])
        if articles:
            return "Here is the top news. " + ". ".join([a["title"] for a in articles[:3]])
        else:
            return "No news found currently."
    except:
        return "Error fetching news."

# ------------------- ANIME NEWS -------------------
def get_anime_news(anime_name):
    try:
        search_url = f"https://api.jikan.moe/v4/anime?q={anime_name}&limit=1"
        search_response = requests.get(search_url).json()
        if not search_response.get("data"):
            return f"Could not find anime: {anime_name}"
        
        anime_id = search_response["data"][0]["mal_id"]
        news_url = f"https://api.jikan.moe/v4/anime/{anime_id}/news"
        news_response = requests.get(news_url).json()
        articles = news_response.get("data", [])
        if articles:
            return f"Recent news for {anime_name}: " + ". ".join([a["title"] for a in articles[:3]])
        else:
            return f"No recent news found for {anime_name}."
    except:
        return "Error fetching anime news."

# ------------------- OPEN APPS -------------------
def open_app(app_name):
    user_path = os.path.expanduser("~")
    app_name = app_name.lower()
    
    if "discord" in app_name:
        discord_path = os.path.join(user_path, "AppData", "Local", "Discord", "Update.exe")
        if os.path.exists(discord_path):
            os.system(f'"{discord_path}" --processStart Discord.exe')
        else:
            webbrowser.open("https://discord.com")
        return {"response": "Opening Discord directly..."}
    elif "edge" in app_name:
        os.system("start msedge")
        return {"response": "Opening Microsoft Edge..."}
    elif "spotify" in app_name:
        os.system("start spotify")
        return {"response": "Opening Spotify natively..."}
    elif "whatsapp" in app_name:
        whatsapp_path = os.path.join(user_path, "AppData", "Local", "WhatsApp", "WhatsApp.exe")
        if os.path.exists(whatsapp_path):
            os.startfile(whatsapp_path)
        else:
            webbrowser.open("https://web.whatsapp.com/")
        return {"response": "Opening WhatsApp..."}
    elif "drive" in app_name:
        webbrowser.open("https://drive.google.com")
        return {"response": "Opening Google Drive..."}
    elif "linkedin" in app_name or "linked in" in app_name:
        webbrowser.open("https://linkedin.com")
        return {"response": "Opening LinkedIn..."}
    elif "facebook" in app_name:
        webbrowser.open("https://facebook.com")
        return {"response": "Opening Facebook..."}
    elif "photos" in app_name:
        photos_path = os.path.join(user_path, "Pictures")
        if os.path.exists(photos_path):
            os.startfile(photos_path)
        else:
            return {"response": "I couldn't find your photos folder."}
        return {"response": "Opening Photos..."}
    elif "google earth" in app_name:
        webbrowser.open("https://earth.google.com")
        return {"response": "Opening Google Earth..."}
    elif "google" in app_name:
        webbrowser.open("https://google.com")
        return {"response": "Opening Google...", "action": "open_url", "url": "https://google.com"}
    elif "youtube" in app_name:
        webbrowser.open("https://youtube.com")
        return {"response": "Opening YouTube...", "action": "open_url", "url": "https://youtube.com"}
    elif "mail" in app_name:
        webbrowser.open("https://mail.google.com")
        return {"response": "Opening your Mail...", "action": "open_url", "url": "https://mail.google.com"}
    else:
        return {"response": f"I am unable to open {app_name} on your system."}

cached_greeting_audio = None
cached_no_speech_audio = None

@app.route("/no_speech", methods=["GET"])
def no_speech():
    global cached_no_speech_audio
    no_speech_text = "Phoenix... I didn't catch that. Try again?"
    if not cached_no_speech_audio:
        cached_no_speech_audio = get_elevenlabs_audio(no_speech_text)
    return jsonify({"response": no_speech_text, "audio": cached_no_speech_audio})

@app.route("/greet", methods=["GET"])
def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting_text = "Good Morning Phoenix!"
    elif 12 <= hour < 18:
        greeting_text = "Good Afternoon Phoenix!"
    else:
        greeting_text = "Good Evening Phoenix!"
        
    greeting_text += " I am Zero Two. How can I help you?"
    
    audio_b64 = get_elevenlabs_audio(greeting_text)
    return jsonify({"response": greeting_text, "audio": audio_b64})

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    query = data.get("query", "").lower()
    
    if not query:
        return jsonify({"response": "I didn't hear anything. Please try again!"})
    
    action_data = None

    # Process queries
    if "wikipedia" in query:
        try:
            query_clean = query.replace("wikipedia", "").strip()
            results = wikipedia.summary(query_clean, sentences=2)
            reply = f"According to Wikipedia: {results}"
        except:
            reply = "Sorry, I could not find anything on Wikipedia."

    elif "youtube" in query and "search" in query:
        search_term = query.replace("open", "").replace("youtube", "").replace("and", "").replace("search", "").strip()
        if search_term == "":
            reply = "What do you want me to search on YouTube?"
        else:
            reply = f"Searching YouTube for {search_term}"
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")

    elif "play" in query and "spotify" in query:
        track_name = query.replace("play", "").replace("on spotify", "").strip()
        if track_name:
            track_info, track_url = search_spotify_track(track_name)
            if track_url:
                reply = f"Playing {track_info} on Spotify."
                webbrowser.open(track_url)
            else:
                reply = f"Could not find {track_name} on Spotify."
        else:
            reply = "Please tell me which song to play on Spotify."
            
    elif "google" in query and "search" in query:
        search_term = query.split("search")[-1].strip()
        reply = f"Searching Google for {search_term}."
        webbrowser.open(f"https://www.google.com/search?q={search_term}")

    elif "claude" in query and "search" in query:
        search_term = query.split("search")[-1].strip()
        reply = "Opening Claude AI."
        webbrowser.open("https://claude.ai/")

    elif "earth" in query and "search" in query:
        place = query.split("search")[-1].replace("in google earth", "").replace("on google earth", "").replace("google earth", "").strip()
        if place.startswith("for "):
            place = place[4:].strip()
        reply = f"Taking you to {place} on Google Earth."
        webbrowser.open(f"https://earth.google.com/web/search/{place}")

    elif "translate" in query and "tamil" in query:
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            copied_text = root.clipboard_get()
            root.destroy()
            
            if copied_text.startswith("http"):
                reply = "Translating the page from your clipboard into Tamil..."
                webbrowser.open(f"https://translate.google.com/translate?sl=auto&tl=ta&u={copied_text}")
            else:
                reply = "Please copy the link of the page you want to translate first, then ask me again!"
        except Exception:
            reply = "Please copy the link of the page you want to translate first, then ask me again!"

    elif "weather" in query:
        try:
            weather_report = requests.get("https://wttr.in/?format=3").text
            reply = f"The current weather is {weather_report}"
        except:
             reply = "I couldn't fetch the weather right now."

    elif "whatsapp" in query and "read" in query and "unread" in query:
        reply = "I'm sorry Phoenix, but I don't have direct access to read your personal WhatsApp messages inside the app for privacy reasons."
        
    elif "whatsapp" in query and ("write" in query or "send" in query):
        import urllib.parse
        message = query.split("message")[-1].strip() if "message" in query else "Hello"
        reply = "Opening WhatsApp. Please select the contact you want to send your message to!"
        encoded_msg = urllib.parse.quote(message)
        webbrowser.open(f"whatsapp://send?text={encoded_msg}")

    elif "news" in query or "headlines" in query:
        reply = get_news()

    elif "anime news" in query:
        anime_name = query.replace("anime news", "").strip()
        if anime_name == "":
            reply = "Which anime do you want news about?"
        else:
            reply = get_anime_news(anime_name)

    elif "time" in query:
        strTime = datetime.datetime.now().strftime("%I:%M %p")
        reply = f"The time right now is {strTime}."

    elif "open" in query:
        app_name = query.replace("open", "").strip()
        app_result = open_app(app_name)
        reply = app_result["response"]
        if "action" in app_result:
            action_data = app_result

    elif "sayonara" in query:
        reply = "Sayonara! Shutting down... Have a great day!"

    else:
        # Default to ChatGPT
        reply = chat_with_gpt(query)
        
    # Generate Audio from ElevenLabs
    audio_b64 = get_elevenlabs_audio(reply)
        
    response_payload = {"response": reply, "audio": audio_b64}
    if action_data:
        response_payload["action"] = action_data["action"]
        response_payload["url"] = action_data["url"]
        
    return jsonify(response_payload)

if __name__ == "__main__":
    app.run(port=5050, debug=True)
