#!/usr/bin/env python3
"""Gate 10: Check offer listing completeness via Partner Center API."""
import json, subprocess, sys
import requests

def get_token():
    r = subprocess.run(
        ['az','account','get-access-token','--resource','https://graph.microsoft.com','--output','json'],
        capture_output=True, text=True)
    return json.loads(r.stdout).get('accessToken')

base  = "https://graph.microsoft.com/rp/product-ingestion"
apiv  = "?api-version=2022-03-01-preview2"
h     = {'Authorization': f'Bearer {get_token()}', 'Content-Type': 'application/json'}

products = requests.get(f"{base}/product{apiv}", headers=h, timeout=15).json().get('value',[])
errors_total = 0

for p in products:
    if p.get('type') != 'azureContainer': continue
    pid   = p['id'].split('/')[-1]
    alias = p.get('alias','?')

    lr = requests.get(f"{base}/listing/{pid}/public/main/default/en-us{apiv}", headers=h, timeout=10)
    if lr.status_code != 200: continue
    listing = lr.json()

    errs = []
    if not listing.get('supportContact',{}).get('email'):
        errs.append('supportContact.email missing')
    elif listing['supportContact']['email'] != 'agent@dcassociatesgroup.com':
        errs.append(f"supportContact.email is {listing['supportContact']['email']}, expected agent@dcassociatesgroup.com")
    if not listing.get('privacyPolicyLink'):
        errs.append('privacyPolicyLink missing')
    if not listing.get('globalSupportWebsite'):
        errs.append('globalSupportWebsite missing')
    if not listing.get('title'):
        errs.append('title missing')
    if not listing.get('description'):
        errs.append('description missing')

    if errs:
        print(f"❌ {alias} ({pid}):")
        for e in errs: print(f"   - {e}")
        errors_total += len(errs)
    else:
        print(f"✅ {alias}: listing complete, contact=agent@dcassociatesgroup.com")

if errors_total:
    sys.exit(1)
