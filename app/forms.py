from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed
from app.constants import (
    SERVICE_TRACK_CHOICES,
    TASK_TYPE_CHOICES,
    LEVEL_CHOICES,
    CITATION_STYLE_CHOICES,
    CURRENCY_CHOICES,
    TIMEZONE_CHOICES,
    BILLING_METHOD_CHOICES,
    PAYOUT_METHOD_CHOICES,
    LANGUAGE_CHOICES,
    CHANNEL_CHOICES,
    LAYOUT_MODE_CHOICES,
    ALLOWED_UPLOAD_EXTENSIONS,
)

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    accept_terms = BooleanField('I agree to the Terms', validators=[InputRequired()])
    accept_privacy = BooleanField('I agree to the Privacy Policy', validators=[InputRequired()])
    submit = SubmitField('Register')

from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class OrderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    service_track = SelectField(
        "Service Track",
        choices=SERVICE_TRACK_CHOICES,
        validators=[DataRequired()],
    )
    task_type = SelectField(
        "Task Type",
        choices=TASK_TYPE_CHOICES,
        validators=[Optional()],
    )
    word_count = IntegerField("Word Count", validators=[Optional()])
    level = SelectField(
        "Academic Level",
        choices=LEVEL_CHOICES,
        validators=[Optional()],
    )
    citation_style = SelectField(
        "Referencing Style",
        choices=CITATION_STYLE_CHOICES,
        validators=[Optional()],
    )
    sources_count = IntegerField("Minimum Sources", validators=[Optional()])
    currency = SelectField(
        "Currency",
        choices=CURRENCY_CHOICES,
        validators=[Optional()],
    )
    timezone = SelectField(
        "Deadline Timezone",
        choices=TIMEZONE_CHOICES,
        validators=[Optional()],
    )
    attachments = FileField("Upload Files", validators=[FileAllowed(list(ALLOWED_UPLOAD_EXTENSIONS), 'Unsupported file type')])
    details = TextAreaField('Details', validators=[DataRequired()])
    deadline = DateField('Deadline', validators=[DataRequired()])
    accept_terms = BooleanField('I agree to the Terms', validators=[InputRequired()])
    accept_privacy = BooleanField('I agree to the Privacy Policy', validators=[InputRequired()])

class ProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[Optional()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("New Password", validators=[Optional()])
    confirm_password = PasswordField("Confirm Password", validators=[Optional(), EqualTo('password')])
    photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Update Profile")

class SettingForm(FlaskForm):
    name = StringField("Full Name", validators=[Optional()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[Optional()])
    academic_level = SelectField(
        "Academic Level",
        choices=[("", "Select level")] + LEVEL_CHOICES,
        validators=[Optional()],
    )
    expertise_tags = StringField("Expertise Tags", validators=[Optional()])
    password = PasswordField("New Password", validators=[Optional()])
    confirm_password = PasswordField("Confirm Password", validators=[Optional(), EqualTo('password')])
    two_factor_enabled = BooleanField("Enable 2FA")
    profile_public = BooleanField("Show profile publicly")
    notify_email = BooleanField("Email notifications")
    notify_sms = BooleanField("SMS notifications")
    notify_in_app = BooleanField("In-app notifications")
    alert_order_updates = BooleanField("Order updates")
    alert_payment_confirmations = BooleanField("Payment confirmations")
    alert_revision_requests = BooleanField("Revision requests")
    alert_admin_announcements = BooleanField("Admin announcements")
    billing_method = SelectField(
        "Billing Method",
        choices=BILLING_METHOD_CHOICES,
        validators=[Optional()],
    )
    payout_method = SelectField(
        "Payout Method",
        choices=PAYOUT_METHOD_CHOICES,
        validators=[Optional()],
    )
    auto_deposit_notifications = BooleanField("Auto-deposit notifications")
    preferred_language = SelectField(
        "Language",
        choices=LANGUAGE_CHOICES,
        validators=[Optional()],
    )
    timezone = SelectField(
        "Time Zone",
        choices=TIMEZONE_CHOICES,
        validators=[Optional()],
    )
    preferred_channel = SelectField(
        "Preferred Communication Channel",
        choices=CHANNEL_CHOICES,
        validators=[Optional()],
    )
    layout_mode = SelectField(
        "Dashboard Layout",
        choices=LAYOUT_MODE_CHOICES,
        validators=[Optional()],
    )
    citation_style = SelectField(
        "Preferred Citation Style",
        choices=CITATION_STYLE_CHOICES,
        validators=[Optional()],
    )
    marketing_opt_in = BooleanField("Receive marketing/newsletter emails")
    photo = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Save changes")
    
