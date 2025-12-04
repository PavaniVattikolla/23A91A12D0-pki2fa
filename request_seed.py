import json
import requests

student_id = "23A91A12D0"
github_repo_url = "https://github.com/PavaniVattikolla/23A91A12D0-pki2fa"
api_url = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws/"

# Read the public key exactly as-is (keep newlines)
with open("student_public.pem", "r") as f:
    public_key = f.read().strip()

payload = {
    "student_id": student_id,
    "github_repo_url": github_repo_url,
    "public_key": public_key
}

response = requests.post(api_url, json=payload)
data = response.json()

if "encrypted_seed" in data:
    with open("encrypted_seed.txt", "w") as f:
        f.write(data["encrypted_seed"])
    print("Encrypted seed saved to encrypted_seed.txt")
else:
    print("Error:", data)
