CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    received_at TEXT NOT NULL,
    esp32_millis INTEGER,
    temperature_air_c REAL NOT NULL,
    humidity_air_pct REAL NOT NULL,
    soil_raw INTEGER NOT NULL,
    soil_moisture_pct REAL NOT NULL,
    wifi_rssi INTEGER,
    risk_level TEXT NOT NULL,
    recommendation TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_received_at
ON sensor_readings (received_at);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id
ON sensor_readings (device_id);
