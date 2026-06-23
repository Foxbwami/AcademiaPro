#!/usr/bin/env python3
"""Remove all remaining references to deleted models"""

import re

with open('app/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove lines that reference removed models
lines_to_remove = [
    r'.*\bWriter\.query\b.*',
    r'.*\bJobApplication\.query\b.*',
    r'.*\bApplication\.query\b.*',
    r'.*\bOrderReview\b.*',
    r'.*\blinked_writer\s*=.*',
    r'.*\bexisting_writer\s*=.*',
    r'.*\bwriter_profile\s*=.*',
    r'.*\bapproved_app\s*=.*',
    r'.*\bapproved_writer\b.*',
    r'.*\bwriter_apps\s*=.*',
    r'.*\bwriter_application\s*=.*',
    r'.*\bapproved_apps\s*=.*',
    r'.*\bwriter_enabled\s*=.*',
]

for pattern in lines_to_remove:
    content = re.sub(pattern + '\n', '\n', content)

# Remove query chains that reference removed models in admin/indexfunctions
content = re.sub(r'\.outerjoin\(Writer,.*?\)', '', content)

# Clean up multiple blank lines
content = re.sub(r'\n\n\n+', '\n\n', content)

with open('app/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Cleaned remaining model references!")
