#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

#define DHTPIN 27
#define DHTTYPE DHT22
#define SOIL_PIN 34

// Copie config.example.h para config.h e preencha os dados reais da sua rede.
// O arquivo config.h fica ignorado pelo Git para nao expor senha de Wi-Fi.
#if __has_include("config.h")
#include "config.h"
#else
const char* WIFI_SSID = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";
const char* SERVER_URL = "http://192.168.0.100:5000/api/sensores";
const char* DEVICE_ID = "esp32-farmtech-01";
const bool ENABLE_WIFI_SEND = false;
#endif
const unsigned long READ_INTERVAL_MS = 10000;
const unsigned long WIFI_TIMEOUT_MS = 20000;

// Calibracao inicial do sensor resistivo.
// Ajuste depois testando a sonda seca e em solo bem umido.
const int SOIL_DRY_RAW = 3200;
const int SOIL_WET_RAW = 1200;

DHT dht(DHTPIN, DHTTYPE);
unsigned long lastRead = 0;

float soilPercentFromRaw(int rawValue) {
  float percent = ((float)(SOIL_DRY_RAW - rawValue) * 100.0f) / (float)(SOIL_DRY_RAW - SOIL_WET_RAW);
  return constrain(percent, 0.0f, 100.0f);
}

bool connectWifi() {
  if (WiFi.status() == WL_CONNECTED) {
    return true;
  }

  Serial.print("Conectando ao Wi-Fi: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startedAt = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startedAt < WIFI_TIMEOUT_MS) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println();
    Serial.println("Wi-Fi nao conectado. Leituras locais continuam no Serial Monitor.");
    return false;
  }

  Serial.println();
  Serial.println("Wi-Fi conectado.");
  Serial.print("IP do ESP32: ");
  Serial.println(WiFi.localIP());
  return true;
}

String buildPayload(float temperatureC, float humidityAir, int soilRaw, float soilPercent) {
  String payload = "{";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  payload += "\"temperature_air_c\":" + String(temperatureC, 2) + ",";
  payload += "\"humidity_air_pct\":" + String(humidityAir, 2) + ",";
  payload += "\"soil_raw\":" + String(soilRaw) + ",";
  payload += "\"soil_moisture_pct\":" + String(soilPercent, 2) + ",";
  payload += "\"wifi_rssi\":" + String(WiFi.RSSI()) + ",";
  payload += "\"esp32_millis\":" + String(millis());
  payload += "}";
  return payload;
}

void sendReading(String payload) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi desconectado. Tentando reconectar...");
    if (!connectWifi()) {
      Serial.println("Envio HTTP pulado nesta leitura.");
      return;
    }
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  int statusCode = http.POST(payload);
  String response = http.getString();

  Serial.print("HTTP status: ");
  Serial.println(statusCode);
  Serial.print("Resposta: ");
  Serial.println(response);

  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println("FarmTech Solutions - ESP32 IoT");
  Serial.println("DHT22 no GPIO 27 e sensor de solo analogico no GPIO 34.");

  dht.begin();
  analogReadResolution(12);
  if (ENABLE_WIFI_SEND) {
    connectWifi();
  } else {
    Serial.println("Envio HTTP desativado. Use apenas para validar leituras no Serial Monitor.");
  }
}

void loop() {
  if (millis() - lastRead < READ_INTERVAL_MS) {
    return;
  }
  lastRead = millis();

  float humidityAir = dht.readHumidity();
  float temperatureC = dht.readTemperature();
  int soilRaw = analogRead(SOIL_PIN);
  float soilPercent = soilPercentFromRaw(soilRaw);

  if (isnan(humidityAir) || isnan(temperatureC)) {
    Serial.println("Falha ao ler o DHT22. Verifique DATA no GPIO 27 e resistor pull-up de 10k.");
    return;
  }

  Serial.println("----------------------------------------");
  Serial.print("Temperatura do ar (C): ");
  Serial.println(temperatureC, 2);
  Serial.print("Umidade do ar (%): ");
  Serial.println(humidityAir, 2);
  Serial.print("Umidade do solo bruta: ");
  Serial.println(soilRaw);
  Serial.print("Umidade do solo (%): ");
  Serial.println(soilPercent, 2);

  String payload = buildPayload(temperatureC, humidityAir, soilRaw, soilPercent);
  Serial.print("Payload: ");
  Serial.println(payload);

  if (ENABLE_WIFI_SEND) {
    sendReading(payload);
  }
}

