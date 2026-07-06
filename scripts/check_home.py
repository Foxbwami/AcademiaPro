import urllib.request, time, sys

base='http://127.0.0.1:5000'

# wait for server
for i in range(15):
    try:
        r=urllib.request.urlopen(base, timeout=3)
        html=r.read().decode('utf-8')
        break
    except Exception as e:
        time.sleep(1)
else:
    print('ERROR: server not reachable')
    sys.exit(2)

# try to determine CSS path
css_path=None
for line in html.splitlines():
    if 'static/style.css' in line:
        start=line.find('href=')
        if start!=-1:
            href=line[start:]
            # crude extract
            import re
            m=re.search(r"href=[\'\"]([^\'\"]+)", href)
            if m:
                css_path=m.group(1)
                break
if not css_path:
    css_path='/static/style.css'
if css_path.startswith('/'):
    css_url=base+css_path
else:
    css_url=base+'/'+css_path

print('Fetching', css_url)
try:
    c=urllib.request.urlopen(css_url, timeout=5).read().decode('utf-8')
except Exception as e:
    print('ERROR: could not fetch css:', e)
    sys.exit(3)

# checks
checks=[]
if 'hero-section' in html:
    checks.append(('hero_present', True))
else:
    checks.append(('hero_present', False))

# check for our padding value
checks.append(('hero_padding_ok', 'padding:80px 0 60px' in c))

# count section-badge occurrences
count_section_badge=c.count('.section-badge')
checks.append(('section_badge_count', count_section_badge))

# check for primary variable usage
checks.append(('primary_var_used', 'var(--primary)' in c))

# print results
for k,v in checks:
    print(f"{k}: {v}")

# determine final status
if checks[0][1] and checks[1][1] and checks[2][1]==1 and checks[3][1]:
    print('VERIFICATION: PASS')
    sys.exit(0)
else:
    print('VERIFICATION: FAIL')
    sys.exit(4)
