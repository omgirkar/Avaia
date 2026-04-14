# Avaia - Smart AI Project

## Project Overview

Avaia is an AI-powered smart dustbin project designed for a CS exhibition. It combines an ESP32 microcontroller for hardware control (motor, ultrasonic sensor, servo, IR sensor) with a Python Flask backend for AI integration (OpenAI LLM, speech-to-text, text-to-speech) and web-based control. The dustbin can respond to voice commands to move to the user, open its lid, and return to a home position.

## Features

*   **Voice Control:** Interact with the dustbin using natural language commands.
*   **Autonomous Navigation:** The dustbin can move towards the user and return to a home position.
*   **Obstacle Avoidance:** Basic obstacle detection using an ultrasonic sensor.
*   **Lid Automation:** Automatic lid opening and closing via servo motor.
*   **IR Home Detection:** Uses an IR sensor to detect its home base.
*   **Web Interface:** A simple web interface for interaction and control.
*   **AI Integration:** Leverages OpenAI for language understanding and response generation.

## Hardware Requirements

To build the Avaia Smart Dustbin, you will need the following hardware components:

*   **ESP32 Development Board:** The microcontroller responsible for hardware control and Wi-Fi communication.
*   **L298N Motor Driver Module:** To control the DC motors for movement.
*   **DC Motors (x2):** For driving the dustbin.
*   **HC-SR04 Ultrasonic Sensor:** For distance measurement and obstacle detection.
*   **MG90S Servo Motor:** To control the dustbin lid.
*   **IR Sensor:** For detecting the home position.
*   **Battery Pack (7.4V - 12V):** To power the motors and ESP32.
*   **Jumper Wires, Breadboard, etc.**

## Circuit Diagram

The following diagram illustrates the wiring connections between the ESP32 and the various components:

![Circuit Diagram](https://private-us-east-1.manuscdn.com/sessionFile/EPXNA1p6dICOpshzPhciLV/sandbox/uGEdETZYbFGa16nKUjr7nm-images_1776197782149_na1fn_L2hvbWUvdWJ1bnR1L2F2YWlhX3Byb2plY3QvY2lyY3VpdF9kaWFncmFt.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvRVBYTkExcDZkSUNPcHNoelBoY2lMVi9zYW5kYm94L3VHRWRFVFpZYkZHYTE2bktVanI3bm0taW1hZ2VzXzE3NzYxOTc3ODIxNDlfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyRjJZV2xoWDNCeWIycGxZM1F2WTJseVkzVnBkRjlrYVdGbmNtRnQucG5nIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzk4NzYxNjAwfX19XX0_&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=gQrtNw3HEX6mNDvRRYy2vy5LUHLG3c1NIJiS9NasgIl1Qng-xKu9ZAv4r~vM9iiis8aZHzzQFHZNtYL4ufrdgd7I7Uso-gD5y8kWylOtvGWyNz8kIEtc2dkx3lvoNQokwssHXLA6i~RNDhnr2csFxJHadNeJbipH04XDe62JTStMr3mgs9f5IQE5SIqG288zKjip-DnqarGOzXdt3E9hjkYiCTNhiDwAt9rGX48G3e6JXx9F-Ak0I4IR9EufSjsH-JTlmnpWliqx-6v1iw3L6A3e6xZmvT1FCQxi5ZQHEbeJyZ7MN0pUonWVxQzMEs0XQLEyvmJYf7L8xn0-txfYDg__)

### Wiring Details:

*   **Motor Driver (L298N):**
    *   `motorA_IN1` (GPIO 23) -> L298N IN1
    *   `motorA_IN2` (GPIO 22) -> L298N IN2
    *   `motorB_IN3` (GPIO 21) -> L298N IN3
    *   `motorB_IN4` (GPIO 19) -> L298N IN4
    *   L298N 12V -> Battery VCC
    *   L298N GND -> Battery GND & ESP32 GND (Common Ground)
    *   L298N 5V -> HC-SR04 VCC
    *   L298N 5V -> Servo VCC
    *   L298N 5V -> IR Sensor VCC
    *   L298N 5V -> ESP32 VIN (Optional, if not powered via USB)

*   **Ultrasonic Sensor (HC-SR04):**
    *   `trigPin` (GPIO 12) -> HC-SR04 Trig
    *   `echoPin` (GPIO 14) -> HC-SR04 Echo

*   **Servo Motor (MG90S):**
    *   `servoPin` (GPIO 15) -> Servo Signal Pin

*   **IR Sensor:**
    *   `irSensorPin` (GPIO 13) -> IR Sensor Output Pin

## Software Setup

### ESP32 (Arduino IDE)

1.  **Install Arduino IDE:** Download and install the Arduino IDE.
2.  **ESP32 Board Manager:** Add the ESP32 board manager URL to your Arduino IDE preferences and install the ESP32 boards.
    *   Go to `File > Preferences`.
    *   Add `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json` to "Additional Board Manager URLs."
    *   Go to `Tools > Board > Boards Manager`, search for "esp32" and install it.
3.  **Install Libraries:**
    *   `WiFi.h` (usually built-in with ESP32 core)
    *   `HTTPClient.h` (usually built-in with ESP32 core)
    *   `ESP32Servo.h`: Go to `Sketch > Include Library > Manage Libraries...`, search for "ESP32Servo" and install.
4.  **Upload `sketch_feb17a.ino`:**
    *   Open `sketch_feb17a.ino` in Arduino IDE.
    *   Update `ssid` and `password` with your Wi-Fi credentials (lines 6-7).
    *   Update `serverAddress` with the IP address of your Python backend (line 33).
    *   Select your ESP32 board and port (`Tools > Board`, `Tools > Port`).
    *   Upload the code to your ESP32.

### Python Backend

1.  **Prerequisites:** Ensure you have Python 3.8+ installed.
2.  **Navigate to Project Directory:** Open your terminal or command prompt and navigate to the `Avaia BETA 2.0.0` directory.
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file is not provided in the uploaded zip, but based on `main.py` and `server.py`, the following packages are likely needed: `flask`, `requests`, `openai`, `python-dotenv`, `langdetect`, `silero` (or a compatible VAD/STT/TTS library). You may need to create this file manually or install them one by one.)*

    Example `requirements.txt` content:
    ```
    Flask
    requests
    openai
    python-dotenv
    langdetect
    # silero (or specific version if needed, or replace with actual VAD/STT/TTS)
    ```

4.  **OpenAI API Key:**
    *   Obtain an OpenAI API key from the [OpenAI website](https://platform.openai.com/).
    *   In `main.py` (line 174) and `server.py` (line 11), replace `"OpenAI API key"` with your actual OpenAI API key.
    *   Alternatively, create a `.env` file in the same directory as `main.py` and add `OPENAI_API_KEY="your_api_key_here"`.
5.  **Update ESP32 IP Address:**
    *   In `main.py` (line 116), update `DUSTBIN_IP_ADDRESS = "ESP32 IP"` with the actual IP address of your ESP32.
    *   In `server.py` (line 14), update `DUSTBIN_IP_ADDRESS = "192.168.51.10"` with the actual IP address of your ESP32.
6.  **Run the Backend Server:**
    ```bash
    python main.py
    ```
    or
    ```bash
    python server.py
    ```
    *(Note: It appears there are two Flask applications, `main.py` and `server.py`. You should clarify which one is the primary backend or if they serve different purposes. For a single integrated system, typically one Flask app handles all functionalities. If both are intended to run, they would need to run on different ports or be integrated into a single application.)*

## Usage

1.  **Power On:** Ensure your ESP32 and the Python backend are running.
2.  **Access Web Interface:** Open a web browser and navigate to the IP address of your Python backend (e.g., `http://localhost:5000` if running locally, or the server's IP address).
3.  **Voice Commands:** Use the web interface to issue voice commands to the dustbin. Supported commands include:
    *   "Dustbin come here"
    *   "Dustbin open lid"
    *   "Dustbin go home"
4.  **AI Interaction:** You can also ask general questions to Avaia, the AI assistant.

## Troubleshooting

*   **Wi-Fi Connection Issues:** Double-check your `ssid` and `password` in `sketch_feb17a.ino`.
*   **ESP32 IP Address:** Ensure the `DUSTBIN_IP_ADDRESS` in your Python files matches the actual IP address of your ESP32.
*   **OpenAI API Key:** Verify your OpenAI API key is correctly set and has the necessary permissions.
*   **Motor/Servo Not Responding:** Check wiring connections and ensure sufficient power supply to the L298N motor driver.
*   **Ultrasonic Sensor Inaccurate:** Ensure the sensor is clear of obstructions and correctly wired.

## Contributing

Feel free to fork this repository, submit pull requests, or open issues for any improvements or bug fixes.

## License

This project is open-source and available under the MIT License.

## Contact

For any questions or inquiries, please contact Om Girkar.
