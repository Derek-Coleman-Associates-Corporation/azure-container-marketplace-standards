#!/usr/bin/env python3
"""Gate 04: Validate createUIDefinition.json."""
import json, sys, os

offer_dir = sys.argv[1] if len(sys.argv) > 1 else 'examples/ubuntu-starter'
filepath  = os.path.join(offer_dir, 'createUIDefinition.json')

with open(filepath) as f:
    d = json.load(f)

errors = []
schema = d.get('$schema', '')
if 'azure.com' not in schema.lower():
    errors.append(f"Invalid $schema: '{schema}' — must reference azure.com")

# outputs can be at root or inside parameters (both are valid)
outputs = d.get('outputs') or d.get('parameters', {}).get('outputs')
if not outputs:
    errors.append("Missing 'outputs' section (checked root and parameters.outputs)")

if errors:
    for e in errors:
        print(f"❌ {e}")
    sys.exit(1)

print(f"✅ createUIDefinition.json valid")
print(f"   outputs keys: {list(outputs.keys())}")
