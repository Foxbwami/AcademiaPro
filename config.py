import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URI") or os.environ.get("DATABASE_URL") or "sqlite:///your.db"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAILS = [
        e.strip().lower()
        for e in os.environ.get(
            "ADMIN_EMAILS",
            "bwamistevenez001@gmail.com",
        ).split(",")
        if e.strip()
    ]
    ADMIN_BOOTSTRAP_EMAIL = os.environ.get("ADMIN_BOOTSTRAP_EMAIL", "").strip().lower()
    ADMIN_BOOTSTRAP_PASSWORD = os.environ.get("ADMIN_BOOTSTRAP_PASSWORD", "")
    ADMIN_ONLY_MODE = os.environ.get("ADMIN_ONLY_MODE", "false").strip().lower() in ("1", "true", "yes", "on")
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
    RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "").strip()
    EMAIL_OTP_ENABLED = os.environ.get("EMAIL_OTP_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
    AUTO_ASSIGN_ADMIN_EMAILS = os.environ.get("AUTO_ASSIGN_ADMIN_EMAILS", "false").strip().lower() in ("1", "true", "yes", "on")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    GROQ_TIMEOUT = int(os.environ.get("GROQ_TIMEOUT", "90"))
    GROQ_MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "6000"))
    # Primary contact number for WhatsApp links. Store as international form, e.g. +447426105606
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "+447426105606").strip()
    ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg"}
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0

LOGIN_MESSAGE = "You must log in to access this page."
LOGIN_MESSAGE_CATEGORY = "warning"
