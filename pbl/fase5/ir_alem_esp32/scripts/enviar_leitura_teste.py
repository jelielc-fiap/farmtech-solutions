from __future__ import annotations

import json
import random
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


URL = "http://localhost:5000/api/sensores"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def build_payload() -> dict[str, float | int | str]:
    soil_pct = random.uniform(18, 82)
    soil_raw = int(3200 - (soil_pct / 100) * (3200 - 1200))
    return {
        "device_id": "teste-python-local",
        "temperature_air_c": round(random.uniform(22, 35), 2),
        "humidity_air_pct": round(random.uniform(35, 85), 2),
        "soil_raw": soil_raw,
        "soil_moisture_pct": round(soil_pct, 2),
        "wifi_rssi": -48,
        "esp32_millis": int(time.time() * 1000),
    }


def main() -> int:
    payload = build_payload()
    data = json.dumps(payload).encode("utf-8")
    request = Request(URL, data=data, headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except HTTPError as exc:
        print(f"Erro HTTP {exc.code}: {exc.read().decode('utf-8')}")
        return 1
    except URLError as exc:
        print(f"Falha ao conectar em {URL}: {exc}")
        print("Confirme se o servidor esta rodando com run_receiver.bat.")
        return 1

    print("Payload enviado:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("Resposta do servidor:")
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
