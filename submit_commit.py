from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import os
import subprocess

# ------------------------------
# Step 1: Load student private key from environment variable
# ------------------------------
student_priv_path = os.getenv("STUDENT_PRIVATE_KEY_PATH")
if not student_priv_path:
    raise Exception("STUDENT_PRIVATE_KEY_PATH environment variable not set!")

with open(student_priv_path, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# ------------------------------
# Step 2: Read commit.txt as bytes
# ------------------------------
with open("commit.txt", "rb") as f:
    commit_bytes = f.read()

# ------------------------------
# Step 3: Sign commit using RSA-PSS
# ------------------------------
signature = private_key.sign(
    commit_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# ------------------------------
# Step 4: Save signature to commit.sig
# ------------------------------
with open("commit.sig", "wb") as f:
    f.write(signature)

print("✅ Commit signed successfully and saved as commit.sig")

# ------------------------------
# Step 5: Optionally call encrypt_commit.py (if you want automated encryption)
# ------------------------------
subprocess.run(["python", "encrypt_commit.py"], check=True)
