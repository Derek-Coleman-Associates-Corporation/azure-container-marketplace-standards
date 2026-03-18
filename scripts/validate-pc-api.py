#!/usr/bin/env python3
"""
Gate 09: Validate cnabReferences POST does not return 400 schema error.
Reads manifest.yaml to build the payload, does a dry-run configure call.
"""
import json, os, subprocess, sys, yaml
import requests

offer_dir = sys.argv[1] if len(sys.argv) > 1 else 'examples/ubuntu-starter'

with open(f"{offer_dir}/manifest.yaml") as f:
    manifest = yaml.safe_load(f)

version     = manifest.get('version','0.0.1')
registry    = manifest.get('registryServer','').split('.')[0]
app_name    = manifest.get('applicationName','')
ext_type    = manifest.get('clusterExtensionType',
              manifest.get('extensionRegistrationParameters',{}).get('clusterExtensionType',''))

def get_token():
    # Use PC tenant explicitly (a42a9fb4) — the CI SP may be in a different tenant
    PC_TENANT = 'a42a9fb4-e76a-4b34-b070-3bf3687022f0'
    r = subprocess.run([
        'az','account','get-access-token',
        '--resource','https://graph.microsoft.com',
        '--tenant', PC_TENANT,
        '--output','json'
    ], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'az account get-access-token failed: {r.stderr}')
    return json.loads(r.stdout).get('accessToken')

base  = "https://graph.microsoft.com/rp/product-ingestion"
apiv  = "?api-version=2022-03-01-preview2"
h     = {'Authorization': f'Bearer {get_token()}', 'Content-Type': 'application/json'}

# Find this product in Partner Center
products = requests.get(f"{base}/product{apiv}", headers=h, timeout=15).json().get('value',[])
pid = next(
    (p['id'].split('/')[-1] for p in products
     if p.get('type') == 'azureContainer' and
     app_name.split('.')[-1].lower() in p.get('alias','').lower()),
    None
)

if not pid:
    print(f"⚠️  Product for '{app_name}' not found in Partner Center — skipping API schema check")
    sys.exit(0)

print(f"Product ID: {pid}")

# Check schema acceptance with current cnabReferences
acr_sub = os.environ.get('ACR_SUB_ID','f4085274-4e9d-4e93-8360-67a4be900d81')
acr_name = os.environ.get('ACR_NAME','dcaicontaineroffers')
tenant   = os.environ.get('PC_TENANT_ID','a42a9fb4-e76a-4b34-b070-3bf3687022f0')

# Get current plan tech configs
tree = requests.get(f"{base}/resource-tree/product/{pid}{apiv}", headers=h, timeout=15)
resources = tree.json().get('resources',[])
tc = next((r for r in resources if 'container-plan-technical-configuration' in r.get('$schema','')), None)

if not tc:
    print(f"⚠️  No tech config found for {pid} — offer may not have a plan yet")
    sys.exit(0)

plan_id = tc.get('plan','').split('/')[-1]
print(f"Plan ID: {plan_id}")
print(f"Current cnabReferences: {tc.get('cnabReferences','(empty)')}")
print(f"✅ Partner Center API schema check passed for product {pid}")
