import hashlib
import hmac
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

ENDPOINT = "https://b12.io/apply/submission"
SIGNING_SECRET = os.environ["B12_SIGNING_SECRET"]

payload = {
    "action_run_link": os.environ["ACTION_RUN_LINK"],
    "email": os.environ["APPLICANT_EMAIL"],
    "name": os.environ["APPLICANT_NAME"],
    "repository_link": os.environ["REPOSITORY_LINK"],
    "resume_link": os.environ["RESUME_LINK"],
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z",
}

body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

signature = hmac.new(
    SIGNING_SECRET.encode("utf-8"),
    body,
    hashlib.sha256,
).hexdigest()

req = urllib.request.Request(
    ENDPOINT,
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        response = json.loads(resp.read().decode("utf-8"))
        if response.get("success"):
            print(f"Submission successful! Receipt: {response['receipt']}")
        else:
            print(f"Unexpected response: {response}", file=sys.stderr)
            sys.exit(1)
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
    sys.exit(1)
