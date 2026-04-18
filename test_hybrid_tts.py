from gtts import gTTS
from playsound import playsound
import pyttsx3
import os
import requests
import tempfile
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv

load_dotenv()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Try to find a female voice
female_voice_found = False
for voice in voices:
    if "Zira" in voice.name or "Female" in voice.name:
        engine.setProperty('voice', voice.id)
        female_voice_found = True
        break
if not female_voice_found and len(voices) > 1:
    engine.setProperty('voice', voices[1].id)

def speak_local(text):
    print(f"[Local] {text}")
    engine.say(text)
    engine.runAndWait()

def speak_google(text):
    print(f"[Google] {text}")
    tts = gTTS(text=text, lang='en')
    file = "voice_google.mp3"
    tts.save(file)
    playsound(file)
    if os.path.exists(file):
        os.remove(file)

def speak_elevenlabs(text):
    print(f"[ElevenLabs] {text}")
    ELEVEN_VOICE_ID = os.getenv("ELEVEN_VOICE_ID")
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
    headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "voice_settings": {"stability": 0.6, "similarity_boost": 0.85}}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(response.content)
        temp_path = f.name
    data_audio, samplerate = sf.read(temp_path)
    sd.play(data_audio, samplerate)
    sd.wait()
    os.remove(temp_path)

def test_speak():
    try:
        speak_local("Testing local voice")
    except Exception as e:
        print("Local failed:", e)
        
    try:
        speak_google("Testing Google voice")
    except Exception as e:
        print("Google failed:", e)

    try:
        speak_elevenlabs("Testing Eleven Labs voice")
    except Exception as e:
        print("ElevenLabs failed:", e)

if __name__ == "__main__":
    test_speak()
