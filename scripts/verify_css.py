from pathlib import Path
import sys
p=Path('app/static/style.css')
if not p.exists():
    print('MISSING: app/static/style.css')
    sys.exit(2)
text=p.read_text(encoding='utf-8')
checks=[]
checks.append(('hero_padding_80_0_60', 'padding:80px 0 60px' in text))
checks.append(('hero_gap_media', '@media(min-width:992px){' in text and '.hero-buttons{ gap:28px' in text))
checks.append(('section_badge_count', text.count('.section-badge')))
for sec in ['.services-section', '.why-section', '.process-section', '.testimonials-section', '.cta-section', '.faq-section']:
    checks.append((f'{sec}_padding_60', f'{sec}{{\n  padding:60px 0' in text or f'{sec}' in text and 'padding:60px 0' in text))
checks.append(('header_shell_padding_left_1.2', 'padding-left: 1.2rem' in text))
checks.append(('primary_var', '--primary:' in text))

ok=True
for k,v in checks:
    print(k, v)
    if k=='section_badge_count' and v!=1:
        ok=False
    elif isinstance(v,bool) and not v:
        ok=False

if ok:
    print('VERIFICATION: PASS')
    sys.exit(0)
else:
    print('VERIFICATION: FAIL')
    sys.exit(3)
