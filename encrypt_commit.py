from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
import os

# ------------------------------
# Step 1: Load instructor's RSA public key from environment variable
# ------------------------------
instructor_pub_path = os.getenv("INSTRUCTOR_PUBLIC_KEY_PATH")
if not instructor_pub_path:
    raise Exception("INSTRUCTOR_PUBLIC_KEY_PATH environment variable not set!")

with open(instructor_pub_path, "rb") as f:
    pub_key = serialization.load_pem_public_key(f.read())

# ------------------------------
# Step 2: Read commit.sig as bytes
# ------------------------------
with open("commit.sig", "rb") as f:
    commit_bytes = f.read()

# ------------------------------
# Step 3: Generate random AES key (256-bit)
# ------------------------------
aes_key = os.urandom(32)  # 32 bytes = 256 bits

# ------------------------------
# Step 4: Encrypt commit.sig using AES-GCM
# ------------------------------
nonce = os.urandom(12)  # 12-byte nonce for GCM
cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
encryptor = cipher.encryptor()
ciphertext = encryptor.update(commit_bytes) + encryptor.finalize()
tag = encryptor.tag

# Combine nonce + tag + ciphertext for storage
aes_encrypted_data = nonce + tag + ciphertext

# ------------------------------
# Step 5: Encrypt AES key using RSA
# ------------------------------
encrypted_aes_key = pub_key.encrypt(
    aes_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# ------------------------------
# Step 6: Base64 encode everything
# ------------------------------
b64_encrypted_commit = b64encode(aes_encrypted_data).decode('utf-8')
b64_encrypted_aes_key = b64encode(encrypted_aes_key).decode('utf-8')

# ------------------------------
# Step 7: Print and save to files
# ------------------------------
print("Encrypted AES Key (RSA + Base64):")
print(b64_encrypted_aes_key)
print("\nEncrypted Commit (AES-GCM + Base64):")
print(b64_encrypted_commit)

with open("encrypted_commit.txt", "w") as f:
    f.write(b64_encrypted_commit)

with open("encrypted_aes_key.txt", "w") as f:
    f.write(b64_encrypted_aes_key)

print("\n✅ Encrypted AES key and commit saved to files successfully!")
