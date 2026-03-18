# azure-container-marketplace-standards

CI/CD compliance pipeline for Azure Marketplace Kubernetes container offers.
Every Microsoft requirement is a **named gate** — all 10 must be green before Partner Center submission.

## 10 Gates

| Gate | What it checks | Depends on |
|---|---|---|
| **01** — ACR Access | Marketplace SP AcrPull + PartnerCenterIngestion registered | — |
| **02** — Artifact Structure | `manifest.yaml`, `createUIDefinition.json`, `mainTemplate.json`, `helm/` | — |
| **03** — Helm Lint | `helm lint` + `global.azure.images.*` pattern | Gate 02 |
| **04** — createUIDefinition | Valid JSON + `outputs` section | Gate 02 |
| **05** — ARM Resource Types | Only `managedClusters` + `extensions` allowed | Gate 02 |
| **06** — `cpa verify` | Microsoft's official validator | Gates 02–05 |
| **07** — `cpa buildbundle` | Builds + pushes valid CNAB to ACR | Gate 06 |
| **08** — Extension Type | `PublisherName.AppName` format, ≤ 50 chars | — |
| **09** — PC API Schema | Partner Center `cnabReferences` POST = 202 | Gates 07+08 |
| **10** — Offer Listing | Screenshots, contacts (`agent@dcassociatesgroup.com`), cert policy 100 | — |

## Required Secrets

```
AZURE_CREDENTIALS      - Service principal JSON for az login
ACR_TOKEN              - ACR repo-scoped token for cpa buildbundle
PC_CLIENT_ID           - Partner Center app registration client ID
PC_CLIENT_SECRET       - Partner Center app registration secret
PC_TENANT_ID           - a42a9fb4-e76a-4b34-b070-3bf3687022f0
```

## Required Variables

```
ACR_NAME               - dcaicontaineroffers
ACR_SUBSCRIPTION_ID    - f4085274-4e9d-4e93-8360-67a4be900d81
```

## Quick Start

```bash
# 1. Grant ACR access to Marketplace SP
./scripts/grant-acr-access.sh dcaicontaineroffers f4085274-4e9d-4e93-8360-67a4be900d81

# 2. Open a PR with your offer under examples/<offer-name>/
# 3. All 10 gates run automatically
# 4. When all-gates-pass is green → submit to Partner Center
```

## Toolchain

- **`cpa`** (`mcr.microsoft.com/container-package-app:latest`) — Microsoft's official CNAB build + validate tool
- **`addnab/docker-run-action@v3`** — runs `cpa` in GitHub Actions
- **Partner Center Product Ingestion API** — validates + configures offer listing

## Example: ubuntu-starter

See [`examples/ubuntu-starter/`](examples/ubuntu-starter) for the reference implementation.
