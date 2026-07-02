import socket

ip = "192.168.137.85"
port = 80

print(f"Testing connection to {ip}...")
try:
    s = socket.create_connection((ip, port), timeout=5)
    print("✓ PORT IS OPEN! The network is fine.")
    s.close()
except Exception as e:
    print(f"✗ CONNECTION FAILED: {e}")