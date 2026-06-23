#!/usr/bin/env python3
"""Script to remove writer-related code from routes.py"""

import re

# Read the routes file
with open('app/routes.py', 'r') as f:
    lines = f.readlines()

# Find line numbers with writer-related content
writer_lines = []
for i, line in enumerate(lines, 1):
    if any(keyword in line for keyword in [
        '_is_approved_writer',
        'OrderReview',
        'Writer.',
        'Application',
        'JobApplication',
        'writer_profile',
        'writer_resume',
        'writer_portfolio',
        'job_posted',
        'writer_id',
    ]):
        writer_lines.append((i, line.strip()))

print("Writer-related lines still in routes.py:")
for line_num, content in writer_lines[:30]:  # Show first 30
    print(f"  Line {line_num}: {content[:80]}")

print(f"\nTotal writer-related lines: {len(writer_lines)}")
print(f"Total file lines: {len(lines)}")
