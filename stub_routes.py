#!/usr/bin/env python3
"""Stub out all writer-related routes"""

import re

# Read the file
with open('app/routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Define routes to stub
ROUTES_TO_STUB = {
    'writer_recruitment': 'writer_recruitment',
    'writer_apply': 'writer_apply',
    'public_writers': 'public_writers',
    'writer_samples': 'writer_samples',
    'admin_writers': 'admin_writers',
    'approve_writer': 'approve_writer',
    'suspend_writer': 'suspend_writer',
    'delete_writer': 'delete_writer',
    'writer_thank_you': 'writer_thank_you',
    'add_writer': 'add_writer',
    'writer_blog_manage': 'writer_blog_manage',
    'writer_edit_blog': 'writer_edit_blog',
    'writer_delete_blog': 'writer_delete_blog',
}

def find_function_bounds(lines, func_name):
    """Find start and end line of a function"""
    start_idx = None
    route_start = None
    
    # Find the function definition
    for i, line in enumerate(lines):
        if f'def {func_name}(' in line:
            start_idx = i
            # Look backwards for @main.route decorator
            for j in range(i-1, -1, -1):
                if '@main.route' in lines[j]:
                    route_start = j
                    break
            break
    
    if start_idx is None:
        return None, None
    
    # Find the next function definition at the same indentation level
    indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
    end_idx = len(lines)
    
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        curr_indent = len(line) - len(line.lstrip())
        if curr_indent <= indent and (line.strip().startswith('@') or line.strip().startswith('def ')):
            end_idx = i
            break
    
    return route_start, end_idx

# Stub out the routes
output_lines = []
skip_until = -1

for i, line in enumerate(lines):
    if i < skip_until:
        continue
    
    # Check if this line starts one of our writer routes
    found_route = False
    for route_name in ROUTES_TO_STUB.keys():
        func_match = re.search(f'def {route_name}\\(', line)
        if func_match:
            # Find the route start
            route_start, route_end = find_function_bounds(lines, route_name)
            if route_start is not None:
                # Add the decorator
                output_lines.append(lines[route_start])
                # Add stub function
                indent = '    '
                func_def = lines[i]  # Keep original function definition
                output_lines.append(func_def)
                
                # Extract login_required if present
                login_req = ''
                for j in range(route_start, i):
                    if '@login_required' in lines[j]:
                        login_req = 'login_required='
                        break
                
                # Add flash and redirect
                output_lines.append(f'{indent}flash("Writer features have been disabled in this version.", "info")\n')
                output_lines.append(f'{indent}return redirect(url_for("main.dashboard"))\n')
                output_lines.append('\n')
                
                skip_until = route_end
                found_route = True
                break
    
    if not found_route:
        output_lines.append(line)

# Write back
with open('app/routes.py', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("Writer routes stubbed out successfully!")
