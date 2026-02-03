#!/usr/bin/env bash
# PUAR-Patients Frontend Deployment Script
# Builds and deploys both PWAs to S3 with CloudFront

set -euo pipefail

# Configuration - AWS Production
API_URL="${API_URL:-https://nmpjiqngaz.us-east-1.awsapprunner.com}"
PATIENT_S3_BUCKET="${PATIENT_S3_BUCKET:-puar-patients-patient-pwa-860599907983}"
DOCTOR_S3_BUCKET="${DOCTOR_S3_BUCKET:-puar-patients-doctor-pwa-860599907983}"
PATIENT_CF_DIST="${PATIENT_CF_DIST:-EJW46XTOYR16L}"
DOCTOR_CF_DIST="${DOCTOR_CF_DIST:-E14KU71BQ3VFB9}"
AWS_REGION="${AWS_REGION:-us-east-1}"

# Colours for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "PUAR-Patients Frontend Deployment"
echo "=============================================="
echo "API URL: ${API_URL}"
echo "Patient S3: ${PATIENT_S3_BUCKET}"
echo "Doctor S3: ${DOCTOR_S3_BUCKET}"
echo "=============================================="

# Build Patient PWA
log_step "Building Patient PWA..."
cd "${PROJECT_ROOT}/frontend/patient"
export VITE_API_URL="${API_URL}"
npm ci --silent
npm run build
log_info "Patient PWA built successfully"

# Build Doctor PWA
log_step "Building Doctor PWA..."
cd "${PROJECT_ROOT}/frontend/doctor"
export VITE_API_URL="${API_URL}"
npm ci --silent
npm run build
log_info "Doctor PWA built successfully"

# Deploy Patient PWA to S3
log_step "Deploying Patient PWA to S3..."
aws s3 sync "${PROJECT_ROOT}/frontend/patient/dist" "s3://${PATIENT_S3_BUCKET}" \
    --delete \
    --region "${AWS_REGION}" \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --exclude "*.json"

aws s3 cp "${PROJECT_ROOT}/frontend/patient/dist/index.html" "s3://${PATIENT_S3_BUCKET}/index.html" \
    --region "${AWS_REGION}" \
    --cache-control "no-cache, no-store, must-revalidate"

# Copy manifest and other JSON files with no-cache
for f in "${PROJECT_ROOT}/frontend/patient/dist"/*.json; do
    if [ -f "$f" ]; then
        aws s3 cp "$f" "s3://${PATIENT_S3_BUCKET}/$(basename "$f")" \
            --region "${AWS_REGION}" \
            --cache-control "no-cache, no-store, must-revalidate"
    fi
done

log_info "Patient PWA deployed to S3"

# Deploy Doctor PWA to S3
log_step "Deploying Doctor PWA to S3..."
aws s3 sync "${PROJECT_ROOT}/frontend/doctor/dist" "s3://${DOCTOR_S3_BUCKET}" \
    --delete \
    --region "${AWS_REGION}" \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --exclude "*.json"

aws s3 cp "${PROJECT_ROOT}/frontend/doctor/dist/index.html" "s3://${DOCTOR_S3_BUCKET}/index.html" \
    --region "${AWS_REGION}" \
    --cache-control "no-cache, no-store, must-revalidate"

# Copy manifest and other JSON files with no-cache
for f in "${PROJECT_ROOT}/frontend/doctor/dist"/*.json; do
    if [ -f "$f" ]; then
        aws s3 cp "$f" "s3://${DOCTOR_S3_BUCKET}/$(basename "$f")" \
            --region "${AWS_REGION}" \
            --cache-control "no-cache, no-store, must-revalidate"
    fi
done

log_info "Doctor PWA deployed to S3"

# Invalidate CloudFront caches
if [ "${PATIENT_CF_DIST}" != "E3EXAMPLE" ]; then
    log_step "Invalidating Patient CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "${PATIENT_CF_DIST}" \
        --paths "/*" \
        --region "${AWS_REGION}" > /dev/null
    log_info "Patient CloudFront cache invalidated"
fi

if [ "${DOCTOR_CF_DIST}" != "E3EXAMPLE" ]; then
    log_step "Invalidating Doctor CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "${DOCTOR_CF_DIST}" \
        --paths "/*" \
        --region "${AWS_REGION}" > /dev/null
    log_info "Doctor CloudFront cache invalidated"
fi

echo ""
echo "=============================================="
log_info "Frontend deployment complete!"
echo "=============================================="
echo ""
log_warn "Note: CloudFront invalidation may take a few minutes."
echo "Run 'python scripts/test_deployed.py' to verify deployment."
