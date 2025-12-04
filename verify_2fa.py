import pyotp
import binascii
import base64

# Step 1: Read decrypted seed (hex) from file
with open("decrypt_seed.txt", "r") as f:
    hex_seed = f.read().strip()

# Step 2: Convert hex to bytes, then to Base32
try:
    seed_bytes = binascii.unhexlify(hex_seed)
except binascii.Error:
    print("❌ Invalid hex seed in decrypt_seed.txt")
    exit(1)

base32_seed = base64.b32encode(seed_bytes).decode('utf-8')

# Step 3: Create TOTP object
totp = pyotp.TOTP(base32_seed)

# Step 4: Automatically generate TOTP
current_code = totp.now()
print(f"Using TOTP code: {current_code}")

# Step 5: Verify the code
if totp.verify(current_code):
    print("✅ Code is valid!")
else:
    print("❌ Invalid code!")
