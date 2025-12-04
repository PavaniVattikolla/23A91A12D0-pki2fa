import pyotp
import binascii
import base64

# Read decrypted seed (hex)
with open("decrypt_seed.txt", "r") as f:
    hex_seed = f.read().strip()

# Convert hex to bytes, then to Base32
seed_bytes = binascii.unhexlify(hex_seed)
base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

# Create TOTP object
totp = pyotp.TOTP(base32_seed)

# Generate current TOTP
print("Current TOTP code:", totp.now())
