#include <WiFi.h>
#include <HTTPClient.h>

// Wi-Fi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Telegram Bot Token and Chat ID
String botToken = "YOUR_TELEGRAM_BOT_TOKEN";
String chatID = "YOUR_TELEGRAM_CHAT_ID";

// Pins
#define TRIG_PIN 5
#define ECHO_PIN 18
#define BUZZER_PIN 19

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi connected.");
}

float measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.034 / 2;
  return distance;
}

void sendTelegramMessage(String message) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = "https://api.telegram.org/bot" + botToken + "/sendMessage?chat_id=" + chatID + "&text=" + message;
    
    http.begin(url);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      Serial.println("Telegram message sent.");
    } else {
      Serial.println("Failed to send Telegram message.");
    }
    http.end();
  } else {
    Serial.println("Wi-Fi not connected. Cannot send message.");
  }
}

void loop() {
  float distance = measureDistance();
  Serial.println("Distance: " + String(distance) + " cm");

  if (distance < 20) {
    // Trigger buzzer
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000); // Buzzer on for 1 second
    digitalWrite(BUZZER_PIN, LOW);

    // Send message to Telegram
    sendTelegramMessage("⚠️ Object detected at " + String(distance) + " cm!");

    // Cooldown for 10 seconds
    delay(10000);
  }

  delay(500); // Normal checking delay
}
