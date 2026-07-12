USER_ROLE_CLIENT = "client"
USER_ROLE_ADMIN = "admin"

SERVICE_TRACK_CHOICES = [
    ("writing", "Academic & Research Writing"),
    ("programming", "Programming & Technical"),
    ("exams", "Exam Preparation"),
    ("career", "Career & Resume"),
]

TASK_TYPE_CHOICES = [
    ("Essay", "Essay"),
    ("Research Paper", "Research Paper"),
    ("Dissertation", "Dissertation"),
    ("Assignment", "Assignment"),
    ("Case Study", "Case Study"),
    ("Admission Essay", "Admission Essay"),
]

LEVEL_CHOICES = [
    ("Undergrad", "Undergrad"),
    ("Masters", "Masters"),
    ("PhD", "PhD"),
]

CITATION_STYLE_CHOICES = [
    ("APA", "APA"),
    ("MLA", "MLA"),
    ("Chicago", "Chicago"),
    ("Harvard", "Harvard"),
]

CURRENCY_CHOICES = [
    ("USD", "USD"),
    ("GBP", "GBP"),
    ("EUR", "EUR"),
]

TIMEZONE_CHOICES = [
    ("UTC", "UTC"),
    ("America/New_York", "GMT-5 (New York)"),
    ("Europe/London", "GMT+0 (London)"),
    ("Africa/Nairobi", "GMT+3 (Nairobi)"),
]

BILLING_METHOD_CHOICES = [
    ("", "Not set"),
    ("Card", "Card"),
    ("PayPal", "PayPal"),
    ("Mobile Money", "Mobile Money"),
    ("Bank", "Bank Transfer"),
]

PAYOUT_METHOD_CHOICES = [
    ("", "Not set"),
    ("PayPal", "PayPal"),
    ("Bank", "Bank Transfer"),
    ("Mobile Money", "Mobile Money"),
]

LANGUAGE_CHOICES = [
    ("English", "English"),
    ("French", "French"),
    ("Spanish", "Spanish"),
]

CHANNEL_CHOICES = [
    ("chat", "Chat"),
    ("email", "Email"),
]

LAYOUT_MODE_CHOICES = [
    ("detailed", "Detailed"),
    ("compact", "Compact"),
]

ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg"}

ORDER_STATUSES = [
    "Pending",
    "Pending Review",
    "Open",
    "In Progress",
    "Draft Submitted",
    "Revision",
    "Completed",
    "Cancelled",
]
