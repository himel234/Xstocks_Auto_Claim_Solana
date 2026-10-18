

## What the files do

- `xstocks_solana_claim.py` — unlocks your encrypted wallet vault and attempts one claim per saved wallet.
- `xstocks_add_solana_wallets.py` — adds wallets to an existing encrypted vault.
- `solana_wallets.vault` — your encrypted wallet list. This file is created locally when you set up the vault; it is not included in this repository.
- `solana_claim_log.txt` — a local log created when the claim script runs.

Keep both the vault and any backup files private. **Never upload your vault, secret keys, or claim logs to GitHub.**

## Requirements

- Windows with Python installed (Python 3.10+ recommended).
- A Solana wallet and its matching secret key.
- Access to the official xStocks Points site.

Check Python in Command Prompt:

```cmd
py --version
```

## 1. Download the scripts

Download `xstocks_solana_claim.py` and `xstocks_add_solana_wallets.py` from the repository and place both files in the same folder, for example:

```text
C:\Users\YourName\xpoints_wallet_manager\
    xstocks_solana_claim.py
    xstocks_add_solana_wallets.py
```

Open Command Prompt in that folder.

## 2. Install dependencies

Run:

```cmd
py -m pip install requests cryptography solders base58
```

## 3. Create the encrypted vault (first-time setup only)

Run:

```cmd
py xstocks_solana_claim.py --setup
```

- Choose a strong vault password of at least 12 characters and confirm it.
- Enter a Solana public address.
- When prompted, enter that wallet's secret key. The prompt hides what you type.
- The script accepts a base58-encoded secret key or a JSON array of key bytes.
- Repeat for each wallet.
- Press **Enter on a blank public address** to finish.

The script checks that the public address matches the secret key before saving. The vault is encrypted with a password-derived key.

**Do not forget the vault password.** There is no password reset in this script. If you lose it, the encrypted vault cannot be unlocked.

## 4. Add more wallets later

If `solana_wallets.vault` already exists, **do not run setup again**. Instead, run:

```cmd
py xstocks_add_solana_wallets.py
```

- Enter your existing vault password.
- Enter each new public address and its matching secret key.
- Press **Enter on a blank address** when finished.

The add-wallet script skips duplicate addresses and checks that each secret key matches its address. Before saving, it creates a backup such as `solana_wallets.vault.bak`. Keep that backup private too.

If the script says it cannot unlock the vault, it makes no changes. Check that you are in the correct folder and that you entered the correct password.

## 5. Run daily claim attempts

Run:

```cmd
py xstocks_solana_claim.py
```

Enter the vault password when prompted. The script attempts one claim for each wallet saved in the vault and writes results to `solana_claim_log.txt`.

- `SUCCESS` means the API returned a success response; verify the result on the official xStocks Points page.
- `CAPTCHA required` means you must complete the official verification flow on the xStocks site.
- `FAILED` means the API rejected the request or returned another error. Read the message and check the official site.
- `NETWORK ERROR` means the request could not complete due to a connection problem.

A successful HTTP response is not a guarantee of future claims, eligibility, or points. The platform may change its API or requirements.

## Security checklist

- Never share your private/secret keys or vault password with anyone.
- Never commit `solana_wallets.vault`, `*.bak`, `*.tmp`, or `solana_claim_log.txt` to GitHub.
- Keep a secure offline backup of the vault. Remember that a backup contains encrypted wallet data, but should still be treated as sensitive.
- Use a strong, unique vault password.
- Only use wallets you own or are authorized to manage.
- Do not attempt to bypass CAPTCHA or other platform security checks.

### Suggested `.gitignore`

Create a file named `.gitignore` in the repository and add:

```gitignore
solana_wallets.vault
solana_wallets.vault.*
*.bak
*.tmp
solana_claim_log.txt
__pycache__/
.venv/
venv/
.env
```

## Troubleshooting

**`ModuleNotFoundError`**  
Run the dependency installation command again using the same Python launcher (`py`).

**`Vault missing`**  
Make sure `solana_wallets.vault` is in the same folder as `xstocks_solana_claim.py`. For a new vault, follow Section 3.

**`Wrong vault password or damaged vault`**  
Check the password and confirm you are using the correct vault file. Do not delete the vault.

**`Address does not match this key`**  
Confirm that the public address and secret key belong to the same Solana wallet. Never paste your secret key into an issue, discussion, or chat.

**Claim fails or CAPTCHA is required**  
Check the official xStocks site and complete any required verification there. The script is experimental and may stop working if the platform changes its API.

## Disclaimer

This is an unofficial community utility, not an official xStocks product. Use it at your own risk and review the platform's rules before use. No claim, multiplier, or reward is guaranteed.
"""

output_path = "/mnt/data/README_xstocks_solana.md"
pypandoc.convert_text(guide, "md", format="md", outputfile=output_path, extra_args=["--standalone"])
print(f"Created {output_path}")
