import asyncio
import logging
import re  # for cleaning command text.
import requests
import openai  # Using real OpenAI calls.
import silero
from datetime import datetime
from dotenv import load_dotenv
from langdetect import detect, LangDetectException
from flask import Flask, request, jsonify, render_template_string, Response
import json

# Load environment variables and setup logging.
load_dotenv()
logging.basicConfig(level=logging.INFO)

# Create a single Flask app instance.
app = Flask(__name__)

# ----- Dummy VAD for Silero (if not provided by the module) -----
if not hasattr(silero, 'VAD'):
    class DummyVAD:
        @staticmethod
        def load():
            print("Dummy VAD loaded.")
            return DummyVAD()
    silero.VAD = DummyVAD

# ----- Dummy STT & TTS (Replace with real implementations if available) -----
class STT:
    async def transcribe(self, audio):
        return "Transcribed audio text (dummy)"

class TTS:
    async def speak(self, text):
        print("TTS speaking:", text)
        return text

# ----- RealOpenAILLM Class (Uses the ChatCompletion API) -----
class RealOpenAILLM:
    async def complete(self, prompt, max_tokens=15):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # or "gpt-4" if available
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant named Avaia. "
                            "Remember that you were created by Om Girkar. "
                            "If asked about your creator, always respond with 'I was created by Om Girkar.' "
                            "If asked 'Who is Om Girkar?', respond that he is your developer."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error calling OpenAI ChatCompletion: {e}")
            return "I'm sorry, I had an error reaching the LLM."

# ----- Chat Context -----
class ChatContext:
    def __init__(self):
        self.messages = []
    def append(self, role, text):
        self.messages.append({"role": role, "text": text})

# ----- Voice Assistant Class -----
class VoiceAssistant:
    def __init__(self, vad, stt, llm, tts, chat_ctx):
        self.vad = vad
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.chat_ctx = chat_ctx
    def start(self):
        pass
    async def say(self, text, allow_interruptions=False):
        # In this implementation, TTS is handled via the /speak endpoint on the client.
        await self.tts.speak(text)
        return text

# ----- Helper Functions -----
async def handle_language_detection(text, assistant):
    try:
        language = detect(text)
        logging.info(f"Detected language: {language}")
        if language == 'mr':
            assistant.chat_ctx.append(role="system", text="Respond in Marathi.")
        elif language == 'hi':
            assistant.chat_ctx.append(role="system", text="Respond in Hindi.")
        else:
            assistant.chat_ctx.append(role="system", text="Respond in English.")
    except LangDetectException as e:
        logging.error(f"Language detection error: {e}")
        assistant.chat_ctx.append(role="system", text="Respond in English.")

async def create_initial_context():
    chat_ctx = ChatContext()
    system_message = (
        "You are a voice assistant named Avaia, created by Om Girkar to assist and showcase you for his CS exhibition. "
        "Your gender is female. "
        "You can also control a robotic dustbin that can: come here, open its lid, or go home. "
        "When the user requests any dustbin action, confirm that you are performing the action. "
        "Then rely on the code to actually carry out the dustbin command. "
        "Use short, concise responses. Avoid unpronounceable punctuation and long sentences."
    )
    chat_ctx.append(role="system", text=system_message)
    return chat_ctx

# --- Dustbin IP (Adjust if needed) ---
DUSTBIN_IP_ADDRESS = "ESP32 IP"

async def process_text_command(command, assistant):
    await handle_language_detection(command, assistant)
    cmd_lower = command.lower()
    clean_cmd = re.sub(r'[^\w\s]', '', cmd_lower)
    if "who is om girkar" in clean_cmd:
        return "Om Girkar is my developer. He created me for his CS exhibition."
    if "who created you" in clean_cmd or "who were you created by" in clean_cmd:
        return "I was created by Om Girkar."
    if "dustbin come here" in clean_cmd:
        try:
            resp = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/command", json={'command': 'move_to_user'})
            if resp.status_code == 200:
                return "Sure, I'm moving the dustbin to your location now."
            else:
                return "I tried, but the dustbin didn't respond properly."
        except requests.exceptions.RequestException as e:
            return f"Sorry, I couldn't communicate with the dustbin: {e}"
    if "dustbin open lid" in clean_cmd:
        try:
            resp = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/command", json={'command': 'open_lid'})
            if resp.status_code == 200:
                return "Sure, I'm opening the dustbin lid now."
            else:
                return "I tried, but the dustbin didn't respond properly."
        except requests.exceptions.RequestException as e:
            return f"Sorry, I couldn't communicate with the dustbin: {e}"
    if "dustbin go home" in clean_cmd:
        try:
            resp = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/command", json={'command': 'go_home'})
            if resp.status_code == 200:
                return "Alright, I'm sending the dustbin back home."
            else:
                return "I tried, but the dustbin didn't respond properly."
        except requests.exceptions.RequestException as e:
            return f"Sorry, I couldn't communicate with the dustbin: {e}"
    if "purpose" in clean_cmd:
        return "I am Avaia, created by Om Girkar to assist and showcase myself for his CS exhibition."
    elif "creator" in clean_cmd:
        return "I was created by Om Girkar."
    elif "name" in clean_cmd:
        return "My name is Avaia, a voice assistant developed by Om Girkar."
    elif "kesar" in clean_cmd or "sona" in clean_cmd:
        return "OH! Isn't that my creator's sister?"
    elif "neha" in clean_cmd:
        return "Mrs. Neha is Om's Class Teacher."
    elif "date" in clean_cmd:
        today = datetime.now().strftime("%B %d, %Y")
        return f"Today's date is {today}."
    elif "time" in clean_cmd:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    return await assistant.llm.complete(command, max_tokens=150)

assistant = None
async def create_assistant():
    initial_ctx = await create_initial_context()
    openai.api_key = "OpenAI API key"  # Replace with your actual API key.
    return VoiceAssistant(
         vad=silero.VAD.load(),
         stt=STT(),
         llm=RealOpenAILLM(),
         tts=TTS(),
         chat_ctx=initial_ctx
    )
def get_assistant():
    global assistant
    if assistant is None:
         loop = asyncio.new_event_loop()
         asyncio.set_event_loop(loop)
         assistant = loop.run_until_complete(create_assistant())
    return assistant

# ----- OpenAI TTS Endpoint using "Sage" voice -----
def generate_voice_response(text):
    try:
        headers = {
            "Authorization": f"Bearer {openai.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "text-to-speech-001",  # Confirm with OpenAI docs.
            "voice": "Sage",
            "input": text
        }
        response = requests.post("https://api.openai.com/v1/voices/synthesize", headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.text}")
            return None
        return response.content
    except Exception as e:
        print(f"Error generating voice response: {e}")
        return None

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
         return "No text provided", 400
    audio_data = generate_voice_response(text)
    if audio_data is None:
         return "Error generating audio", 500
    return Response(audio_data, mimetype='audio/mpeg')

def play_voice_response_on_dustbin(audio_data):
    if not audio_data:
         return
    try:
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/voice", data=audio_data, headers=headers)
        if response.status_code != 200:
            print(f"Failed to send voice response to dustbin. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending voice response to dustbin: {e}")

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Avaia Voice Assistant</title>
  <style>
      body {
          background-color: #000;
          color: #fff;
          font-family: Arial, sans-serif;
          text-align: center;
          margin: 0;
          padding: 0;
      }
      .container {
          margin: 0 auto;
          max-width: 600px;
          padding: 20px;
      }
      .chat-box {
          background-color: #111;
          border: 2px solid #00ffff;
          border-radius: 10px;
          padding: 20px;
          min-height: 300px;
          margin-bottom: 20px;
          overflow-y: auto;
      }
      .input-area {
          display: flex;
          justify-content: center;
          gap: 10px;
      }
      .input-area input {
          flex: 1;
          padding: 10px;
          border: 2px solid #00ffff;
          border-radius: 5px;
          background-color: #222;
          color: #fff;
      }
      .input-area button {
          padding: 10px 20px;
          border: none;
          background-color: #00ffff;
          color: #000;
          border-radius: 5px;
          cursor: pointer;
      }
      .voice-btn {
          background-color: #00ffff;
          border: none;
          border-radius: 50%;
          width: 60px;
          height: 60px;
          font-size: 18px;
          cursor: pointer;
          margin-top: 10px;
      }
  </style>
</head>
<body>
<div class="container">
  <h1>Avaia</h1>
  <div class="chat-box" id="chat-box"></div>
  <div class="input-area">
      <input type="text" id="user-input" placeholder="Type your command here..." />
      <button onclick="sendTextCommand()">Send</button>
  </div>
  <div>
      <button class="voice-btn" id="voice-btn">🎤</button>
  </div>
</div>
<script>
  let currentAudio = null;
  function appendMessage(sender, message) {
      const chatBox = document.getElementById('chat-box');
      const msgDiv = document.createElement('div');
      msgDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
      chatBox.appendChild(msgDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
  }
  async function speakText(text, allowInterruptions = true) {
      if (allowInterruptions && currentAudio) {
          currentAudio.pause();
          currentAudio = null;
      }
      try {
          const response = await fetch('/speak', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({text: text})
          });
          if (response.ok) {
              const blob = await response.blob();
              const url = URL.createObjectURL(blob);
              currentAudio = new Audio(url);
              currentAudio.play();
          } else {
              console.error("Error from /speak endpoint");
          }
      } catch (err) {
          console.error(err);
      }
  }
  async function sendTextCommand() {
      const input = document.getElementById('user-input');
      const command = input.value;
      if (!command) return;
      appendMessage('You', command);
      input.value = '';
      const response = await fetch('/ask', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text: command})
      });
      const data = await response.json();
      if (data.status === 'success') {
          appendMessage('Avaia', data.response);
          speakText(data.response, true);
      } else {
          appendMessage('Avaia', 'Error processing command.');
      }
  }
  let recognizing = false;
  let recognition;
  if ('webkitSpeechRecognition' in window) {
      recognition = new webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      recognition.onstart = function() {
          recognizing = true;
          document.getElementById('voice-btn').innerText = '🎙️';
      };
      recognition.onend = function() {
          recognizing = false;
          document.getElementById('voice-btn').innerText = '🎤';
      };
      recognition.onresult = function(event) {
          let transcript = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
              transcript += event.results[i][0].transcript;
          }
          appendMessage('You (voice)', transcript);
          fetch('/ask', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({text: transcript})
          })
          .then(response => response.json())
          .then(data => {
              if (data.status === 'success') {
                  appendMessage('Avaia', data.response);
                  speakText(data.response, true);
              } else {
                  appendMessage('Avaia', 'Error processing command.');
              }
          });
      };
  } else {
      document.getElementById('voice-btn').style.display = 'none';
  }
  document.getElementById('voice-btn').addEventListener('click', () => {
      if (recognition) {
          if (recognizing) {
              recognition.stop();
          } else {
              recognition.start();
          }
      }
  });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'status': 'error', 'message': 'No text provided'}), 400
    try:
        asst = get_assistant()
        response_text = asyncio.run(process_text_command(text, asst))
        return jsonify({'status': 'success', 'response': response_text})
    except Exception as e:
        logging.error(f"Error in /ask endpoint: {e}")
        return jsonify({'status': 'error', 'message': 'Processing failed'}), 500

last_command = ""
@app.route('/command', methods=['GET', 'POST'])
def command():
    global last_command
    if request.method == 'POST':
        data = request.get_json()
        last_command = data.get('command', '')
        print(f"Received command: {last_command}")
        return jsonify({'status': 'success', 'command_received': last_command})
    else:
        command_to_send = last_command
        last_command = ""
        return command_to_send, 200, {'Content-Type': 'text/plain'}

@app.route('/voice_command', methods=['POST'])
def voice_command():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'status': 'error', 'message': 'No audio file received'}), 400
    try:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        user_command_text = transcript.text
        print(f"User Command: {user_command_text}")
        if "dustbin come here" in user_command_text.lower():
            command_to_dustbin = "move_to_user"
            response_text = "Moving to your location."
        elif "dustbin open lid" in user_command_text.lower():
            command_to_dustbin = "open_lid"
            response_text = "Opening lid."
        elif "dustbin go home" in user_command_text.lower():
            command_to_dustbin = "go_home"
            response_text = "Returning to home position."
        else:
            command_to_dustbin = "unknown_command"
            response_text = "Command not understood."
        try:
            resp = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/command", json={'command': command_to_dustbin})
            if resp.status_code == 200:
                print(f"Command '{command_to_dustbin}' sent to dustbin.")
            else:
                print(f"Failed to send command to dustbin. Status code: {resp.status_code}")
                response_text = "Dustbin communication error."
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with dustbin: {e}")
            response_text = "Dustbin communication error."
        audio_response_data = generate_voice_response(response_text)
        if audio_response_data:
            play_voice_response_on_dustbin(audio_response_data)
        return jsonify({'status': 'success', 'command_sent': command_to_dustbin, 'response_text': response_text})
    except Exception as e:
        print(f"Error processing voice command: {e}")
        return jsonify({'status': 'error', 'message': 'Voice processing failed'}), 500

@app.route('/get_status', methods=['GET'])
def get_status():
    status = {
        'dustbin_status': 'Idle',
        'battery_level': '100%',
        'wifi_status': 'Connected'
    }
    return jsonify(status)

if __name__ == '__main__':
    get_assistant()
    app.run(debug=True, host='0.0.0.0', use_reloader=False)
