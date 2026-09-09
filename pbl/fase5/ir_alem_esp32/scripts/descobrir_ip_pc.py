from __future__ import annotations

import socket
import sys


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def discover_local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())
    finally:
        sock.close()


if __name__ == "__main__":
    ip = discover_local_ip()
    print("IP local provavel deste computador:")
    print(ip)
    print()
    print("Use esta URL no sketch do ESP32:")
    print(f'const char* SERVER_URL = "http://{ip}:5000/api/sensores";')
