const waveContainer = document.getElementById('wave-container');
const chatContainer = document.getElementById('chat');
const micBtn = document.getElementById('mic-btn');
const statusIndicator = document.getElementById('status-indicator');

// ⚠️ CHANGE THIS URL TO YOUR RENDER APP URL AFTER DEPLOYING ⚠️
const BACKEND_URL = "https://your-app.onrender.com";

const DOMPurifyHelpers = {
    escapeHTML: function(str) {
        let div = document.createElement('div');
        div.innerText = str;
        return div.innerHTML;
    }
};

let isSpeaking = false;
let currentModel = null;
let currentAudio = null;
let hasGreeted = false;
let isAssistantActive = false; // Controls the continuous listening loop

// ============== SPEECH / CHAT SETUP ============== //
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
let isListening = false;
let listeningTimeout = null;

// Character Image Animation Trigger
const characterImg = document.getElementById('character-img');
function updateCharacterImage() {
    if (!characterImg) return;
    if (isSpeaking) {
        characterImg.src = TALK_IMG;
        characterImg.classList.add("talking");
    } else {
        characterImg.src = IDLE_IMG;
        characterImg.classList.remove("talking");
    }
}

function handleNoSpeech() {
    console.warn("No speech detected.");
    statusIndicator.innerText = "Didn't catch that!";
    addMessage("Darling... I didn't catch that. Try again?", 'Zero Two', 'dar-msg');
    
    fetch(`${BACKEND_URL}/no_speech`)
        .then(res => res.json())
        .then(data => {
            if (data.audio) {
                playElevenLabsAudio(data.audio);
            } else {
                speakTextFallback(data.response);
            }
        }).catch(e => console.error("No Speech fallback error:", e));
}

function startListening() {
    if (!SpeechRecognition) {
        alert("Your browser does not support Speech Recognition. Use Chrome.");
        return;
    }

    if (isListening && recognition) {
        console.log("🛑 Stopping Assistant");
        isListening = false;
        try { recognition.stop(); } catch(e) {}
        micBtn.classList.remove('active');
        statusIndicator.innerText = "Waiting for command...";
        statusIndicator.classList.remove('listening');
        return;
    }

    if (currentAudio) {
        currentAudio.pause();
        isSpeaking = false;
        waveContainer.classList.add('hidden');
    }

    if (!recognition) {
        recognition = new SpeechRecognition();
        recognition.lang = "en-IN";
        recognition.continuous = true;
        recognition.interimResults = true;

        let lastCommand = "";
        let lastTime = 0;
        let silenceTimer = null;

        recognition.onstart = () => {
            console.log("🎤 Assistant started");
            micBtn.classList.add('active');
            statusIndicator.innerText = "Listening... ^_^";
            statusIndicator.classList.add('listening');
        };

        recognition.onresult = function(event) {
            let result = event.results[event.results.length - 1];

            // ❌ Ignore interim partial results entirely to prevent duplicate firing
            if (!result.isFinal) return;

            let text = result[0].transcript.toLowerCase().trim();
            let confidence = result[0].confidence;
            
            // Clean up stuttering native bugs
            text = text.replace(/open open/g, "open");

            if (confidence < 0.3) {
                 console.log("Low confidence, ignoring...");
                 return;
            }

            let now = Date.now();
            // ❌ Ignore exact duplicate phrases fired within 3 seconds of each other
            if (text === lastCommand && (now - lastTime < 3000)) {
                console.log("⚠️ Duplicate ignored:", text);
                return;
            }

            lastCommand = text;
            lastTime = now;

            console.log("🗣 You said:", text);
            addMessage(text, 'User', 'user-msg');

            // 🛑 STOP COMMAND
            if (text.includes("bye zero two") || text.includes("sayonara")) {
                isListening = false;
                statusIndicator.innerText = "Stopped";
                statusIndicator.classList.remove('listening');
                micBtn.classList.remove('active');
                sendCommand("sayonara");
                return;
            }

            // ✅ send to backend
            try { recognition.stop(); } catch(e) {}
            
            statusIndicator.innerText = "Thinking...";
            statusIndicator.classList.remove('listening');
            micBtn.classList.remove('active');
            sendCommand(text);
        };

        recognition.onerror = function(event) {
            console.error("❌ Error:", event.error);
            if (event.error === "not-allowed" || event.error === "audio-capture") {
                isListening = false;
                statusIndicator.innerText = "Microphone access denied or error! " + event.error;
                statusIndicator.classList.remove('listening');
                micBtn.classList.remove('active');
            }
        };

        recognition.onend = () => {
            console.log("🔁 Recognition stopped.");
            if (isListening && !isSpeaking && statusIndicator.innerText !== "Thinking...") {
                console.log("🔥 KEEP ALIVE triggered");
                try { recognition.start(); } catch(e) {}
            } else if (!isListening && statusIndicator.innerText !== "Thinking...") {
                micBtn.classList.remove('active');
                statusIndicator.innerText = "Waiting for command...";
                statusIndicator.classList.remove('listening');
            }
        };
    }

    isListening = true;

    if (!hasGreeted) {
        hasGreeted = true;
        micBtn.classList.add('active');
        statusIndicator.innerText = "Greeting...";
        fetch(`${BACKEND_URL}/greet`)
            .then(res => res.json())
            .then(data => {
                addMessage(data.response, 'Zero Two', 'dar-msg');
                if (data.audio) {
                    playElevenLabsAudio(data.audio);
                    const originalOnEnded = currentAudio.onended;
                    currentAudio.onended = () => {
                        if (originalOnEnded) originalOnEnded();
                        if (isListening) { try { recognition.start(); } catch(e) {} }
                    };
                } else {
                    speakTextFallback(data.response, () => {
                        if (isListening) { try { recognition.start(); } catch(e) {} }
                    });
                }
            }).catch(e => {
                console.error("Failed to greet:", e);
                if (isListening) { try { recognition.start(); } catch(err) {} }
            });
    } else {
        try { recognition.start(); } catch(e) { console.error("Start error:", e); }
    }
}

async function sendCommand(text) {
    try {
        const res = await fetch(`${BACKEND_URL}/command`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({query: text})
        });

        const data = await res.json();
        addMessage(data.response, 'Zero Two', 'dar-msg');
        statusIndicator.innerText = "Waiting for command...";
        
        // Play ElevenLabs Audio if available
        if (data.audio) {
            console.log("Received ElevenLabs Audio base64 payload.");
            playElevenLabsAudio(data.audio);
        } else {
            console.warn("No ElevenLabs audio found. Falling back to browser SpeechSynthesis.");
            // Fallback to browser TTS if ElevenLabs fails
            speakTextFallback(data.response);
        }
        
        // Execute UI navigation / action payloads mapped from backend!
        if (data.action === "open_url" && data.url) {
            console.log("Navigating directly natively to:", data.url);
            window.open(data.url, "_blank");
        }
        
    } catch (error) {
        addMessage("Failed to connect to backend server.", "System", "dar-msg");
        statusIndicator.innerText = "Connection error.";
    }
}
function addMessage(text, sender, className) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    msgDiv.innerHTML = `<span class="sender">${sender}</span><p>${DOMPurifyHelpers.escapeHTML(text)}</p>`;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function playElevenLabsAudio(base64Data) {
    if (currentAudio) {
        currentAudio.pause();
    }
    
    currentAudio = new Audio("data:audio/mpeg;base64," + base64Data);
    
    currentAudio.onplay = () => {
        isSpeaking = true;
        waveContainer.classList.remove('hidden');
        updateCharacterImage();
    };
    
    currentAudio.onended = () => {
        isSpeaking = false;
        waveContainer.classList.add('hidden');
        updateCharacterImage();
        
        // When AI finishes speaking, natively reignite continuous listening!
        if (isListening && recognition) {
            try { 
                recognition.start(); 
            } catch(e) { 
                console.error("Critical Audio Restart Block:", e); 
                statusIndicator.innerText = "Browser actively blocked microphone restart!"; 
            }
        }
    };
    
    currentAudio.onerror = () => {
        console.error("Audio object error:", currentAudio.error);
        isSpeaking = false;
        waveContainer.classList.add('hidden');
        updateCharacterImage();
    };

    const playPromise = currentAudio.play();
    if (playPromise !== undefined) {
        playPromise.catch(error => {
            console.error("Autoplay prevents audio playback or similar error:", error);
            statusIndicator.innerText = "Browser prevented audio. Please click here to play a sound.";
        });
    }
}

// Fallback if ElevenLabs runs out of credits or has no key
// Fallback if ElevenLabs runs out of credits or has no key
function speakTextFallback(text, onEndCallback = null) {
    const synth = window.speechSynthesis;
    if (!synth) {
        if (onEndCallback) onEndCallback();
        return;
    }
    if (synth.speaking) synth.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    window.currentUtterance = utterance; // EXTREMELY CRITICAL: Prevents Chrome Garbage Collection bug!
    
    const voices = synth.getVoices();
    const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Zira") || v.name.includes("Google UK English Female"));
    if(femaleVoice) utterance.voice = femaleVoice;
    
    utterance.pitch = 1.2;
    utterance.rate = 1.05;
    
    // Safety Net: if browser completely silences the SpeechSynthesis engine, force proceed after 5 seconds to prevent soft-locks
    let fallbackTimeout = setTimeout(() => {
        isSpeaking = false;
        waveContainer.classList.add('hidden');
        if (onEndCallback) onEndCallback();
        onEndCallback = null; // Prevent double execution
    }, 5000);
    
    utterance.onstart = () => {
        isSpeaking = true;
        waveContainer.classList.remove('hidden');
        updateCharacterImage();
    };
    
    utterance.onend = () => {
        clearTimeout(fallbackTimeout);
        isSpeaking = false;
        waveContainer.classList.add('hidden');
        updateCharacterImage();
        if (onEndCallback) {
            onEndCallback();
            onEndCallback = null;
        }
        
        // Restart continuous loop natively after fallback TTS
        if (isListening && recognition) {
            try { recognition.start(); } catch(e) {}
        }
    };
    
    utterance.onerror = (e) => {
        console.error("Speech Synthesis Error", e);
        clearTimeout(fallbackTimeout);
        isSpeaking = false;
        waveContainer.classList.add('hidden');
        updateCharacterImage();
        if (onEndCallback) {
            onEndCallback();
            onEndCallback = null;
        }
    };

    synth.speak(utterance);
}

if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
  window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
}

// ==========================================
// RENDER FREE TIER COLD-START WAKE UP PING
// ==========================================
// Render's free tier sleeps after 15 mins. This triggers an immediate
// background request to wake it up silently when the Vercel site loads!
fetch(`${BACKEND_URL}/`).catch(e => console.log("Wake up ping sent"));
