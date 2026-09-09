from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request


BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "leituras_esp32.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema_sqlite.sql"

app = Flask(__name__)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def get_connection() -> sqlite3.Connection:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def required_float(payload: dict[str, Any], field: str, minimum: float, maximum: float) -> float:
    if field not in payload:
        raise ValueError(f"Campo obrigatorio ausente: {field}")
    try:
        value = float(payload[field])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Campo invalido: {field}") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"Campo fora da faixa esperada: {field}")
    return value


def optional_int(payload: dict[str, Any], field: str) -> int | None:
    value = payload.get(field)
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Campo invalido: {field}") from exc


def build_recommendation(temperature_air_c: float, humidity_air_pct: float, soil_moisture_pct: float) -> tuple[str, str]:
    actions: list[str] = []
    risk_points = 0

    if soil_moisture_pct < 30:
        actions.append("Irrigar o canteiro, pois a umidade do solo está baixa.")
        risk_points += 2
    elif soil_moisture_pct > 75:
        actions.append("Suspender irrigação temporariamente para evitar excesso de água.")
        risk_points += 1
    else:
        actions.append("Manter monitoramento; umidade do solo dentro da faixa operacional.")

    if temperature_air_c >= 32:
        actions.append("Temperatura elevada: priorizar leituras mais frequentes.")
        risk_points += 1

    if humidity_air_pct < 35:
        actions.append("Umidade do ar baixa: acompanhar estresse hídrico da cultura.")
        risk_points += 1

    if risk_points >= 3:
        risk_level = "Alto"
    elif risk_points >= 1:
        risk_level = "Médio"
    else:
        risk_level = "Baixo"

    return risk_level, " ".join(actions)


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    init_db()
    return {"status": "ok", "database": str(DB_PATH)}, 200


@app.post("/api/sensores")
def receive_sensor_data():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"status": "erro", "message": "Envie um JSON valido."}), 400

    try:
        device_id = str(payload.get("device_id") or "esp32-farmtech-01").strip()
        if not device_id:
            raise ValueError("Campo invalido: device_id")

        temperature_air_c = required_float(payload, "temperature_air_c", -10, 70)
        humidity_air_pct = required_float(payload, "humidity_air_pct", 0, 100)
        soil_raw = int(required_float(payload, "soil_raw", 0, 4095))
        soil_moisture_pct = required_float(payload, "soil_moisture_pct", 0, 100)
        wifi_rssi = optional_int(payload, "wifi_rssi")
        esp32_millis = optional_int(payload, "esp32_millis")
    except ValueError as exc:
        return jsonify({"status": "erro", "message": str(exc)}), 400

    received_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    risk_level, recommendation = build_recommendation(
        temperature_air_c=temperature_air_c,
        humidity_air_pct=humidity_air_pct,
        soil_moisture_pct=soil_moisture_pct,
    )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sensor_readings (
                device_id,
                received_at,
                esp32_millis,
                temperature_air_c,
                humidity_air_pct,
                soil_raw,
                soil_moisture_pct,
                wifi_rssi,
                risk_level,
                recommendation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device_id,
                received_at,
                esp32_millis,
                temperature_air_c,
                humidity_air_pct,
                soil_raw,
                soil_moisture_pct,
                wifi_rssi,
                risk_level,
                recommendation,
            ),
        )
        reading_id = cursor.lastrowid

    return jsonify(
        {
            "status": "ok",
            "id": reading_id,
            "risk_level": risk_level,
            "recommendation": recommendation,
        }
    ), 201


@app.get("/api/leituras")
def list_readings():
    try:
        limit = min(max(int(request.args.get("limit", "100")), 1), 500)
    except ValueError:
        limit = 100

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return jsonify([dict(row) for row in reversed(rows)])


@app.get("/api/ultima")
def latest_reading():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sensor_readings ORDER BY id DESC LIMIT 1",
        ).fetchone()

    if row is None:
        return jsonify({"status": "vazio", "message": "Nenhuma leitura recebida ainda."}), 404

    return jsonify(dict(row))


@app.get("/")
def html_dashboard():
    return """
    <!doctype html>
    <html lang="pt-BR">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>FarmTech ESP32 IoT</title>
      <style>
        :root {
          --bg: #eef5ef;
          --panel: #ffffff;
          --text: #19372a;
          --muted: #5d7167;
          --border: #c8d8ce;
          --green: #166534;
          --orange: #b45309;
          --red: #b91c1c;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          background: var(--bg);
          color: var(--text);
          font-family: Arial, Helvetica, sans-serif;
        }
        main {
          max-width: 1120px;
          margin: 0 auto;
          padding: 28px 18px 42px;
        }
        header {
          background: #123524;
          color: #fff;
          border-radius: 12px;
          padding: 22px 24px;
          margin-bottom: 18px;
        }
        h1 { margin: 0 0 8px; font-size: 28px; }
        p { margin: 0; color: var(--muted); }
        header p { color: #d9efe1; }
        .grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }
        .card, section {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: 10px;
          padding: 16px;
        }
        .label { color: var(--muted); font-size: 13px; margin-bottom: 8px; }
        .value { font-size: 26px; font-weight: 700; }
        section { margin-top: 14px; }
        h2 { margin: 0 0 12px; font-size: 18px; }
        .recommendation {
          border-left: 4px solid var(--green);
          padding-left: 12px;
          line-height: 1.5;
        }
        .risk-Alto { color: var(--red); }
        .risk-Medio { color: var(--orange); }
        .risk-Baixo { color: var(--green); }
        svg {
          display: block;
          width: 100%;
          height: 280px;
          border: 1px solid var(--border);
          border-radius: 8px;
          background: #fbfdfb;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }
        th, td {
          border-bottom: 1px solid var(--border);
          padding: 10px 8px;
          text-align: left;
        }
        th { color: #244f38; }
        @media (max-width: 800px) {
          .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 520px) {
          .grid { grid-template-columns: 1fr; }
        }
      </style>
    </head>
    <body>
      <main>
        <header>
          <h1>FarmTech ESP32 IoT</h1>
          <p>Recebendo temperatura, umidade do ar e umidade do solo via HTTP.</p>
        </header>

        <div class="grid">
          <div class="card"><div class="label">Temperatura</div><div class="value" id="temp">--</div></div>
          <div class="card"><div class="label">Umidade do ar</div><div class="value" id="air">--</div></div>
          <div class="card"><div class="label">Umidade do solo</div><div class="value" id="soil">--</div></div>
          <div class="card"><div class="label">Risco</div><div class="value" id="risk">--</div></div>
        </div>

        <section>
          <h2>Recomendação automática</h2>
          <p class="recommendation" id="recommendation">Aguardando leituras do ESP32.</p>
        </section>

        <section>
          <h2>Histórico das leituras</h2>
          <svg id="chart" viewBox="0 0 900 280" role="img" aria-label="Grafico de umidade do solo"></svg>
        </section>

        <section>
          <h2>Últimos registros</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Recebido em</th>
                <th>Dispositivo</th>
                <th>Temp.</th>
                <th>Umid. ar</th>
                <th>Solo</th>
                <th>RSSI</th>
              </tr>
            </thead>
            <tbody id="rows">
              <tr><td colspan="7">Aguardando dados.</td></tr>
            </tbody>
          </table>
        </section>
      </main>

      <script>
        function fmt(value, suffix) {
          if (value === null || value === undefined) return "--";
          return Number(value).toFixed(1) + suffix;
        }

        function drawChart(data) {
          const svg = document.getElementById("chart");
          svg.innerHTML = "";
          const width = 900, height = 280, pad = 36;

          const bgLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
          bgLine.setAttribute("x1", pad);
          bgLine.setAttribute("x2", width - pad);
          bgLine.setAttribute("y1", height - pad);
          bgLine.setAttribute("y2", height - pad);
          bgLine.setAttribute("stroke", "#b8cec0");
          svg.appendChild(bgLine);

          if (!data.length) return;

          const points = data.map((row, index) => {
            const x = pad + (index * (width - 2 * pad)) / Math.max(data.length - 1, 1);
            const y = height - pad - (Number(row.soil_moisture_pct) * (height - 2 * pad)) / 100;
            return `${x},${y}`;
          }).join(" ");

          const polyline = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
          polyline.setAttribute("points", points);
          polyline.setAttribute("fill", "none");
          polyline.setAttribute("stroke", "#166534");
          polyline.setAttribute("stroke-width", "4");
          polyline.setAttribute("stroke-linecap", "round");
          polyline.setAttribute("stroke-linejoin", "round");
          svg.appendChild(polyline);

          data.forEach((row, index) => {
            const x = pad + (index * (width - 2 * pad)) / Math.max(data.length - 1, 1);
            const y = height - pad - (Number(row.soil_moisture_pct) * (height - 2 * pad)) / 100;
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", x);
            circle.setAttribute("cy", y);
            circle.setAttribute("r", "4");
            circle.setAttribute("fill", "#123524");
            svg.appendChild(circle);
          });
        }

        async function refresh() {
          const response = await fetch("/api/leituras?limit=30");
          const data = await response.json();
          const latest = data[data.length - 1];

          if (latest) {
            document.getElementById("temp").textContent = fmt(latest.temperature_air_c, " °C");
            document.getElementById("air").textContent = fmt(latest.humidity_air_pct, "%");
            document.getElementById("soil").textContent = fmt(latest.soil_moisture_pct, "%");
            const risk = document.getElementById("risk");
            risk.textContent = latest.risk_level;
            const riskColors = {"Alto": "#b91c1c", "Médio": "#b45309", "Baixo": "#166534"};
            risk.className = "value";
            risk.style.color = riskColors[latest.risk_level] || "#183629";
            document.getElementById("recommendation").textContent = latest.recommendation;
          }

          drawChart(data);

          const rows = document.getElementById("rows");
          rows.innerHTML = "";
          data.slice().reverse().slice(0, 12).forEach((row) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
              <td>${row.id}</td>
              <td>${row.received_at}</td>
              <td>${row.device_id}</td>
              <td>${fmt(row.temperature_air_c, " °C")}</td>
              <td>${fmt(row.humidity_air_pct, "%")}</td>
              <td>${fmt(row.soil_moisture_pct, "%")}</td>
              <td>${row.wifi_rssi ?? "--"}</td>`;
            rows.appendChild(tr);
          });
        }

        refresh();
        setInterval(refresh, 5000);
      </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
