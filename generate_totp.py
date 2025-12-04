import hmac
import hashlib
import time
import struct
import os
from cryptography.hazmat.primitives import serialization

# Load private key path from environment variable
private_key_path = os.getenv("STUDENT_PRIVATE_KEY_PATH")
if not private_key_path:
    raise Exception("STUDENT_PRIVATE_KEY_PATH environment variable not set!")

# Load the private key (assumes PEM format, no password)
with open(private_key_path, "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None
    )

# For TOTP, derive a seed from the private key bytes
# Here we use the DER-encoded private key bytes as the seed
seed_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

def generate_totp(seed, digits=6, time_step=30):
    # Get current Unix time and divide by the time step
    counter = int(time.time() // time_step)
    
    # Pack counter into 8-byte big-endian
    counter_bytes = struct.pack(">Q", counter)
    
    # HMAC-SHA1 of seed and counter
    hmac_hash = hmac.new(seed, counter_bytes, hashlib.sha1).digest()
    
    # Dynamic truncation
    offset = hmac_hash[-1] & 0x0F
    code = ((hmac_hash[offset] & 0x7f) << 24 |
            (hmac_hash[offset+1] & 0xff) << 16 |
            (hmac_hash[offset+2] & 0xff) << 8 |
            (hmac_hash[offset+3] & 0xff))
    
    # Get the OTP of required digits
    return str(code % (10 ** digits)).zfill(digits)

# Generate OTP
otp = generate_totp(seed_bytes)
print("Your TOTP is:", otp)
