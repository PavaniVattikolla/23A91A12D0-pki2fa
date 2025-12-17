#!/usr/bin/env python3
"""Generate commit proof for submission"""

import subprocess
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64

print("=== PKI 2FA Commit Proof Generator ===")
print()

# Get current commit hash
commit_hash = subprocess.check_output(['git', 'log', '-1', '--format=%H']).decode('utf-8').strip()
print(f"Commit Hash: {commit_hash}")

# Load student private key
with open('student_private.pem', 'rb') as f:
    student_private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Sign commit hash (as ASCII string)
print("\nSigning commit hash...")
signature = student_private_key.sign(
    commit_hash.encode('utf-8'),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)
print(f"Signature generated: {len(signature)} bytes")

# Load instructor public key
with open('instructor_public.pem', 'rb') as f:
    instructor_public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

# Encrypt signature with instructor's public key
print("Encrypting signature with instructor's public key...")
encrypted_signature = instructor_public_key.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Base64 encode
encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode('utf-8')

print("\n" + "="*60)
print("SUBMISSION INFORMATION")
print("="*60)
print(f"\nCommit Hash:")
print(commit_hash)
print(f"\nEncrypted Signature (copy for submission):")
print(encrypted_signature_b64)
print(f"\nSignature length: {len(encrypted_signature_b64)} characters")
print("\n" + "="*60)
print("Copy the encrypted signature above for your submission!")
print("="*60)
