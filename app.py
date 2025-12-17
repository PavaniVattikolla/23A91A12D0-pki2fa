from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import pyotp
import base64
import os
from pathlib import Path
import time

app = FastAPI()

SEED_FILE = Path("/data/seed.txt")
PRIVATE_KEY_FILE = Path("/app/student_private.pem")

class EncryptedSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def load_private_key():
    """Load student private key"""
    with open(PRIVATE_KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )

def decrypt_seed_data(encrypted_seed_b64: str) -> str:
    """Decrypt base64-encoded encrypted seed using RSA/OAEP"""
    private_key = load_private_key()
    
    # Decode from base64
    encrypted_data = base64.b64decode(encrypted_seed_b64)
    
    # Decrypt using RSA/OAEP with SHA-256
    decrypted = private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return decrypted.decode('utf-8')

def hex_to_base32(hex_seed: str) -> str:
    """Convert hex seed to base32 for TOTP"""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode('utf-8')

@app.post("/decrypt-seed")
async def decrypt_seed(request: EncryptedSeedRequest):
    """Decrypt and store seed"""
    try:
        # Decrypt the seed
        hex_seed = decrypt_seed_data(request.encrypted_seed)
        
        # Validate it's 64-character hex
        if len(hex_seed) != 64 or not all(c in '0123456789abcdef' for c in hex_seed):
            raise ValueError("Invalid seed format")
        
        # Ensure /data directory exists
        SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to persistent storage
        with open(SEED_FILE, "w") as f:
            f.write(hex_seed)
        
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed")

@app.get("/generate-2fa")
async def generate_2fa():
    """Generate current TOTP code"""
    try:
        if not SEED_FILE.exists():
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        
        # Read hex seed
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        
        # Convert to base32 and generate TOTP
        base32_seed = hex_to_base32(hex_seed)
        totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
        
        # Get current code
        code = totp.now()
        
        # Calculate remaining seconds
        current_time = int(time.time())
        valid_for = 30 - (current_time % 30)
        
        return {"code": code, "valid_for": valid_for}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/verify-2fa")
async def verify_2fa(request: VerifyRequest):
    """Verify TOTP code"""
    try:
        if not request.code:
            raise HTTPException(status_code=400, detail="Missing code")
        
        if not SEED_FILE.exists():
            raise HTTPException(status_code=500, detail="Seed not decrypted yet")
        
        # Read hex seed
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()
        
        # Convert to base32 and verify TOTP
        base32_seed = hex_to_base32(hex_seed)
        totp = pyotp.TOTP(base32_seed, interval=30, digits=6)
        
        # Verify with ±1 period tolerance (±30 seconds)
        is_valid = totp.verify(request.code, valid_window=1)
        
        return {"valid": is_valid}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
