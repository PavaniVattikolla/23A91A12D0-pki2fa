from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pyotp

app = FastAPI()

class Verify2FARequest(BaseModel):
    code: str

# Use the Base32 seed directly
seed = "TTEITKXG3SHQPLTCOIJZMWLUEVXXKI5X5ZH3SPM5RGWNCOZBMFAQ===="
totp = pyotp.TOTP(seed)

@app.get("/")
def root():
    return {"message": "PKI 2FA Microservice is running!"}

@app.get("/generate-2fa")
def generate_2fa():
    code = totp.now()
    return {"2fa_code": code}

@app.post("/verify-2fa")
def verify_2fa(request: Verify2FARequest):
    if totp.verify(request.code):
        return {"status": "success", "message": "2FA code is valid"}
    else:
        raise HTTPException(status_code=400, detail="Invalid 2FA code")
