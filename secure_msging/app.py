"""Secure Messaging Demo covering Levels 1-4.

Level 4 (default) uses client-side E2EE; server stores only ciphertext.
Level 1/2 demo routes are kept for educational purposes.
"""

import base64
import datetime
import os
import time
from typing import Optional

import bcrypt
import jwt
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import and_, or_

from crypto_utils import HybridPayload, generate_rsa_keys, hybrid_decrypt, hybrid_encrypt, serialize_public_key


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///secure_chat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# ------------------------- Models -------------------------


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    public_key_pem = db.Column(db.Text, nullable=False)
    key_version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ciphertext = db.Column(db.Text, nullable=False)
    enc_key = db.Column(db.Text, nullable=False)
    enc_key_sender = db.Column(db.Text, nullable=True)
    iv = db.Column(db.Text, nullable=False)
    hmac_tag = db.Column(db.Text, nullable=True)
    signature = db.Column(db.Text, nullable=True)
    key_version = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def ensure_tables():
    db.create_all()
    # lightweight migration: add enc_key_sender if missing
    insp = db.inspect(db.engine)
    cols = [c["name"] for c in insp.get_columns("message")]
    if "enc_key_sender" not in cols:
        with db.engine.begin() as conn:
            conn.execute(db.text("ALTER TABLE message ADD COLUMN enc_key_sender TEXT"))


# ------------------------- Auth helpers -------------------------


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def issue_jwt(user: User) -> str:
    payload = {"sub": user.id, "name": user.username, "exp": time.time() + 3600}
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def current_user_from_token(token: str) -> Optional[User]:
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except Exception:
        return None
    return User.query.get(int(data["sub"]))


# ------------------------- Routes: HTML pages -------------------------


@app.route("/")
@login_required
def index():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template("index.html", users=users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            login_user(user)
            return redirect(url_for("index"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        public_key_pem = request.form.get("public_key_pem")

        if not public_key_pem:
            return render_template("register.html", error="Public key missing. Allow the page to generate keys." )
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")

        user = User(
            username=username,
            password_hash=hash_password(password),
            public_key_pem=public_key_pem,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ------------------------- Routes: Level 1 & 2 demos -------------------------


@app.route("/level1", methods=["GET", "POST"])
def level1():
    result = None
    if request.method == "POST":
        msg = request.form.get("message", "")
        priv, pub = generate_rsa_keys()
        payload = hybrid_encrypt(msg, pub)
        decrypted = hybrid_decrypt(payload, priv)
        result = {
            "ciphertext": payload.ciphertext_b64,
            "enc_key": payload.enc_key_b64,
            "iv": payload.iv_b64,
            "decrypted": decrypted,
        }
    return render_template("level1.html", result=result)


# Level 2 keeps two fixed users server-side and decrypts for receiver
priv_a, pub_a = generate_rsa_keys()
priv_b, pub_b = generate_rsa_keys()
level2_msgs = []


@app.route("/level2", methods=["GET", "POST"])
def level2():
    global level2_msgs
    if request.method == "POST":
        sender = request.form.get("sender")
        receiver = request.form.get("receiver")
        msg = request.form.get("message")
        recv_pub = pub_a if receiver == "Alice" else pub_b
        payload = hybrid_encrypt(msg, recv_pub)
        level2_msgs.append({"sender": sender, "receiver": receiver, "payload": payload})

    view = []
    for item in level2_msgs:
        priv = priv_a if item["receiver"] == "Alice" else priv_b
        decrypted = hybrid_decrypt(item["payload"], priv)
        view.append({**item, "decrypted": decrypted})
    return render_template("level2.html", messages=view)


# ------------------------- Routes: API (Level 4) -------------------------


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    public_key_pem = data.get("publicKeyPem")

    if User.query.filter_by(username=username).first():
        return {"error": "exists"}, 400

    user = User(username=username, password_hash=hash_password(password), public_key_pem=public_key_pem)
    db.session.add(user)
    db.session.commit()
    token = issue_jwt(user)
    return {"token": token}


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        return {"error": "bad creds"}, 401
    token = issue_jwt(user)
    login_user(user)  # also create session for HTML
    return {"token": token, "publicKeyPem": user.public_key_pem}


@app.route("/api/pubkey/<username>")
def api_pubkey(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {"error": "not found"}, 404
    return {"publicKeyPem": user.public_key_pem, "keyVersion": user.key_version}


@app.route("/api/message", methods=["POST"])
@login_required
def api_message():
    user = current_user
    data = request.get_json()
    receiver_name = data.get("receiver")
    receiver = User.query.filter_by(username=receiver_name).first()
    if not receiver:
        app.logger.warning("api_message receiver not found: %s", receiver_name)
        return {"error": "receiver"}, 404

    app.logger.info("api_message from %s to %s", user.username, receiver.username)
    msg = Message(
        sender_id=user.id,
        receiver_id=receiver.id,
        ciphertext=data.get("ciphertext"),
        enc_key=data.get("encKey"),
        enc_key_sender=data.get("encKeySender"),
        iv=data.get("iv"),
        hmac_tag=data.get("hmac"),
        signature=data.get("signature"),
        key_version=data.get("keyVersion", 1),
    )
    db.session.add(msg)
    db.session.commit()
    return {"status": "stored"}


@app.route("/api/messages/<peer>")
@login_required
def api_messages(peer):
    user = current_user
    peer_user = User.query.filter_by(username=peer).first()
    if not peer_user:
        return {"error": "peer"}, 404

    rows = (
        Message.query.filter(
            or_(
                and_(Message.sender_id == user.id, Message.receiver_id == peer_user.id),
                and_(Message.sender_id == peer_user.id, Message.receiver_id == user.id),
            )
        )
        .order_by(Message.timestamp.asc())
        .all()
    )
    payload = []
    for r in rows:
        payload.append(
            {
                "id": r.id,
                "sender": User.query.get(r.sender_id).username,
                "receiver": User.query.get(r.receiver_id).username,
                "ciphertext": r.ciphertext,
                "enc_key": r.enc_key,
                "enc_key_sender": r.enc_key_sender,
                "iv": r.iv,
                "hmac": r.hmac_tag,
                "signature": r.signature,
                "ts": int(r.timestamp.timestamp()),
                "keyVersion": r.key_version,
            }
        )
    return jsonify(payload)


@app.route("/api/keyupdate", methods=["POST"])
@login_required
def api_keyupdate():
    user = current_user
    data = request.get_json()
    new_pub = data.get("publicKeyPem")
    if not new_pub:
        return {"error": "missing key"}, 400
    user.public_key_pem = new_pub
    user.key_version = user.key_version + 1
    db.session.commit()
    return {"status": "updated", "keyVersion": user.key_version}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
