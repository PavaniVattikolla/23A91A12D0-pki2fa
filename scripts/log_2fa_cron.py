#!/usr/bin/env python3

import os
import sys
import time
import base64
import pyotp
from datetime import datetime, timezone

# File paths (relative to this script)
seed_file = os.path.join(os.path.dirname(__file__), '../data/seed.txt')
last_code_file = os.path.join(os.path.dirname(__file__), '../cron/last_code.txt')

try:
    # Read hex seed
    with open(seed_file, 'r') as f:
        hex_seed = f.read().strip()

    # Convert hex seed to bytes and then to Base32
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

    # Generate current TOTP code
    totp = pyotp.TOTP(base32_seed)
    code = totp.now()

    # Get current UTC timestamp
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Append code to log file
    os.makedirs(os.path.dirname(last_code_file), exist_ok=True)  # Ensure directory exists
    with open(last_code_file, 'a') as f:
        f.write(f"{timestamp} - 2FA Code: {code}\n")

    print(f"Logged TOTP code: {code}")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
