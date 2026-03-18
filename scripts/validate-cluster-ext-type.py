#!/usr/bin/env python3
"""Validate clusterExtensionType format: PublisherName.AppName, ≤ 50 chars."""
import sys, yaml, re

with open(sys.argv[1]) as f:
    m = yaml.safe_load(f)

ext_type = m.get("clusterExtensionType","")
if not ext_type:
    # May be in extensionRegistrationParameters
    ext_type = m.get("extensionRegistrationParameters",{}).get("clusterExtensionType","")

errors = []
pattern = r'^[A-Za-z][A-Za-z0-9]+\.[A-Za-z][A-Za-z0-9]+$'
if not re.match(pattern, ext_type):
    errors.append(f"clusterExtensionType '{ext_type}' must match PublisherName.ApplicationName format")
if len(ext_type) > 50:
    errors.append(f"clusterExtensionType '{ext_type}' exceeds 50 characters ({len(ext_type)})")

if errors:
    for e in errors: print(f"❌ {e}")
    sys.exit(1)
print(f"✅ clusterExtensionType '{ext_type}' is valid")
