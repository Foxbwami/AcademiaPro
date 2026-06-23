#!/usr/bin/env python3
"""Comprehensive cleanup of routes.py to remove writer model references and fix syntax errors"""

import re

# Read the file
with open('app/routes.py', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
    lines = content.split('\n')

# Phase 1: Remove incomplete assignment statements
cleaned_lines = []
skip_next = False
for i, line in enumerate(lines):
    # Skip lines that are incomplete assignments (end with = but no value)
    if re.match(r'^\s*\w+\s*=\s*$', line):
        # This is an incomplete assignment - skip it and the next line if it's a continuation
        skip_next = True
        continue
    elif skip_next and (line.strip().startswith('(') or line.strip().startswith('.')):
        # Skip continuation of incomplete query
        if line.strip() == ').all()':
            skip_next = False
        continue
    else:
        skip_next = False
    
    # Skip lines trying to use removed models
    if any(x in line for x in ['Writer.', 'JobApplication.', 'OrderReview.', 'Application.query', 'Application.filter', 'Writer.query', 'JobApplication.query']):
        continue
    
    # Skip writer-related variable assignments
    if any(x in line for x in ['writer_profile =', 'approved_app =', 'existing_writer =', 'linked_writer =']):
        continue
    
    # Skip references to removed models in strings when they don't make sense
    if 'existing_writer' in line and 'existing_' not in line.split('=')[0]:
        continue
    
    cleaned_lines.append(line)

# Phase 2: Fix unclosed parentheses/braces by removing orphaned ones
content = '\n'.join(cleaned_lines)

# Remove orphaned close parens/brackets from incomplete statements
content = re.sub(r'^\s*\)\s*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^\s*\]\s*$', '', content, flags=re.MULTILINE)  
content = re.sub(r'^\s*\}\s*$', '', content, flags=re.MULTILINE)

# Remove multiple consecutive blank lines
content = re.sub(r'\n\n\n+', '\n\n', content)

# Phase 3: Remove incomplete function bodies that reference removed models
# Remove sections that start with function defs for admin functions that worked with writers
removed_functions = [
    r'def approve_job_application.*?(?=^def |\Z)',
    r'def reject_job_application.*?(?=^def |\Z)',
    r'def clarify_job_application.*?(?=^def |\Z)',
]

# Actually, since we already stubbed those, let's just remove problematic queries

# Remove Writer queries
content = re.sub(r'.*Writer\.query\..*\n', '', content)
content = re.sub(r'.*\.outerjoin\(Writer.*\n', '', content)
content = re.sub(r'.*Writer\.name\..*\n', '', content)

# Remove JobApplication queries  
content = re.sub(r'.*JobApplication\.query\..*\n', '', content)
content = re.sub(r'.*JobApplication\..*(filter|order).*\n', '', content)

# Remove Application queries
content = re.sub(r'.*Application\.query\..*\n', '', content)
content = re.sub(r'.*Application\..*(filter|approved).*\n', '', content)

# Remove OrderReview queries
content = re.sub(r'.*OrderReview\..*\n', '', content)

# Clean up empty filter clauses
content = re.sub(r'\.filter\(\s*\)', '.filter()', content)

# Fix dangling Writer imports that might be in try blocks
content = re.sub(r'.*Writer[, )].*\n', '', content)

# Write back
with open('app/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comprehensive cleanup completed!")
