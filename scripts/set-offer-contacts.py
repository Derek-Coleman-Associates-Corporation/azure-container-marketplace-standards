#!/usr/bin/env python3
"""
Gate 10: Set offer listing contacts via Partner Center API.
All new offers automatically get agent@dcassociatesgroup.com as contact.
"""
import argparse, json, os, subprocess, sys, time
import requests

def get_graph_token():
    PC_TENANT = 'a42a9fb4-e76a-4b34-b070-3bf3687022f0'
    r = subprocess.run([
        'az','account','get-access-token',
        '--resource','https://graph.microsoft.com',
        '--tenant', PC_TENANT,
        '--output','json'
    ], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'az token failed: {r.stderr}')
    return json.loads(r.stdout).get('accessToken')

def poll(base, apiv, headers, job_id, retries=20):
    for _ in range(retries):
        time.sleep(5)
        r = requests.get(f"{base}/configure/{job_id}/status{apiv}", headers=headers, timeout=10)
        s = r.json().get('jobStatus','').lower()
        if s in ('completed','succeeded'): return True
        if s == 'failed': return False, r.json().get('errors')
    return None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--support-email', default='agent@dcassociatesgroup.com')
    p.add_argument('--support-name',  default='DC Associates Agent')
    p.add_argument('--phone',         default='18564484318')
    p.add_argument('--support-url',   default='https://www.dcassociatesgroup.com')
    p.add_argument('--privacy-url',   default='https://www.dcassociatesgroup.com/privacy')
    p.add_argument('--product-id',    default=os.environ.get('PRODUCT_ID',''))
    args = p.parse_args()

    token = get_graph_token()
    base  = "https://graph.microsoft.com/rp/product-ingestion"
    apiv  = "?api-version=2022-03-01-preview2"
    h     = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    # Find all container offers if no product-id given
    products = []
    if args.product_id:
        products = [args.product_id]
    else:
        r = requests.get(f"{base}/product{apiv}", headers=h, timeout=15)
        products = [
            p['id'].split('/')[-1]
            for p in r.json().get('value',[])
            if p.get('type') == 'azureContainer'
        ]

    contact = {
        "name":  args.support_name,
        "email": args.support_email,
        "phone": args.phone
    }

    for pid in products:
        listing_id = f"listing/{pid}/public/main/default/en-us"
        # GET current listing
        lr = requests.get(f"{base}/{listing_id}{apiv}", headers=h, timeout=10)
        if lr.status_code != 200:
            print(f"⚠️  Could not get listing for {pid}: {lr.status_code}")
            continue

        listing = lr.json()
        listing['supportContact']             = contact
        listing['engineeringContact']         = contact
        listing['cloudSolutionProviderContact'] = contact
        listing['globalSupportWebsite']       = args.support_url
        listing['privacyPolicyLink']          = args.privacy_url

        conf = {
            "$schema": "https://schema.mp.microsoft.com/schema/configure/2022-03-01-preview2",
            "resources": [listing]
        }
        cr = requests.post(f"{base}/configure{apiv}", headers=h, json=conf, timeout=30)
        if cr.status_code in (200, 202):
            ok = poll(base, apiv, h, cr.json().get('jobId'))
            status = '✅' if ok else '❌'
            print(f"{status} [{pid}] contacts set to {args.support_email}")
        else:
            print(f"❌ [{pid}] {cr.status_code}: {cr.json().get('error',{}).get('message','')[:100]}")
            sys.exit(1)

if __name__ == '__main__':
    main()
