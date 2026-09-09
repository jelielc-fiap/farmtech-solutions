from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "http://localhost:5000"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def request_json(path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict | list]:
    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    with urlopen(request, timeout=10) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def main() -> int:
    payload = {
        "device_id": "teste-validacao-api",
        "temperature_air_c": 29.5,
        "humidity_air_pct": 58.0,
        "soil_raw": 2850,
        "soil_moisture_pct": 22.5,
        "wifi_rssi": -50,
        "esp32_millis": 10000,
    }

    try:
        status, health = request_json("/health")
        print(f"[OK] Health HTTP {status}: {health}")

        status, response = request_json("/api/sensores", method="POST", payload=payload)
        print(f"[OK] POST HTTP {status}: {response}")

        status, latest = request_json("/api/ultima")
        print(f"[OK] Ultima leitura HTTP {status}: {latest}")

        if not isinstance(latest, dict) or latest.get("device_id") != payload["device_id"]:
            print("[ERRO] A ultima leitura retornada nao corresponde ao payload enviado.")
            return 1
    except HTTPError as exc:
        print(f"[ERRO] HTTP {exc.code}: {exc.read().decode('utf-8')}")
        return 1
    except (URLError, TimeoutError) as exc:
        print(f"[ERRO] Nao foi possivel acessar {BASE_URL}: {exc}")
        print("Abra primeiro o servidor com run_receiver.bat ou run_all.bat.")
        return 1

    print("[OK] API, gravacao SQLite e leitura de retorno validadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
