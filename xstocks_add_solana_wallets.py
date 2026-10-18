"""Safely add Solana wallets to an existing xStocks solana_wallets.vault."""
import base64, getpass, hashlib, json, os, shutil
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from solders.keypair import Keypair
except ImportError:
    print('Install dependencies first: py -m pip install cryptography solders base58')
    raise SystemExit(1)

VAULT = Path(__file__).with_name('solana_wallets.vault')

def derive(password, salt):
    return base64.urlsafe_b64encode(hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000, dklen=32))

def parse_key(raw):
    raw = raw.strip()
    if raw.startswith('['):
        return Keypair.from_bytes(bytes(json.loads(raw)))
    import base58
    return Keypair.from_bytes(base58.b58decode(raw))

def main():
    if not VAULT.exists():
        print(f'Cannot find {VAULT.name}. Put this script beside your existing vault.')
        return
    try:
        data = json.loads(VAULT.read_text(encoding='utf-8'))
        password = getpass.getpass('Existing Solana vault password: ')
        cipher = Fernet(derive(password, base64.b64decode(data['salt'])))
        wallets = json.loads(cipher.decrypt(data['wallets'].encode()).decode())
    except Exception:
        print('Could not unlock vault. Password may be wrong or the vault may be damaged. No changes made.')
        return

    existing = {w.get('address') for w in wallets}
    print(f'Unlocked existing vault: {len(wallets)} wallet(s).')
    added = 0
    while True:
        address = input('New Solana public address (blank to finish): ').strip()
        if not address:
            break
        if address in existing:
            print('That address is already in the vault; skipped.')
            continue
        secret = getpass.getpass('Private/secret key (hidden; base58 or JSON array): ').strip()
        try:
            kp = parse_key(secret)
        except Exception:
            print('Could not parse that secret key; skipped.')
            continue
        if str(kp.pubkey()) != address:
            print(f'Address does not match this key (key resolves to {kp.pubkey()}); skipped.')
            continue
        wallets.append({'address': address, 'secret': secret})
        existing.add(address)
        added += 1
        secret = None
        print(f'Added wallet. Total now: {len(wallets)}.')

    if not added:
        print('No new wallets added; vault unchanged.')
        return

    backup = VAULT.with_name('solana_wallets.vault.bak')
    if backup.exists():
        backup = VAULT.with_name('solana_wallets.vault.' + __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S') + '.bak')
    shutil.copy2(VAULT, backup)
    # Preserve the original salt and password-derived key, re-encrypt updated wallet list.
    data['wallets'] = cipher.encrypt(json.dumps(wallets).encode()).decode()
    temp = VAULT.with_suffix('.vault.tmp')
    temp.write_text(json.dumps(data, indent=2), encoding='utf-8')
    os.replace(temp, VAULT)
    try: os.chmod(VAULT, 0o600)
    except OSError: pass
    print(f'Saved {added} new wallet(s). Existing vault backed up to {backup.name}.')
    print('Run your normal Solana claim script to process all wallets. Keep the vault and backup private.')

if __name__ == '__main__':
    main()
