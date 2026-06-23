#!/usr/bin/env python3
"""Remove all writer-related code from routes.py"""

import re

# Read the file
with open('app/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Define function names to remove
WRITER_FUNCTIONS = [
    'writer_apply',
    'public_writers', 
    'writer_samples',
    'admin_writers',
    'approve_writer',
    'suspend_writer',
    'delete_writer',
    'writer_thank_you',
    'add_writer',
    'writer_blog_manage',
    'writer_edit_blog',
    'writer_delete_blog'
]

def find_function_end(lines, start_idx):
    """Find the end of a function definition"""
    if start_idx >= len(lines):
        return start_idx
    
    # Start from current line
    indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    
    # Find the next function or class at same or lower indent level
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        
        curr_indent = len(line) - len(line.lstrip())
        
        # If we find a line with @ (decorator) or def at same/lower indent, that's the end
        if curr_indent <= indent_level and (line.strip().startswith('@') or line.strip().startswith('def ')):
            return i
    
    return len(lines)

# Find and mark all writer function lines for deletion
delete_ranges = []

for i, line in enumerate(lines):
    for func_name in WRITER_FUNCTIONS:
        if f'def {func_name}(' in line:
            end_idx = find_function_end(lines, i)
            # Also include any decorators before the function
            start_idx = i
            for j in range(i-1, -1, -1):
                if lines[j].strip().startswith('@main.route'):
                    start_idx = j
                elif lines[j].strip() == '':
                    continue
                else:
                    break
            delete_ranges.append((start_idx, end_idx))
            break

# Remove duplicates and sort by start position (descending)
delete_ranges = sorted(list(set(delete_ranges)), reverse=True)

# Delete function bodies from end to start (to preserve indices)
for start, end in delete_ranges:
    del lines[start:end]

# Join back
content = '\n'.join(lines)

# Remove Writer/JobApplication/Application from imports if they exist
content = re.sub(
    r'from app\.models import \((.*?)\)',
    lambda m: 'from app.models import (' + ', '.join(
        x.strip() for x in m.group(1).split(',') 
        if x.strip() not in ['Writer', 'JobApplication', 'Application']
    ) + ')',
    content,
    flags=re.DOTALL
)

# Remove any remaining writer-related imports on single lines  
content = re.sub(r'from app\.models import.*(?:Writer|JobApplication|Application).*\n', '', content)

# Remove Writer. queries
content = re.sub(r'\s*Writer\.query.*\n', '\n', content)

# Remove JobApplication references
content = re.sub(r'\s*JobApplication\.query.*\n', '\n', content)

# Remove writer_profile queries
content = re.sub(r'\s*writer_profile\s*=\s*Writer\.query.*\n', '\n', content)

# Remove duplicate blank lines
content = re.sub(r'\n\n\n+', '\n\n', content)

# Write back
with open('app/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Writer cleanup completed!")
print(f"Removed {len(delete_ranges)} writer-related functions/routes")
