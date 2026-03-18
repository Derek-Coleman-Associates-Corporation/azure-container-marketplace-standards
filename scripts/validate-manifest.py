#!/usr/bin/env python3
"""Validate manifest.yaml against required fields."""
import sys, yaml, re

offer_dir = sys.argv[1]
with open(f"{offer_dir}/manifest.yaml") as f:
    m = yaml.safe_load(f)

errors = []
required = ["applicationName","publisher","version","helmChart","clusterArmTemplate","uiDefinition","registryServer","extensionRegistrationParameters"]
for field in required:
    if field not in m:
        errors.append(f"Missing required field: {field}")

version = str(m.get("version",""))
if not re.match(r"^\d+\.\d+\.\d+$", version):
    errors.append(f"version '{version}' must be in #.#.# format")

app_name = m.get("applicationName","")
if not re.match(r"^[a-z][a-z0-9]*\.[a-z][a-z0-9]*\.[a-z][a-z0-9]*$", app_name.lower()):
    errors.append(f"applicationName '{app_name}' should be in reverse-domain format (e.g., com.publisher.app)")

ext_params = m.get("extensionRegistrationParameters", {})
if "defaultScope" not in ext_params:
    errors.append("extensionRegistrationParameters.defaultScope is required")
if ext_params.get("defaultScope") not in ("cluster", "namespace"):
    errors.append("defaultScope must be 'cluster' or 'namespace'")

if errors:
    for e in errors: print(f"❌ {e}")
    sys.exit(1)
print(f"✅ manifest.yaml valid — {m['applicationName']} v{m['version']}")
