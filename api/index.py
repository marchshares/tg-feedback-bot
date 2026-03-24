import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request


load_dotenv()

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def extract_message_text(update: Dict[str, Any]) -> Optional[str]:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None

    if message.get("text"):
        return message["text"]

    if message.get("caption"):
        return f"[media]\n{message['caption']}"

    return "[unsupported message type]"


def send_to_owner(text: str) -> None:
    response = requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={
            "chat_id": OWNER_CHAT_ID,
            "text": text,
        },
        timeout=15,
    )
    response.raise_for_status()


@app.get("/")
def index():
    return jsonify(
        {
            "ok": True,
            "message": "Telegram webhook is running",
        }
    )


@app.post("/")
def webhook():
    if not TELEGRAM_BOT_TOKEN or not OWNER_CHAT_ID:
        return jsonify({"ok": False, "error": "Missing env vars"}), 500

    if WEBHOOK_SECRET:
        incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming_secret != WEBHOOK_SECRET:
            return jsonify({"ok": False, "error": "Unauthorized"}), 401

    update = request.get_json(silent=True) or {}
    message = update.get("message") or update.get("edited_message")
    if not message:
        return jsonify({"ok": True, "skipped": True})

    user = message.get("from", {})
    chat = message.get("chat", {})
    text = extract_message_text(update)

    forwarded_text = (
        "New message to bot\n\n"
        f"From: {user.get('first_name', 'Unknown')}"
        f" @{user.get('username', '-')}\n"
        f"User ID: {user.get('id', '-')}\n"
        f"Chat ID: {chat.get('id', '-')}\n\n"
        f"Text:\n{text or '[empty]'}"
    )

    try:
        send_to_owner(forwarded_text)
    except requests.RequestException as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500

    return jsonify({"ok": True})
