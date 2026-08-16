import os
import sys
import urllib.request
import json

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    print("No GEMINI_API_KEY found in environment.")
    sys.exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": "Say hello in exactly 3 words."}]}]
}
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req) as resp:
        print("SUCCESS:", resp.status)
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("FAILED:", e.code)
    print(e.read().decode())