#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

/* =========================
   WIFI & SIEM SETTINGS
========================= */

const char* ssid = "Internet Name";
const char* password = "Internet Password";

const char* siem_url = "http://localhost:8000/api/v1/ingest";

/* =========================
   HARDWARE SETTINGS
========================= */

#define MQ2_PIN D1
#define DHT_PIN D2
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

/* =========================
   TIMER
========================= */

unsigned long previousMillisDHT = 0;
const long intervalDHT = 10000;  // 10 seconds

/* =========================
   SITUATION VARIABLES
========================= */

int lastGasState = HIGH;  

/* =========================
   SETUP
========================= */

void setup() {

  Serial.begin(115200);
  delay(1000);

  pinMode(MQ2_PIN, INPUT);
  dht.begin();

  Serial.println("\n[+] Launching a Physical SIEM Agent...");

  WiFi.begin(ssid, password);

  Serial.print("[+] Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[+] WiFi Connected!");
  Serial.print("[+] IP Address: ");
  Serial.println(WiFi.localIP());
}

/* =========================
   LOOP
========================= */

void loop() {

  unsigned long currentMillis = millis();

  /* -------------------------
     1) GAS CONTROL
  ------------------------- */

  int currentGasState = digitalRead(MQ2_PIN);

  Serial.print("Gas State: ");
  Serial.println(currentGasState);

  if (currentGasState == LOW && lastGasState == HIGH) {

    Serial.println("[!] GAS ALARM DETECTED!");

    sendToSIEM(
      "physical_security",
      "gas_leak_detected",
      "HIGH",
      "!!! Critical level of Gas/Smoke detected"
    );

    delay(5000); 
  }

  lastGasState = currentGasState;


  /* -------------------------
     2) TEMPERATURE CONTROL
  ------------------------- */

  if (currentMillis - previousMillisDHT >= intervalDHT) {

    previousMillisDHT = currentMillis;

    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(t) || isnan(h)) {
      Serial.println("[-] DHT11 read error!");
      
    }

    Serial.print("[*] TEMPERATURE: ");
    Serial.print(t);
    Serial.print(" C | Humidity: %");
    Serial.println(h);

    if (t > 35.0) {

      String msg = "!!! THE SYSTEM ROOM IS EXTREMELY HOT! Available: " + String(t) + "C";

      Serial.println(msg);

      sendToSIEM(
        "environment_monitoring",
        "extreme_temperature",
        "HIGH",
        msg
      );
    }
  }

  delay(1000);
}


/* =========================
   SIEM SENDING FUNCTION
========================= */

void sendToSIEM(String event_type, String action, String severity, String message) {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[-] No WiFi connection!!");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  http.begin(client, siem_url);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<512> doc;

  doc["source_ip"] = WiFi.localIP().toString();
  doc["device_id"] = "esp8266-server-room-01";
  doc["event_type"] = event_type;
  doc["action"] = action;
  doc["severity"] = severity;
  doc["message"] = message;

  String requestBody;
  serializeJson(doc, requestBody);

  Serial.println("[>] Sending to SIEM:");
  Serial.println(requestBody);

  int httpResponseCode = http.POST(requestBody);

  if (httpResponseCode > 0) {
    Serial.print("[+] SUCCESS! HTTP Code: ");
    Serial.println(httpResponseCode);
  } else {
    Serial.print("[-] Oops! Code: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}