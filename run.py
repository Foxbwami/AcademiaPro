import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.logger.info("Starting app on %s:%s", host, port)
    app.logger.info("GROQ_API_KEY set: %s", bool(app.config.get("GROQ_API_KEY")))
    app.logger.info("ADMIN_BOOTSTRAP_EMAIL set: %s", bool(app.config.get("ADMIN_BOOTSTRAP_EMAIL")))
    app.logger.info("ADMIN_ONLY_MODE: %s", app.config.get("ADMIN_ONLY_MODE"))
    app.run(host=host, port=port, debug=debug)
