from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import base64

# Load your private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )

# Read encrypted seed
with open("encrypted_seed.txt", "r") as f:
    encrypted_seed_b64 = f.read().strip()

# Decode from base64
encrypted_seed_bytes = base64.b64decode(encrypted_seed_b64)

# Decrypt using RSA
decrypted_seed = private_key.decrypt(
    encrypted_seed_bytes,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Print the decrypted seed as string
print("Decrypted seed:", decrypted_seed.decode())
