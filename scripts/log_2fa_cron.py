#!/usr/bin/env python3
import os
import time
import base64
import pyotp
from datetime import datetime, timezone

# Read hex seed from persistent storage
seed_file = '/data/seed.txt'
log_file = '/cron/last_code.txt'

try:
    with open(seed_file, 'r') as f:
        hex_seed = f.read().strip()
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - 2FA Code: {code}\n")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
