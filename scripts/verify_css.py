from pathlib import Path
import re
import sys


CSS_ROOT = Path("app/static")
css_files = sorted(CSS_ROOT.rglob("*.css"))

if not css_files:
    print("MISSING: no CSS files found under app/static")
    sys.exit(2)

combined = "\n".join(path.read_text(encoding="utf-8") for path in css_files)
checks = []

required_selectors = [
    ".site-header",
    ".trust-bar",
    ".header-shell",
    ".mobile-drawer",
    ".mega-feature",
    ".hero-section",
    ".services-section",
    ".testimonials-section",
    ".site-footer",
]

for selector in required_selectors:
    checks.append((f"selector {selector}", selector in combined))

for path in css_files:
    text = path.read_text(encoding="utf-8")
    checks.append((f"balanced braces {path.as_posix()}", text.count("{") == text.count("}")))

    for match in re.finditer(r"url\((?![\"']?(?:data:|https?:|#))([\"']?)([^)\"']+)\1\)", text):
        raw = match.group(2).strip()
        target = (path.parent / raw).resolve()
        checks.append((f"asset {path.as_posix()} -> {raw}", target.exists()))

checks.append(("legacy AcademicPro spelling absent", "AcademicPro" not in combined))
checks.append(("missing mega image reference absent", "mega-feature.jpg" not in combined))

ok = True
for name, result in checks:
    print(name, result)
    if not result:
        ok = False

if ok:
    print("VERIFICATION: PASS")
    sys.exit(0)

print("VERIFICATION: FAIL")
sys.exit(3)
