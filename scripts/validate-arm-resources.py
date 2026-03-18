#!/usr/bin/env python3
"""Validate ARM template only uses allowed Marketplace resource types."""
import sys, json

ALLOWED = {
    "Microsoft.ContainerService/managedClusters",
    "Microsoft.KubernetesConfiguration/extensions"
}

with open(sys.argv[1]) as f:
    template = json.load(f)

errors = []
for res in template.get("resources", []):
    rtype = res.get("type","")
    if rtype and rtype not in ALLOWED:
        errors.append(f"Disallowed resource type: '{rtype}'")
        errors.append(f"  Allowed: {sorted(ALLOWED)}")

if errors:
    for e in errors: print(f"❌ {e}")
    sys.exit(1)
print(f"✅ ARM template uses only allowed resource types")
