# AcademicPro Web

Flask site for academic support services. It includes public service pages, student client registration and orders, admin-managed order status, client/admin messaging, support chat, admin dashboards, blog/samples, OTP hooks, and AI chat endpoints.

## Local Start

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = "replace-this-for-local-dev"
$env:ADMIN_BOOTSTRAP_EMAIL = "admin@example.com"
$env:ADMIN_BOOTSTRAP_PASSWORD = "change-this-password"
.\.venv\Scripts\python.exe run.py
```

Open http://127.0.0.1:5000.

## Useful Checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```powershell
curl http://127.0.0.1:5000/health
```

## Required Production Settings

Set these environment variables on the host before launch:

- `SECRET_KEY`: long random secret.
- `SQLALCHEMY_DATABASE_URI` or `DATABASE_URL`: production database URL.
- `ADMIN_BOOTSTRAP_EMAIL`: first admin account email.
- `ADMIN_BOOTSTRAP_PASSWORD`: first admin password, then rotate after first login.
- `ADMIN_ONLY_MODE`: optional; set to `true` on a separate admin deployment to redirect public pages to `/staff-portal`.
- `EMAIL_OTP_ENABLED`: set to `true` only after email delivery is configured.
- `RESEND_API_KEY` and `RESEND_FROM_EMAIL`: needed for OTP email delivery if using Resend.
- `MAIL_USERNAME` and `MAIL_PASSWORD`: needed if using SMTP.
- `GROQ_API_KEY`: required for live Groq AI responses in the chat widget and AI API endpoints.
- `GROQ_MODEL`: optional model override; defaults to `llama-3.3-70b-versatile`.
- `GROQ_TIMEOUT`: optional Groq request timeout in seconds; defaults to `90`.
- `GROQ_MAX_TOKENS`: optional AI response cap; defaults to `6000`.

Do not run production with `FLASK_DEBUG=true`.

## Render Deployment Checklist

Set these in Render under **Environment** before redeploying:

- `GROQ_API_KEY`: your real Groq key.
- `ADMIN_BOOTSTRAP_EMAIL`: the email you will use at `/staff-portal`.
- `ADMIN_BOOTSTRAP_PASSWORD`: the password for that admin account.
- `ADMIN_EMAILS`: same admin email, or a comma-separated admin list.
- `SQLALCHEMY_DATABASE_URI` or `DATABASE_URL`: persistent production database.

After setting them, redeploy and check `/health`. It should report `groq_api_key: true` and `admin_bootstrap_email: true`.

## Launch Flow To Verify

1. Register a client account.
2. Place an order at `/order`.
3. Log in as an operator at `/staff-portal`.
4. Update the order status from the admin orders page.
5. Confirm the student can use `/orders/<id>/chat`.
6. Confirm admin can review the order thread and reply from the communication hub.
