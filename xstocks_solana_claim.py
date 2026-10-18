"""xStocks daily multiplier claim attempt for Solana wallets. CAPTCHA is not bypassed.""" 
import argparse, base64, getpass, hashlib, json, os, time
from pathlib import Path
from datetime import datetime
try:
    import requests
    from cryptography.fernet import Fernet
    from solders.keypair import Keypair
except ImportError:
    print("Install: py -m pip install requests cryptography solders base58")
    raise SystemExit(1)

API = "https://points-api.xstocks.fi/api/v1/xdrop-user/daily-spin-multiplier"
MESSAGE = "Reveal daily spin multiplier"
VAULT = Path(__file__).with_name("solana_wallets.vault")

def derive(password, salt):
    return base64.urlsafe_b64encode(hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000, dklen=32))

def parse_key(raw):
    raw = raw.strip()
    if raw.startswith("["):
        return Keypair.from_bytes(bytes(json.loads(raw)))
    import base58
    return Keypair.from_bytes(base58.b58decode(raw))

def log(msg):
    line = f"[{datetime.now().astimezone().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with Path(__file__).with_name("solana_claim_log.txt").open("a", encoding="utf-8") as f:
        f.write(line + "\\n")

def setup():
    if VAULT.exists():
        print(f"{VAULT.name} already exists; refusing to overwrite."); return
    pw = getpass.getpass("New vault password: ")
    if len(pw) < 12 or pw != getpass.getpass("Repeat vault password: "):
        print("Passwords must match and be at least 12 characters."); return
    salt = os.urandom(16); cipher = Fernet(derive(pw, salt)); wallets = []
    while True:
        address = input("Solana public address (blank to finish): ").strip()
        if not address: break
        secret = getpass.getpass("Solana secret key (hidden; base58 or JSON array): ").strip()
        try: kp = parse_key(secret)
        except Exception:
            print("Could not parse key; skipped."); continue
        if str(kp.pubkey()) != address:
            print(f"Address mismatch; key resolves to {kp.pubkey()}. Skipped."); continue
        wallets.append({"address": address, "secret": secret}); secret = None
        print(f"Added wallet #{len(wallets)}.")
    if not wallets: print("No wallets added."); return
    blob = cipher.encrypt(json.dumps(wallets).encode()).decode()
    VAULT.write_text(json.dumps({"salt": base64.b64encode(salt).decode(), "wallets": blob}, indent=2), encoding="utf-8")
    try: os.chmod(VAULT, 0o600)
    except OSError: pass
    print(f"Saved {len(wallets)} wallet(s) to password-encrypted {VAULT.name}.")

def load_wallets():
    if not VAULT.exists(): raise RuntimeError("Vault missing. Run: py xstocks_solana_claim.py --setup")
    pw = getpass.getpass("Vault password: "); data = json.loads(VAULT.read_text(encoding="utf-8"))
    try:
        cipher = Fernet(derive(pw, base64.b64decode(data["salt"])))
        return json.loads(cipher.decrypt(data["wallets"].encode()).decode())
    except Exception: raise RuntimeError("Wrong vault password or damaged vault.")

def claim(address, secret):
    kp = parse_key(secret); ts = int(time.time())
    msg = f"{MESSAGE} | {ts}".encode("utf-8")
    signature = str(kp.sign_message(msg))
    payload = {"walletAddress": address, "signature": signature, "signMethod": "message", "signTimestamp": ts}
    try:
        r = requests.put(API, json=payload, timeout=25)
        try: data = r.json()
        except ValueError: data = {"response": r.text[:250]}
        if r.status_code == 403 and isinstance(data, dict) and data.get("error") in ("captcha_required", "captcha_invalid"):
            log(f"{address}: CAPTCHA required; complete the official site flow.")
        elif r.ok and isinstance(data, dict) and data.get("success") is True:
            d = data.get("data") or {}
            log(f"{address}: SUCCESS multiplier={d.get('newDailySpinMultiplier')} points_delta={d.get('pointsDifference')}")
        else:
            log(f"{address}: FAILED HTTP {r.status_code}: {data.get('error', data) if isinstance(data, dict) else data}")
    except requests.RequestException as e: log(f"{address}: NETWORK ERROR: {e}")

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--setup", action="store_true"); args = parser.parse_args()
    if args.setup: setup(); return
    try: wallets = load_wallets()
    except Exception as e: print(e); return
    log(f"Starting one attempt for {len(wallets)} Solana wallet(s).")
    for i, w in enumerate(wallets):
        claim(w["address"], w["secret"])
        if i + 1 < len(wallets): time.sleep(2)
    log("Finished; verify results on xStocks Points page.")

if __name__ == "__main__": main()
