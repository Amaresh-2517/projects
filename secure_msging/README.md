# Secure Messaging Web Application

Step‑by‑step secure messaging demo in Flask that grows from a basic hybrid crypto demo (Level 1) to a production‑style E2EE chat (Level 4). Current app runs the Level 4 UI by default, with Level 1/2 demo pages preserved for reference.

## Project Structure (repo root)

```
secure_msging/
├── app.py                 # Flask app + REST API
├── crypto_utils.py        # Hybrid crypto helpers (RSA-OAEP + AES-GCM, signatures, HMAC)
├── templates/             # HTML UIs (Level 4 default + Level 1/2 demos)
├── secure_chat.db         # SQLite DB (auto-created in repo or instance/)
└── instance/secure_chat.db
```

## Features by Level

### Level 1: Basic Encryption Demo
- RSA key pair generation
- Hybrid encryption (RSA + AES)
- Simple encrypt/decrypt demonstration

### Level 2: Two-User Chat System
- Multiple users with individual key pairs
- Encrypted message exchange
- In-memory message storage

### Level 3: Real End-to-End Encryption
- Client-side encryption/decryption (WebCrypto)
- Server stores only ciphertext + wrapped keys
- Public key exchange endpoints

### Level 4: Production-Level Secure Chat (default UI)
- Auth + registration (Flask-Login), bcrypt password hashing
- SQLite persistence
- Client-side E2EE (AES-GCM per message, RSA-OAEP key wrapping)
- Sender also wraps AES key for self (can read own messages)
- HMAC + RSA signatures stored alongside ciphertext
- Message timestamps

## Security Features

- Hybrid RSA-OAEP + AES-GCM per message
- Dual key wrap: AES key encrypted for receiver and for sender
- HMAC tag + RSA signature stored with each message
- Client-side crypto with WebCrypto; server never sees plaintext
- Passwords hashed with bcrypt

## Installation & Run

```bash
cd secure_msging
python3 -m venv .venv && source .venv/bin/activate
pip install flask cryptography flask-login flask-sqlalchemy bcrypt pyjwt
# optional: choose a port
PORT=5001 python3 app.py
```

Open http://127.0.0.1:5001 (or chosen port).

## Usage (Level 4 UI)

1) Register/login (one user per browser profile is simplest).
2) Keys are generated in-browser and stored in localStorage; public key is synced to the server.
3) Select a peer in the Users list, then send. New messages decrypt for both sender and receiver.
4) “Seed demo users” creates Alice/Bob (password `demo123`) and syncs their public keys.

## Security Architecture

- **RSA Keys**: 2048-bit for asymmetric encryption
- **AES Keys**: 256-bit for symmetric encryption
- **OAEP Padding**: For RSA encryption
- **PKCS7 Padding**: For AES encryption
- **SHA-256**: For hashing operations

## API (Level 4)

- `POST /api/register` `{username,password,publicKeyPem}` -> `{token}`
- `POST /api/login` `{username,password}` -> `{token, publicKeyPem}`
- `GET /api/pubkey/<username>` -> `{publicKeyPem,keyVersion}`
- `POST /api/message` (auth session) stores ciphertext, wrapped keys, HMAC, signature
- `GET /api/messages/<peer>` (auth session) returns encrypted thread
- `POST /api/keyupdate` `{publicKeyPem}` bumps key_version

## Database (current)

Users: id, username, password_hash, public_key_pem, key_version, created_at

Messages: id, sender_id, receiver_id, ciphertext, enc_key (for receiver), enc_key_sender (for sender), iv, hmac_tag, signature, key_version, timestamp

## Quick Test

1) Register two users in two browsers (e.g., Safari=Alice, Chrome=Bob) or click “Seed demo users”.
2) Select the other user and send “hello”.
3) Both sides should see plaintext; the sender sees their own message because `enc_key_sender` is used.

## Production Considerations

- Serve behind HTTPS with real certs; set a strong `SECRET_KEY` in env.
- Enforce key rotation per user (`key_version`) and expire old wraps.
- Add rate limiting, security headers, CSRF on forms, and a real JWT auth flow for APIs.
- Persist client keys securely (e.g., passphrase + IndexedDB) and add export/import for multi-device use.

## License

This project is for educational purposes demonstrating cryptographic concepts in web applications.
