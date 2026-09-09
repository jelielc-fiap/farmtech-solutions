#pragma once

// Copie este arquivo para config.h e preencha com os dados reais da sua rede.
// O config.h fica ignorado pelo Git para proteger a senha do Wi-Fi.

const char* WIFI_SSID = "SUA_REDE_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";
const char* SERVER_URL = "http://192.168.0.100:5000/api/sensores";
const char* DEVICE_ID = "esp32-farmtech-01";

// Primeiro use false para validar sensores no Serial Monitor.
// Depois altere para true para enviar dados ao servidor Python.
const bool ENABLE_WIFI_SEND = false;
