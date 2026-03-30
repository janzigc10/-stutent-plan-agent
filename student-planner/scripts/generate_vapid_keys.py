"""Generate a VAPID key pair for Web Push.

Run once:
    python scripts/generate_vapid_keys.py

Copy the output into your .env or environment variables.
"""

from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

print("Add these to your environment:\n")
print(f'SP_VAPID_PRIVATE_KEY="{vapid.private_pem().decode().strip()}"')
print(f'SP_VAPID_PUBLIC_KEY="{vapid.public_key_urlsafe_base64()}"')
print('SP_VAPID_CLAIMS_EMAIL="mailto:admin@studentplanner.local"')