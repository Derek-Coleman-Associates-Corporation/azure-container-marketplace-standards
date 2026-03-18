#!/usr/bin/env python3
"""Ensure all Helm templates use global.azure.images.* for image references."""
import sys, os, re, glob

offer_dir = sys.argv[1]
templates_dir = os.path.join(offer_dir, "helm", "templates")
values_file = os.path.join(offer_dir, "helm", "values.yaml")

errors = []

# Check values.yaml has global.azure.images
with open(values_file) as f:
    values_content = f.read()
if "global:" not in values_content or "azure:" not in values_content or "images:" not in values_content:
    errors.append("values.yaml must define global.azure.images.* for all image references")

# Check templates don't hardcode image repos
for tmpl in glob.glob(f"{templates_dir}/**/*.yaml", recursive=True):
    with open(tmpl) as f:
        content = f.read()
    hardcoded = re.findall(r'image:\s*["\']?((?!.*global\.azure\.images)[\w./:-]{5,})["\']?', content)
    for h in hardcoded:
        if not h.startswith("{{") and "/" in h:
            errors.append(f"{tmpl}: hardcoded image ref '{h}' — use global.azure.images.*")

if errors:
    for e in errors: print(f"❌ {e}")
    sys.exit(1)
print("✅ All image references use global.azure.images pattern")
