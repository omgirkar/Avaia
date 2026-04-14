#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>

// --- WiFi Credentials ---
const char* ssid = "esp";         // Replace with your WiFi SSID
const char* password = "987654321"; // Replace with your WiFi password

// --- Motor Driver Pins ---

const int motorA_IN1 = 23;
const int motorA_IN2 = 22;

const int motorB_IN3 = 21;
const int motorB_IN4 = 19;

// --- Ultrasonic Sensor Pins ---

const int trigPin = 12;
const int echoPin = 14;

// --- Servo Motor Pin ---
const int servoPin = 15;
Servo dustbinLidServo;

// --- IR Sensor Pin ---
const int irSensorPin = 13;

// --- Buzzer Pin ---
// const int buzzerPin = 4;

// --- Server IP Address (Python Backend) ---
const char* serverAddress = "192.168.51.121"; // Replace with your Python backend IP
const int serverPort = 5000;                          // Flask default port

bool isMoving = false; // Flag to track if dustbin is moving

void setup() {
  Serial.begin(115200);

  // --- Initialize WiFi ---
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // --- Motor Driver Pins Setup ---
 
  pinMode(motorA_IN1, OUTPUT);
  pinMode(motorA_IN2, OUTPUT);
  
  pinMode(motorB_IN3, OUTPUT);
  pinMode(motorB_IN4, OUTPUT);
  stopMotors(); // Initialize motors stopped

  // --- Ultrasonic Sensor Pins Setup ---
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // --- Servo Setup ---
  dustbinLidServo.attach(servoPin);
  closeLid(); // Initialize lid closed

  // --- IR Sensor Setup ---
  pinMode(irSensorPin, INPUT_PULLUP); // Use INPUT_PULLUP if IR sensor is active LOW

  // --- Buzzer Setup ---
//  pinMode(buzzerPin, OUTPUT);
//  digitalWrite(buzzerPin, LOW); // Buzzer off initially
}

void loop() {
  // --- Check for Command from Server ---
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String("http://") + serverAddress + ":" + String(serverPort) + "/command"); // ESP32 endpoint to receive commands
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println("Command Payload: " + payload);
      processCommand(payload); // Function to parse and execute command
    } else {
      Serial.print("Error receiving command. HTTP Code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
    // Handle WiFi disconnection (e.g., try to reconnect)
  }
  // --- Normal State/Idle Behavior (e.g., occasional ultrasonic scan, passive voice responses) ---
  if (!isMoving) {
    // Example: Periodically check distance (for presence detection, etc. - can be extended for user following)
    float distance = getDistance();
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    delay(2000); // Check every 2 seconds in idle state
  }

  delay(10); // Small delay to avoid overwhelming processor
}

// --- Function to Process Command from Server ---
void processCommand(String commandPayload) {
  if (commandPayload.indexOf("move_to_user") != -1) {
    moveToUser();
  } else if (commandPayload.indexOf("open_lid") != -1) {
    openLid();
  } else if (commandPayload.indexOf("go_home") != -1) {
    goHome();
  } else if (commandPayload.indexOf("move_forward") != -1) {
    moveForward();
  } else if (commandPayload.indexOf("move_backward") != -1) {
    moveBackward();
  } else if (commandPayload.indexOf("turn_left") != -1) {
    turnLeft();
  } else if (commandPayload.indexOf("turn_right") != -1) {
    turnRight();
  } else if (commandPayload.indexOf("stop") != -1) {
    stopMotors();
  }
}

// --- Motor Control Functions ---
void moveForward() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);

}

void moveBackward() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);

}

void turnRight() {
  digitalWrite(motorA_IN1, HIGH);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, HIGH);

}

void turnLeft() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, HIGH);
  digitalWrite(motorB_IN3, HIGH);
  digitalWrite(motorB_IN4, LOW);

}

void stopMotors() {
  digitalWrite(motorA_IN1, LOW);
  digitalWrite(motorA_IN2, LOW);
  digitalWrite(motorB_IN3, LOW);
  digitalWrite(motorB_IN4, LOW);
}

// --- Ultrasonic Sensor Function ---
float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  
  long duration = pulseIn(echoPin, HIGH, 30000); // 30,000 microseconds timeout
  return duration * 0.034 / 2.0; // Speed of sound in cm/microseconds divided by 2 (round trip)
}

// --- Servo Control Functions ---
void openLid() {
  dustbinLidServo.write(90); // Adjust angle as needed for open position
  delay(1000); // Keep lid open for 1 second
  closeLid(); // Automatically close after opening
}

void closeLid() {
  dustbinLidServo.write(0);  // Adjust angle as needed for closed position
}

// --- IR Sensor Function (Home Position Detection) ---
bool isHome() {
  // Assuming IR sensor is active LOW when it detects the home base
  return digitalRead(irSensorPin) == LOW;
}



// --- Autonomous Functions ---
void moveToUser() {
  isMoving = true;
  Serial.println("Moving to user...");


  while (true) { // Basic obstacle avoidance and forward movement - IMPROVE NAVIGATION LOGIC
    float distanceToObstacle = getDistance();
    if (distanceToObstacle < 45) { // Obstacle detected within 30cm - ADJUST THRESHOLD
      Serial.println("Obstacle detected, stopping.");
      stopMotors();
      delay(1000); // Wait briefly then try again (better obstacle avoidance needed)
      break; // For now, just stop. Better logic would be to try and navigate around.
    } else {
      moveForward(); // Move forward if no obstacle
    }
    delay(50); // Small delay in movement loop
    // In a real system, you'd need more sophisticated user following logic (e.g., using camera, beacons, etc.)
    // For this example, it's a simplified move forward until obstacle is detected or a timeout occurs.
    if (distanceToObstacle > 100) { // Example: Stop moving forward if nothing is detected within 100cm - ADJUST THRESHOLD, this is very basic and needs improvement.
      Serial.println("Reached approximate user location or lost track (very basic logic). Stopping.");
      stopMotors();
      break;
    }
  }
  isMoving = false;

}

void goHome() {
  isMoving = true;
  Serial.println("Going home...");

  while (!isHome()) { // Move backward until IR sensor detects home base - ADJUST MOVEMENT STRATEGY
    moveBackward(); // Simplistic - might need turning logic for more complex home base scenarios
    delay(50);
  }
  stopMotors();
  Serial.println("Home position reached.");

  isMoving = false;
}


