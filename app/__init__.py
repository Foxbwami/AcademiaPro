import os
import re
import shutil
from flask import Flask, Response, request, url_for
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, generate_csrf
from app.extensions import db, login_manager, migrate
from app.models import User, Message, BlogPost, AIConversationMessage, OTPCode
from flask_login import current_user
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

mail = Mail()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    if os.environ.get("RENDER", "").strip().lower() in ("1", "true", "yes", "on") and not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY must be set in the Render environment before starting AcademiaPro.")
    login_manager.init_app(app)

    # Email configuration
    app.config.setdefault('MAIL_SERVER', 'smtp.gmail.com')
    app.config.setdefault('MAIL_PORT', 587)
    app.config.setdefault('MAIL_USE_TLS', True)
    app.config.setdefault('MAIL_USERNAME', '')
    app.config.setdefault('MAIL_PASSWORD', '')
    app.config.setdefault('MAIL_TIMEOUT', 10)
    app.config.setdefault('MAIL_MAX_EMAILS', 5)
    app.config.setdefault('MAIL_DEFAULT_SENDER', app.config.get('MAIL_USERNAME') or 'noreply@academicpro.local')

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    @app.after_request
    def add_csrf_tokens_to_post_forms(response):
        # Legacy plain HTML forms receive a token unless Flask-WTF already added one.
        if response.mimetype != 'text/html':
            return response
        try:
            html = response.get_data(as_text=True)
            token = generate_csrf()
            form_pattern = re.compile(r"(<form\b[^>]*>)(.*?)(</form>)", re.IGNORECASE | re.DOTALL)
            def inject_token(match):
                opening, body, closing = match.groups()
                method_match = re.search(r"\bmethod\s*=\s*['\"]?([^\s'\"]+)", opening, re.IGNORECASE)
                if not method_match or method_match.group(1).lower() != 'post':
                    return match.group(0)
                if re.search(r"name\s*=\s*['\"]csrf_token['\"]", body, re.IGNORECASE):
                    return match.group(0)
                field = '<input type="hidden" name="csrf_token" value="' + token + '">'
                return opening + field + body + closing
            response.set_data(form_pattern.sub(inject_token, html))
        except (RuntimeError, ValueError):
            app.logger.exception('Unable to add CSRF tokens to rendered forms')
        return response

    with app.app_context():
        # Best-effort compatibility for existing SQLite deployments where
        # model fields/tables were added without a matching migration chain.
        db.create_all()
        # Move legacy root uploads out of Flask's public static directory.
        legacy_uploads = os.path.join(app.static_folder, 'uploads')
        private_uploads = os.environ.get('PRIVATE_UPLOAD_DIR') or os.path.join(app.instance_path, 'private_uploads')
        profile_uploads = os.path.join(legacy_uploads, 'profiles')
        os.makedirs(private_uploads, exist_ok=True)
        os.makedirs(profile_uploads, exist_ok=True)
        profile_names = {
            name for (name,) in db.session.query(User.photo).filter(User.photo.isnot(None)).all()
            if name
        }
        if os.path.isdir(legacy_uploads):
            for entry in os.scandir(legacy_uploads):
                if not entry.is_file():
                    continue
                destination_dir = profile_uploads if entry.name in profile_names else private_uploads
                destination = os.path.join(destination_dir, entry.name)
                if not os.path.exists(destination):
                    shutil.move(entry.path, destination)
                else:
                    os.remove(entry.path)
            legacy_support = os.path.join(legacy_uploads, 'support')
            private_support = os.path.join(private_uploads, 'support')
            if os.path.isdir(legacy_support):
                os.makedirs(private_support, exist_ok=True)
                for entry in os.scandir(legacy_support):
                    if entry.is_file():
                        destination = os.path.join(private_support, entry.name)
                        if not os.path.exists(destination):
                            shutil.move(entry.path, destination)
                        else:
                            os.remove(entry.path)
        inspector = inspect(db.engine)
        if "order" in inspector.get_table_names():
            order_columns = {col["name"] for col in inspector.get_columns("order")}
            order_additions = [
                ("assigned_at", "ALTER TABLE \"order\" ADD COLUMN assigned_at DATETIME"),
                ("task_type", "ALTER TABLE \"order\" ADD COLUMN task_type VARCHAR(60)"),
                ("price", "ALTER TABLE \"order\" ADD COLUMN price FLOAT"),
                ("service_track", "ALTER TABLE \"order\" ADD COLUMN service_track VARCHAR(50) DEFAULT 'writing'"),
                ("citation_style", "ALTER TABLE \"order\" ADD COLUMN citation_style VARCHAR(30)"),
                ("sources_count", "ALTER TABLE \"order\" ADD COLUMN sources_count INTEGER"),
                ("currency", "ALTER TABLE \"order\" ADD COLUMN currency VARCHAR(10)"),
                ("timezone", "ALTER TABLE \"order\" ADD COLUMN timezone VARCHAR(50)"),
            ]
            for col_name, sql in order_additions:
                if col_name not in order_columns:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        if "message" in inspector.get_table_names():
            message_columns = {col["name"] for col in inspector.get_columns("message")}
            if "is_read" not in message_columns:
                db.session.execute(text("ALTER TABLE message ADD COLUMN is_read BOOLEAN DEFAULT 0 NOT NULL"))
                db.session.commit()
        if "user" in inspector.get_table_names():
            user_columns = {col["name"] for col in inspector.get_columns("user")}
            if "role" not in user_columns:
                db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'client' NOT NULL"))
                db.session.commit()
            if "email_verified" not in user_columns:
                try:
                    db.session.execute(text("ALTER TABLE \"user\" ADD COLUMN email_verified BOOLEAN DEFAULT FALSE NOT NULL"))
                    db.session.commit()
                except Exception:
                    db.session.rollback()
            user_additions = [
                ("phone", "ALTER TABLE user ADD COLUMN phone VARCHAR(30)"),
                ("academic_level", "ALTER TABLE user ADD COLUMN academic_level VARCHAR(50)"),
                ("expertise_tags", "ALTER TABLE user ADD COLUMN expertise_tags VARCHAR(255)"),
                ("two_factor_enabled", "ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0 NOT NULL"),
                ("profile_public", "ALTER TABLE user ADD COLUMN profile_public BOOLEAN DEFAULT 1 NOT NULL"),
                ("notify_email", "ALTER TABLE user ADD COLUMN notify_email BOOLEAN DEFAULT 1 NOT NULL"),
                ("notify_sms", "ALTER TABLE user ADD COLUMN notify_sms BOOLEAN DEFAULT 0 NOT NULL"),
                ("notify_in_app", "ALTER TABLE user ADD COLUMN notify_in_app BOOLEAN DEFAULT 1 NOT NULL"),
                ("alert_order_updates", "ALTER TABLE user ADD COLUMN alert_order_updates BOOLEAN DEFAULT 1 NOT NULL"),
                ("alert_payment_confirmations", "ALTER TABLE user ADD COLUMN alert_payment_confirmations BOOLEAN DEFAULT 1 NOT NULL"),
                ("alert_revision_requests", "ALTER TABLE user ADD COLUMN alert_revision_requests BOOLEAN DEFAULT 1 NOT NULL"),
                ("alert_admin_announcements", "ALTER TABLE user ADD COLUMN alert_admin_announcements BOOLEAN DEFAULT 1 NOT NULL"),
                ("billing_method", "ALTER TABLE user ADD COLUMN billing_method VARCHAR(50)"),
                ("payout_method", "ALTER TABLE user ADD COLUMN payout_method VARCHAR(50)"),
                ("auto_deposit_notifications", "ALTER TABLE user ADD COLUMN auto_deposit_notifications BOOLEAN DEFAULT 0 NOT NULL"),
                ("preferred_language", "ALTER TABLE user ADD COLUMN preferred_language VARCHAR(50)"),
                ("timezone", "ALTER TABLE user ADD COLUMN timezone VARCHAR(50)"),
                ("preferred_channel", "ALTER TABLE user ADD COLUMN preferred_channel VARCHAR(30)"),
                ("layout_mode", "ALTER TABLE user ADD COLUMN layout_mode VARCHAR(20)"),
                ("citation_style", "ALTER TABLE user ADD COLUMN citation_style VARCHAR(30)"),
                ("marketing_opt_in", "ALTER TABLE user ADD COLUMN marketing_opt_in BOOLEAN DEFAULT 0 NOT NULL"),
            ]
            for col_name, sql in user_additions:
                if col_name not in user_columns:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        if "sample" in inspector.get_table_names():
            sample_columns = {col["name"] for col in inspector.get_columns("sample")}
            sample_additions = [
                ("style", "ALTER TABLE sample ADD COLUMN style VARCHAR(50)"),
                ("level", "ALTER TABLE sample ADD COLUMN level VARCHAR(50)"),
                ("subject", "ALTER TABLE sample ADD COLUMN subject VARCHAR(100)"),
                ("grade", "ALTER TABLE sample ADD COLUMN grade VARCHAR(50)"),
                ("published_at", "ALTER TABLE sample ADD COLUMN published_at DATETIME"),
                ("source_url", "ALTER TABLE sample ADD COLUMN source_url VARCHAR(255)"),
                ("file_type", "ALTER TABLE sample ADD COLUMN file_type VARCHAR(20)"),
                ("file_name", "ALTER TABLE sample ADD COLUMN file_name VARCHAR(255)"),
            ]
            for col_name, sql in sample_additions:
                if col_name not in sample_columns:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        if "blog_post" in inspector.get_table_names():
            blog_columns = {col["name"] for col in inspector.get_columns("blog_post")}
            blog_additions = [
                ("excerpt", "ALTER TABLE blog_post ADD COLUMN excerpt TEXT"),
                ("category", "ALTER TABLE blog_post ADD COLUMN category VARCHAR(80) DEFAULT 'Academic Skills' NOT NULL"),
                ("pillar", "ALTER TABLE blog_post ADD COLUMN pillar VARCHAR(120)"),
                ("cluster_topic", "ALTER TABLE blog_post ADD COLUMN cluster_topic VARCHAR(120)"),
                ("author_id", "ALTER TABLE blog_post ADD COLUMN author_id INTEGER"),
                ("author_name", "ALTER TABLE blog_post ADD COLUMN author_name VARCHAR(120)"),
                ("is_published", "ALTER TABLE blog_post ADD COLUMN is_published BOOLEAN DEFAULT TRUE NOT NULL"),
                ("updated_at", "ALTER TABLE blog_post ADD COLUMN updated_at DATETIME"),
            ]
            for col_name, sql in blog_additions:
                if col_name not in blog_columns:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        if "ai_conversation_message" not in inspector.get_table_names():
            try:
                db.session.execute(text(
                    "CREATE TABLE ai_conversation_message ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id INTEGER, "
                    "guest_thread_id VARCHAR(64), "
                    "role VARCHAR(20) NOT NULL, "
                    "content TEXT NOT NULL, "
                    "created_at DATETIME, "
                    "FOREIGN KEY(user_id) REFERENCES user(id))"
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()
        else:
            ai_columns = {col["name"] for col in inspector.get_columns("ai_conversation_message")}
            ai_additions = [
                ("user_id", "ALTER TABLE ai_conversation_message ADD COLUMN user_id INTEGER"),
                ("guest_thread_id", "ALTER TABLE ai_conversation_message ADD COLUMN guest_thread_id VARCHAR(64)"),
                ("role", "ALTER TABLE ai_conversation_message ADD COLUMN role VARCHAR(20) DEFAULT 'assistant' NOT NULL"),
                ("content", "ALTER TABLE ai_conversation_message ADD COLUMN content TEXT DEFAULT '' NOT NULL"),
                ("created_at", "ALTER TABLE ai_conversation_message ADD COLUMN created_at DATETIME"),
            ]
            for col_name, sql in ai_additions:
                if col_name not in ai_columns:
                    try:
                        db.session.execute(text(sql))
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
        if "otp_code" not in inspector.get_table_names():
            try:
                db.session.execute(text(
                    "CREATE TABLE otp_code ("
                    "id INTEGER PRIMARY KEY, "
                    "user_id INTEGER, "
                    "email VARCHAR(120) NOT NULL, "
                    "purpose VARCHAR(40) NOT NULL, "
                    "code VARCHAR(8) NOT NULL, "
                    "is_used BOOLEAN DEFAULT FALSE NOT NULL, "
                    "expires_at DATETIME NOT NULL, "
                    "created_at DATETIME NOT NULL, "
                    "FOREIGN KEY(user_id) REFERENCES user(id))"
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()
        if app.config.get("AUTO_ASSIGN_ADMIN_EMAILS", False):
            admin_emails = {e.strip().lower() for e in app.config.get("ADMIN_EMAILS", []) if e.strip()}
            if admin_emails:
                users = User.query.filter(User.email.in_(list(admin_emails))).all()
                for user in users:
                    user.role = "admin"
                if users:
                    db.session.commit()
        bootstrap_email = app.config.get("ADMIN_BOOTSTRAP_EMAIL", "")
        bootstrap_password = app.config.get("ADMIN_BOOTSTRAP_PASSWORD", "")
        if bootstrap_email and bootstrap_password:
            admin = User.query.filter_by(email=bootstrap_email).first()
            if not admin:
                app.logger.info("Bootstrapping admin user for %s", bootstrap_email)
                admin = User(email=bootstrap_email, name="Admin", password_hash=generate_password_hash(bootstrap_password), role="admin")
                db.session.add(admin)
            else:
                app.logger.info("Updating bootstrap admin credentials for %s", bootstrap_email)
                admin.password_hash = generate_password_hash(bootstrap_password)
                admin.role = "admin"
            db.session.commit()
        else:
            app.logger.warning(
                "ADMIN_BOOTSTRAP_EMAIL or ADMIN_BOOTSTRAP_PASSWORD is not configured; admin bootstrap skipped."
            )

        app.logger.info(
            "ADMIN_BOOTSTRAP_EMAIL present: %s | ADMIN_ONLY_MODE: %s",
            bool(app.config.get("ADMIN_BOOTSTRAP_EMAIL")),
            app.config.get("ADMIN_ONLY_MODE", False),
        )
        app.logger.info(
            "GROQ_API_KEY present: %s | GROQ_MODEL: %s",
            bool(app.config.get("GROQ_API_KEY")),
            app.config.get("GROQ_MODEL"),
        )

        if not app.config.get("GROQ_API_KEY"):
            app.logger.warning(
                "GROQ_API_KEY is not configured; AI endpoints will fall back to unavailable provider behavior."
            )

        if BlogPost.query.count() == 0:
            seed_posts = [
                BlogPost(
                    title="The Ultimate Guide to Mastering Grade 12 Exams",
                    excerpt="A practical framework for revision planning, mock strategy, and exam-day execution.",
                    category="Exam Strategy",
                    pillar="Grade 12 Mastery",
                    cluster_topic="Foundation",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Grade 12 exam success is rarely about studying longer. It is about studying with structure.\n\n"
                        "Start by building a subject map: list each subject, the weight of every unit, and your current confidence level. "
                        "Rank topics into three groups: strong, moderate, and weak. Your weekly plan should spend most time on weak areas while still revising strong ones to keep recall sharp.\n\n"
                        "Use a 3-cycle revision model.\n"
                        "Cycle 1: Concept review. Summarize each topic into one-page notes with definitions, formulas, and common traps.\n"
                        "Cycle 2: Active recall. Close notes and answer questions from memory, then check errors.\n"
                        "Cycle 3: Timed papers. Simulate exam conditions to train speed, calmness, and accuracy.\n\n"
                        "For each mock, run a post-mock audit. Record every error under one of these labels: knowledge gap, misread question, time pressure, or careless slip. "
                        "Fixing the error type is more effective than just redoing questions randomly.\n\n"
                        "In the final week, reduce new content. Focus on high-yield summaries, formula sheets, and repeated weak-question types. "
                        "Sleep consistency and short review blocks will help retention better than all-night sessions.\n\n"
                        "Exam day checklist: arrive early, read instructions once fully, allocate time per section before writing, and leave final minutes for targeted checking. "
                        "Discipline in execution often decides the final grade."
                    ),
                ),
                BlogPost(
                    title="8 Common Calculus Mistakes and How to Avoid Them",
                    excerpt="A mistake-by-mistake breakdown to improve marks quickly in derivatives, integrals, and limits.",
                    category="STEM Skills",
                    pillar="Grade 12 Mastery",
                    cluster_topic="Calculus",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Most calculus losses come from repeated patterns, not hard theory.\n\n"
                        "1) Sign errors during expansion. Slow down when distributing negatives and use one line per transformation.\n"
                        "2) Misusing chain rule. If a function is nested, include inner derivative every time.\n"
                        "3) Product/quotient confusion. Memorize form and keep numerator in brackets before simplifying.\n"
                        "4) Ignoring domain restrictions. Check values that make denominators zero or roots invalid.\n"
                        "5) Skipping constant of integration. Always add +C for indefinite integrals.\n"
                        "6) Poor limit notation. Show substitution and algebraic steps clearly to avoid logic gaps.\n"
                        "7) Unit blindness in applications. State units in rates, areas, and optimization outputs.\n"
                        "8) No verification pass. Re-differentiate antiderivatives and test critical points.\n\n"
                        "Build a personal error ledger. After each set, log mistake type, why it happened, and correction rule. "
                        "In 2-3 weeks, this approach can reduce avoidable losses dramatically."
                    ),
                ),
                BlogPost(
                    title="How to Write a Thesis Without Burnout",
                    excerpt="Use milestone planning, realistic writing targets, and feedback loops to finish strong.",
                    category="Research Writing",
                    pillar="Thesis Writing",
                    cluster_topic="Workflow",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Thesis burnout usually starts when planning is vague. Convert your thesis into concrete milestones: proposal, literature review, methods, results, discussion, final edits.\n\n"
                        "Set weekly deliverables with measurable outputs, such as words drafted, sources annotated, or figures finalized. "
                        "Avoid goals like 'work on chapter 2' and use 'complete section 2.1 with three cited sources'.\n\n"
                        "Use deep-work blocks of 60-90 minutes with short breaks. Protect two high-focus blocks each day for writing and one low-focus block for formatting, references, or admin tasks.\n\n"
                        "Build a supervisor feedback loop every 1-2 weeks. Smaller review cycles prevent major rewrites at the end.\n\n"
                        "When stuck, switch task type instead of forcing output. Move from drafting to outlining, or from analysis to source organization. "
                        "Momentum matters more than perfect flow.\n\n"
                        "Your final month should prioritize argument clarity, coherence between chapters, citation consistency, and formatting compliance. "
                        "A finished good draft is stronger than an unfinished perfect chapter."
                    ),
                ),
                BlogPost(
                    title="APA vs MLA vs Chicago: Practical Comparison for Students",
                    excerpt="Quick rules and examples to choose the right style and avoid formatting penalties.",
                    category="Citation & Integrity",
                    pillar="Citation Mastery",
                    cluster_topic="Style Comparison",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Choosing the right citation style depends on discipline and institutional guidelines.\n\n"
                        "APA is common in social sciences. It uses author-date citations and emphasizes publication year relevance.\n"
                        "MLA is frequent in humanities. It uses author-page citations and focuses on textual analysis.\n"
                        "Chicago appears in history and business contexts, often with notes-bibliography format.\n\n"
                        "Common penalties come from inconsistent in-text format, missing bibliography details, and incorrect capitalization rules.\n\n"
                        "Before writing, set your style once and keep a template for title page, headings, and references. "
                        "Use citation tools carefully and always validate output manually. Automated tools help speed, but human review ensures correctness.\n\n"
                        "Final check before submission: every in-text citation must match one reference entry, and every reference entry must be cited in text."
                    ),
                ),
                BlogPost(
                    title="Avoiding Plagiarism: A Student Guide to Safe Academic Writing",
                    excerpt="A practical method to paraphrase correctly, cite confidently, and protect originality.",
                    category="Citation & Integrity",
                    pillar="Citation Mastery",
                    cluster_topic="Plagiarism Prevention",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Plagiarism is often accidental when students copy structure or phrasing too closely.\n\n"
                        "Safe workflow:\n"
                        "1) Read source and close it.\n"
                        "2) Write idea in your own words from memory.\n"
                        "3) Reopen source to verify accuracy.\n"
                        "4) Add citation immediately.\n\n"
                        "Use direct quotes only for precise wording that must be preserved. Most academic writing should be paraphrased with attribution.\n\n"
                        "Track sources while drafting. Leaving citation to the end increases risk of lost references and weak attribution.\n\n"
                        "Before submission, run an originality check and inspect flagged sections manually. "
                        "Similarity is not automatically plagiarism; context matters, but uncited overlaps are always risky."
                    ),
                ),
                BlogPost(
                    title="Time Management for Exam Season: A 4-Week Plan",
                    excerpt="A realistic schedule framework to balance classes, revision, and recovery during peak pressure.",
                    category="Exam Strategy",
                    pillar="Grade 12 Mastery",
                    cluster_topic="Time Management",
                    author_name="AcademicPro Editorial Team",
                    is_published=True,
                    content=(
                        "Week 4: Build your plan. List all exams, topics, and current readiness. Assign daily blocks by priority.\n"
                        "Week 3: Start timed practice for high-weight subjects. Keep error logs after each session.\n"
                        "Week 2: Increase mixed-topic drills and memory recall sessions. Tighten weak topics.\n"
                        "Week 1: Reduce cognitive overload. Review summaries, formulas, and frequent error patterns.\n\n"
                        "Daily structure example:\n"
                        "Morning: high-focus study block.\n"
                        "Afternoon: practice questions and marking.\n"
                        "Evening: low-intensity recap and planning for next day.\n\n"
                        "Use a simple rule: do the most important difficult task first each day. "
                        "Consistency beats intensity, especially under exam pressure."
                    ),
                ),
            ]
            db.session.add_all(seed_posts)
            db.session.commit()

    @app.context_processor
    def inject_user():
        unread_count = 0
        if getattr(current_user, "is_authenticated", False):
            try:
                unread_count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
            except Exception:
                unread_count = 0
        # Inject WhatsApp number and other globals for templates
        whatsapp = app.config.get("WHATSAPP_NUMBER", "+447426105606")
        try:
            from flask import url_for
            order_href = url_for('main.order') if getattr(current_user, 'is_authenticated', False) else f"https://wa.me/{whatsapp.replace('+','')}?text=Hello%20AcademiaPro%20Admin%2C%20I'd%20like%20to%20place%20an%20order."
            consult_wa = f"https://wa.me/{whatsapp.replace('+','')}?text=Hello%20AcademiaPro%20Admin%2C%20I'd%20like%20to%20request%20a%20consultation."
        except Exception:
            order_href = '#'
            consult_wa = '#'
        consult_mailto = app.config.get('SUPPORT_EMAIL', 'support@academiapro.com')
        consult_mailto = f"mailto:{consult_mailto}?subject=AcademiaPro%20Consultation%20Request"
        return dict(current_user=current_user, unread_count=unread_count, WHATSAPP_NUMBER=whatsapp, ORDER_LINK=order_href, CONSULT_WA=consult_wa, CONSULT_MAILTO=consult_mailto)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes import main
    from app.route_modules.ai_routes import ai_bp
    app.register_blueprint(main)
    app.register_blueprint(ai_bp)


    # Search-engine discovery for the public AcademiaPro website.
    # Update SEO_SITE_URL in Render when the project moves to a custom domain.
    seo_site_url = (app.config.get("SEO_SITE_URL") or "https://academiapro-9f39.onrender.com").rstrip("/")

    seo_pages = {
        "main.index": ("AcademiaPro Kenya | Academic & Technical Consultancy",
            "AcademiaPro provides academic and technical support in Kenya, including research guidance, dissertation support, proofreading, editing, data analysis and programming assistance."),
        "main.about": ("About AcademiaPro | Academic & Technical Support in Kenya",
            "Learn about AcademiaPro, our student-focused approach, direct admin support, confidentiality and commitment to clear academic and technical guidance."),
        "main.services_page": ("Academic & Technical Services | AcademiaPro Kenya",
            "Explore AcademiaPro services in Kenya, including academic writing guidance, research and dissertation support, editing, proofreading, programming and data analysis."),
        "main.pricing_page": ("Pricing | AcademiaPro Kenya",
            "Understand AcademiaPro pricing and request a clear quotation for academic support, research guidance, editing, data analysis and technical services."),
        "main.testimonials": ("Client Testimonials | AcademiaPro Kenya",
            "Read feedback and experiences shared by people who have used AcademiaPro's academic and technical support services."),
        "main.privacy_policy": ("Privacy Policy | AcademiaPro",
            "Read how AcademiaPro handles account details, project information, communication and personal data."),
        "main.faq": ("Frequently Asked Questions | AcademiaPro Kenya",
            "Find answers about AcademiaPro services, the order process, communication, project requirements, payments and support."),
        "main.how_it_works": ("How It Works | AcademiaPro Kenya",
            "See how to share your project brief, confirm requirements with the AcademiaPro admin team and follow your request through completion."),
        "main.terms": ("Terms & Conditions | AcademiaPro",
            "Review the terms and conditions governing the use of AcademiaPro services and website."),
        "main.fair_use": ("Fair Use Policy | AcademiaPro",
            "Learn about responsible and appropriate use of AcademiaPro services and website resources."),
        "main.payment_policy": ("Payment Policy | AcademiaPro",
            "Review AcademiaPro payment information, quotation steps and payment-related terms."),
        "main.blog_list": ("Academic Resources & Articles | AcademiaPro Kenya",
            "Explore practical articles and student resources from AcademiaPro on research, academic writing, study skills, citation, exams and technical topics."),
        "main.Samples": ("Academic Samples Library | AcademiaPro Kenya",
            "Browse sample resources by subject, academic level and style to understand formats and project requirements."),
        "main.essay_writing": ("Essay Writing Guidance | AcademiaPro Kenya",
            "Get structured guidance on essay planning, argument development, research, referencing, editing and proofreading."),
        "main.research_papers": ("Research Paper Support | AcademiaPro Kenya",
            "Explore support for research questions, literature searches, paper structure, methodology, citations and final editing."),
        "main.case_studies": ("Case Study Support | AcademiaPro Kenya",
            "Get help understanding case study requirements, analysing evidence, structuring findings and presenting recommendations."),
        "main.dissertations": ("Dissertation Support | AcademiaPro Kenya",
            "Explore dissertation guidance covering research questions, literature reviews, methodology, analysis, structure and editing."),
        "main.theses": ("Thesis Support | AcademiaPro Kenya",
            "Find guidance for thesis planning, research structure, academic conventions, referencing and proofreading."),
        "main.speeches": ("Speech Writing Guidance | AcademiaPro Kenya",
            "Get support with speech structure, audience-focused messaging, research, clarity and presentation preparation."),
        "main.assignments": ("Assignment Support | AcademiaPro Kenya",
            "Understand assignment requirements and get guidance on research, planning, structure, citations and proofreading."),
        "main.narrative_essays": ("Narrative Essay Guidance | AcademiaPro Kenya",
            "Explore narrative essay structure, storytelling techniques, coherent paragraphs and effective editing."),
        "main.analytical_essays": ("Analytical Essay Guidance | AcademiaPro Kenya",
            "Develop analytical essays with clear claims, critical reasoning, evidence, structure and accurate citations."),
        "main.persuasive_essays": ("Persuasive Essay Guidance | AcademiaPro Kenya",
            "Build persuasive essays with focused arguments, credible evidence, counterarguments and clear academic structure."),
        "main.admission_help": ("Admissions Application Support | AcademiaPro Kenya",
            "Get guidance on organising application materials, personal statements, essays and supporting documents."),
        "main.literature_reviews": ("Literature Review Support | AcademiaPro Kenya",
            "Explore literature review planning, source evaluation, synthesis, research gaps, academic structure and referencing."),
        "main.book_reports": ("Book Report Guidance | AcademiaPro Kenya",
            "Get guidance on book report structure, summarising key ideas, developing analysis and presenting evidence clearly."),
        "main.academic_writing": ("Academic Writing Support | AcademiaPro Kenya",
            "Explore academic writing guidance for essays, reports and coursework, with attention to structure, clarity, citations and originality."),
        "main.research_dissertation": ("Research & Dissertation Guidance | AcademiaPro Kenya",
            "Get structured research and dissertation guidance, from refining a topic and proposal to methodology, analysis and final editing."),
        "main.programming": ("Programming & Coding Support | AcademiaPro Kenya",
            "Explore programming support for code structure, debugging, project planning, explanations and technical documentation."),
        "main.statistics": ("Statistics & Data Analysis Support | AcademiaPro Kenya",
            "Get guidance on statistical methods, data cleaning, analysis, interpretation, charts and reporting using common data tools."),
        "main.business_finance": ("Business & Finance Support | AcademiaPro Kenya",
            "Explore business and finance guidance, including financial analysis, business case studies, models and clear reporting."),
        "main.research_proposals": ("Research Proposal Guidance | AcademiaPro Kenya",
            "Develop a focused research proposal with guidance on the topic, problem statement, objectives, literature and methodology."),
        "main.career_services": ("Career Services Support | AcademiaPro Kenya",
            "Get guidance on career documents, professional presentation and planning your next career step."),
        "main.linkedin_optimization": ("LinkedIn Profile Guidance | AcademiaPro Kenya",
            "Improve your LinkedIn profile with clearer positioning, stronger experience descriptions and a professional presentation."),
        "main.exam_preparation": ("Exam Preparation Resources | AcademiaPro Kenya",
            "Explore study planning, revision strategies, practice approaches and practical exam preparation guidance."),
        "main.database_architecture": ("Database Architecture Support | AcademiaPro Kenya",
            "Explore database design guidance, data modelling, relational structures, queries and technical documentation."),
        "main.ai_machine_learning": ("AI & Machine Learning Support | AcademiaPro Kenya",
            "Get guidance on AI and machine learning concepts, model workflows, data preparation, evaluation and technical projects."),
        "main.editing_proofreading": ("Editing & Proofreading | AcademiaPro Kenya",
            "Improve clarity, grammar, formatting, flow and referencing with editing and proofreading support from AcademiaPro."),
        "main.blog_detail": ("Academic Article | AcademiaPro Kenya",
            "Practical academic guidance and student resources from AcademiaPro Kenya."),
    }

    @app.context_processor
    def inject_seo_metadata():
        endpoint = request.endpoint or ""
        page_title, page_description = seo_pages.get(
            endpoint,
            ("AcademiaPro Kenya | Academic & Technical Consultancy",
             "AcademiaPro provides academic and technical support, research guidance, editing, proofreading, data analysis and programming assistance.")
        )
        canonical_path = request.path.rstrip("/") or "/"
        canonical_url = f"{seo_site_url}{canonical_path}"
        return {
            "seo_default_title": page_title,
            "seo_default_description": page_description,
            "seo_robots": "index, follow" if endpoint in seo_pages else "noindex, nofollow",
            "seo_canonical_url": canonical_url,
            "seo_organization_schema": {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "AcademiaPro",
                "url": seo_site_url,
                "description": "Academic and technical support, research guidance, editing, proofreading, data analysis and programming assistance in Kenya.",
                "areaServed": {"@type": "Country", "name": "Kenya"}
            }
        }

    @app.get("/robots.txt")
    def robots_txt():
        rules = [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin",
            "Disallow: /staff-portal",
            "Disallow: /dashboard",
            "Disallow: /my-orders",
            "Disallow: /orders/",
            "Disallow: /profile",
            "Disallow: /settings",
            "Disallow: /notifications",
            "Disallow: /support-tickets",
            "Disallow: /support/",
            "Disallow: /guest/",
            "Disallow: /ai/",
            "Disallow: /api/",
            "Disallow: /chat/",
            "Disallow: /admin_chat",
            "Disallow: /health",
            f"Sitemap: {seo_site_url}/sitemap.xml"
        ]
        return Response("\n".join(rules) + "\n", mimetype="text/plain")

    @app.get("/sitemap.xml")
    def sitemap_xml():
        from xml.etree.ElementTree import Element, SubElement, tostring

        namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        urlset = Element("urlset", {"xmlns": namespace})
        sitemap_endpoints = [endpoint for endpoint in seo_pages if endpoint in app.view_functions]
        for endpoint in sitemap_endpoints:
            entry = SubElement(urlset, "url")
            SubElement(entry, "loc").text = f"{seo_site_url}{url_for(endpoint)}"

        published_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
        for post in published_posts:
            entry = SubElement(urlset, "url")
            SubElement(entry, "loc").text = f"{seo_site_url}{url_for('main.blog_detail', id=post.id)}"
            last_modified = getattr(post, "updated_at", None) or getattr(post, "created_at", None)
            if last_modified:
                SubElement(entry, "lastmod").text = last_modified.date().isoformat() if hasattr(last_modified, "date") else str(last_modified)

        xml_bytes = tostring(urlset, encoding="utf-8", xml_declaration=True)
        return Response(xml_bytes, mimetype="application/xml")

    return app  # ✅ this must be inside the create_app() function
