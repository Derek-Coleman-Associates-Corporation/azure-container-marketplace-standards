#!/usr/bin/env bash
# Idempotent: grant Marketplace SP AcrPull on the target ACR
set -e
ACR_NAME=${1:-$ACR_NAME}
SUB_ID=${2:-$ACR_SUBSCRIPTION_ID}
MARKETPLACE_APP_ID="32597670-3e15-4def-8851-614ff48c1efa"

az account set --subscription "$SUB_ID"
SP_OID=$(az ad sp show --id "$MARKETPLACE_APP_ID" --query id -o tsv 2>/dev/null || \
         az ad sp create --id "$MARKETPLACE_APP_ID" --query id -o tsv)
echo "Marketplace SP: $SP_OID"
ACR_ID=$(az acr show --name "$ACR_NAME" --query id -o tsv)
az role assignment create \
  --assignee-object-id "$SP_OID" \
  --assignee-principal-type ServicePrincipal \
  --scope "$ACR_ID" \
  --role AcrPull 2>/dev/null || echo "AcrPull already assigned"
az provider register --namespace Microsoft.PartnerCenterIngestion \
  --subscription "$SUB_ID" --wait
echo "✅ ACR access granted"
