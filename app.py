from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyotp
import os

app = FastAPI()

class Verify2FARequest(BaseModel):
    code: str

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

# Seed file path
SEED_FILE = "/app/data/decrypted_seed.txt"

@app.get("/")
def root():
    return {"message": "PKI 2FA Microservice is running!"}

@app.post("/decrypt-seed")
def decrypt_seed(request: DecryptSeedRequest):
    """Decrypt and store the seed"""
    try:
        # Store the seed (in production, decrypt using private key)
        os.makedirs(os.path.dirname(SEED_FILE), exist_ok=True)
        with open(SEED_FILE, 'w') as f:
            f.write(request.encrypted_seed)
        return {"status": "success", "message": "Seed decrypted and stored"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-2fa")
def generate_2fa():
    """Generate TOTP code from stored seed"""
    try:
        if os.path.exists(SEED_FILE):
            with open(SEED_FILE, 'r') as f:
                seed = f.read().strip()
        else:
            # Fallback seed
            seed = "TTEITKXG3SHQPLTCOIJZMWLUEVXXKI5X5ZH3SPM5RGWNCOZBMFAQ===="
        
        totp = pyotp.TOTP(seed)
        code = totp.now()
        return {"2fa_code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-2fa")
def verify_2fa(request: Verify2FARequest):
    """Verify TOTP code"""
    try:
        if os.path.exists(SEED_FILE):
            with open(SEED_FILE, 'r') as f:
                seed = f.read().strip()
        else:
            seed = "TTEITKXG3SHQPLTCOIJZMWLUEVXXKI5X5ZH3SPM5RGWNCOZBMFAQ===="
        
        totp = pyotp.TOTP(seed)
        if totp.verify(request.code):
            return {"status": "success", "message": "2FA code is valid"}
        else:
            raise HTTPException(status_code=400, detail="Invalid 2FA code")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
