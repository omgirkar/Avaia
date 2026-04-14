from flask import Flask, request, jsonify, render_template
import openai
import requests
import json

app = Flask(__name__)
last_command = ""


# --- OpenAI API Setup ---
openai.api_key = "YOUR API KEY"

# --- ESP32 Dustbin IP Address ---
DUSTBIN_IP_ADDRESS = "000.000.00.00" # Replace with your ESP32's IP

# --- Voice Response Function (Optional - can use pre-recorded sounds as well) ---
def generate_voice_response(text):
    try:
        response = openai.audio.speech.create(
            model="gpt-4o-mini",
            voice="alloy", # Choose a voice
            max_tokens=15,
            input=text
        )
        return response.content
    except Exception as e:
        print(f"Error generating voice response: {e}")
        return None

def play_voice_response_on_dustbin(audio_data):
    try:
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/voice", data=audio_data, headers=headers)
        if response.status_code != 200:
            print(f"Failed to send voice response to dustbin. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending voice response to dustbin: {e}")

# --- Add this route to serve index.html ---
@app.route('/')
def index():
    return render_template('index.html') # Render the index.html template

@app.route('/command', methods=['GET', 'POST'])
def command():
    global last_command
    if request.method == 'POST':
        data = request.get_json()
        last_command = data.get('command', '')
        print(f"Received command: {last_command}")
        return jsonify({'status': 'success', 'command_received': last_command})
    else:  # GET request from ESP32 polling for a command
        command_to_send = last_command
        # Optionally clear the command after sending it
        last_command = ""
        return command_to_send, 200, {'Content-Type': 'text/plain'}
    
# --- API Endpoint for Voice Command ---
@app.route('/voice_command', methods=['POST'])
def voice_command():
    audio_file = request.files['audio'] # Expecting audio file in request
    if not audio_file:
        return jsonify({'status': 'error', 'message': 'No audio file received'}), 400

    try:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        user_command_text = transcript.text
        print(f"User Command: {user_command_text}")

        # --- Intent Recognition and Command Logic ---
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

        # --- Send Command to ESP32 Dustbin ---
        try:
            response = requests.post(f"http://{DUSTBIN_IP_ADDRESS}/command", json={'command': command_to_dustbin})
            if response.status_code == 200:
                print(f"Command '{command_to_dustbin}' sent to dustbin.")
            else:
                print(f"Failed to send command to dustbin. Status code: {response.status_code}")
                response_text = "Dustbin communication error."
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with dustbin: {e}")
            response_text = "Dustbin communication error."

        # --- Generate and Play Voice Response (Optional) ---
        audio_response_data = generate_voice_response(response_text)
        if audio_response_data:
            play_voice_response_on_dustbin(audio_response_data)


        return jsonify({'status': 'success', 'command_sent': command_to_dustbin, 'response_text': response_text})

    except Exception as e:
        print(f"Error processing voice command: {e}")
        return jsonify({'status': 'error', 'message': 'Voice processing failed'}), 500

@app.route('/get_status', methods=['GET'])
def get_status():
    # For now, we return static status data
    status = {
        'dustbin_status': 'Idle',
        'battery_level': '100%',
        'wifi_status': 'Connected'
    }
    return jsonify(status)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')