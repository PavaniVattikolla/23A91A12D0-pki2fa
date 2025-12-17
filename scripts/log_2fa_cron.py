#!/usr/bin/env python3
import os
import sys
import pyotp
import base64
from datetime import datetime
from pathlib import Path

SEED_FILE = Path("/data/seed.txt")

def hex_to_base32(hex_seed: str) -> str:
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode('utf-8')

try:
    if not SEED_FILE.exists():
        print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: Seed file not found", file=sys.stderr)
        sys.exit(1)
    
    with open(SEED_FILE, "r") as f:
        hex_seed = f.read().strip()
    
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
    code = totp.now()
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} - 2FA Code: {code}")
    
except Exception as e:
    print(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {e}", file=sys.stderr)
    sys.exit(1)
