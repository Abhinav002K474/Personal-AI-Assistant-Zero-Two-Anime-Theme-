# Personal AI Assistant - Zero Two (Anime Theme)

A fully functional, voice-interactive personal AI assistant featuring a Zero Two (anime) aesthetic and personality. This application contains a frontend web interface equipped with real-time visual feedback and a robust backend Python capability that handles speech synthesis, recognition, artificial intelligence text generation, and dynamic web searching. 

## Features

- **Dynamic Interactive UI:** A premium black/red-themed interface displaying Zero Two.
- **Voice Recognition & Speech:** Talk to your assistant naturally. It uses specialized Text-to-Speech (Google TTS / ElevenLabs) to respond.
- **AI Backend:** Powered by Gemini AI for contextual, intelligent responses.
- **System Integration:** Can open websites, control music via Spotify, fetch news, and scrape Wikipedia summaries.
- **Micro-Animations:** Beautiful visualizers dynamically responding to your interactions.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- A modern Web Browser (Chrome/Edge recommended)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Abhinav002K474/Personal-AI-Assistant-Zero-Two-Anime-Theme-.git
cd Personal-AI-Assistant-Zero-Two-Anime-Theme-
```

2. Install the required Python packages:
```bash
pip install flask python-dotenv sounddevice numpy SpeechRecognition wikipedia soundfile gTTS pygame-ce pyttsx3
```

3. Setup your Environment Variables.
Create a new file called `.env` in the root folder based on `.env.example` and populate it with your own API keys.
```bash
cp .env.example .env
```

## Running the Assistant

1. Start the Flask application backend:
```bash
python app.py
```
2. The server will start, typically on `http://127.0.0.1:5000/`. Visit this URL in your browser to access the assistant.

## Configuration & APIs

To get full functionality, you will need the following API keys:
- **Gemini AI API Key:** For the core intelligence.
- **ElevenLabs API Key:** (Optional) For high-quality, realistic character voices.
- **News API Key:** To fetch the latest world news.
- **Spotify API Keys:** To connect your music and control playback.

Enjoy your very own personal 02 assistant!
