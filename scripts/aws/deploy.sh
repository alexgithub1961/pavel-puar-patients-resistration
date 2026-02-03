#!/usr/bin/env bash
# PUAR-Patients AWS Deployment Script
# Deploys complete stack: RDS PostgreSQL + App Runner (Backend) + S3/CloudFront (Frontend)
#
# Usage: AWS_PROFILE=aptus ./scripts/aws/deploy.sh

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================
APP_NAME="puar-patients"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_PROFILE="${AWS_PROFILE:-aptus}"
ENVIRONMENT="${ENVIRONMENT:-production}"

# Database settings
DB_INSTANCE_CLASS="db.t3.micro"
DB_ALLOCATED_STORAGE="20"
DB_NAME="puar_patients"
DB_USER="puar"
DB_ENGINE_VERSION="16.6"

# App Runner settings
APP_RUNNER_CPU="1024"      # 1 vCPU
APP_RUNNER_MEMORY="2048"   # 2 GB

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ============================================================================
# Prerequisites Check
# ============================================================================
check_prerequisites() {
    log_step "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Set AWS profile
    export AWS_PROFILE="${AWS_PROFILE}"
    export AWS_DEFAULT_REGION="${AWS_REGION}"

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured for profile: ${AWS_PROFILE}"
        exit 1
    fi

    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    log_info "Using AWS Account: ${AWS_ACCOUNT_ID}"
    log_info "Region: ${AWS_REGION}"
    log_info "Profile: ${AWS_PROFILE}"
}

# ============================================================================
# Generate Secure Password
# ============================================================================
generate_password() {
    # Generate 24-char alphanumeric password (RDS compatible)
    openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 24
}

# ============================================================================
# Create or Get Database Password from Secrets Manager
# ============================================================================
setup_database_secret() {
    log_step "Setting up database credentials..."

    SECRET_NAME="${APP_NAME}/db-password"

    if aws secretsmanager describe-secret --secret-id "${SECRET_NAME}" &> /dev/null; then
        log_info "Database secret already exists"
        DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id "${SECRET_NAME}" --query SecretString --output text)
    else
        log_info "Creating database secret..."
        DB_PASSWORD=$(generate_password)
        aws secretsmanager create-secret \
            --name "${SECRET_NAME}" \
            --description "PUAR Patients database password" \
            --secret-string "${DB_PASSWORD}"
        log_info "Database secret created"
    fi
}

# ============================================================================
# Create JWT Secret
# ============================================================================
setup_jwt_secret() {
    log_step "Setting up JWT secret..."

    SECRET_NAME="${APP_NAME}/jwt-secret"

    if aws secretsmanager describe-secret --secret-id "${SECRET_NAME}" &> /dev/null; then
        log_info "JWT secret already exists"
        JWT_SECRET=$(aws secretsmanager get-secret-value --secret-id "${SECRET_NAME}" --query SecretString --output text)
    else
        log_info "Creating JWT secret..."
        JWT_SECRET=$(openssl rand -base64 48)
        aws secretsmanager create-secret \
            --name "${SECRET_NAME}" \
            --description "PUAR Patients JWT signing key" \
            --secret-string "${JWT_SECRET}"
        log_info "JWT secret created"
    fi
}

# ============================================================================
# Create Security Group for RDS
# ============================================================================
create_security_group() {
    log_step "Creating security group for RDS..."

    SG_NAME="${APP_NAME}-rds-sg"

    # Check if security group exists
    SG_ID=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=${SG_NAME}" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null || echo "None")

    if [ "${SG_ID}" != "None" ] && [ "${SG_ID}" != "" ]; then
        log_info "Security group already exists: ${SG_ID}"
    else
        # Get default VPC
        VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)

        if [ "${VPC_ID}" == "None" ] || [ -z "${VPC_ID}" ]; then
            log_error "No default VPC found. Please create a default VPC or specify one."
            exit 1
        fi

        log_info "Using VPC: ${VPC_ID}"

        # Create security group
        SG_ID=$(aws ec2 create-security-group \
            --group-name "${SG_NAME}" \
            --description "Security group for PUAR RDS PostgreSQL" \
            --vpc-id "${VPC_ID}" \
            --query "GroupId" \
            --output text)

        log_info "Created security group: ${SG_ID}"

        # Allow PostgreSQL from anywhere (for App Runner - it doesn't have fixed IPs)
        # In production, use VPC connector for App Runner
        aws ec2 authorize-security-group-ingress \
            --group-id "${SG_ID}" \
            --protocol tcp \
            --port 5432 \
            --cidr 0.0.0.0/0

        log_info "Added PostgreSQL ingress rule"
    fi

    export RDS_SECURITY_GROUP_ID="${SG_ID}"
}

# ============================================================================
# Create RDS PostgreSQL Instance
# ============================================================================
create_rds_instance() {
    log_step "Creating RDS PostgreSQL instance..."

    DB_INSTANCE_ID="${APP_NAME}-db"

    # Check if RDS instance exists
    if aws rds describe-db-instances --db-instance-identifier "${DB_INSTANCE_ID}" &> /dev/null; then
        log_info "RDS instance already exists"
        DB_ENDPOINT=$(aws rds describe-db-instances \
            --db-instance-identifier "${DB_INSTANCE_ID}" \
            --query "DBInstances[0].Endpoint.Address" \
            --output text)
    else
        log_info "Creating RDS instance (this may take 5-10 minutes)..."

        aws rds create-db-instance \
            --db-instance-identifier "${DB_INSTANCE_ID}" \
            --db-instance-class "${DB_INSTANCE_CLASS}" \
            --engine postgres \
            --engine-version "${DB_ENGINE_VERSION}" \
            --allocated-storage "${DB_ALLOCATED_STORAGE}" \
            --master-username "${DB_USER}" \
            --master-user-password "${DB_PASSWORD}" \
            --db-name "${DB_NAME}" \
            --vpc-security-group-ids "${RDS_SECURITY_GROUP_ID}" \
            --publicly-accessible \
            --backup-retention-period 7 \
            --storage-type gp3 \
            --no-multi-az \
            --tags "Key=Application,Value=${APP_NAME}" "Key=Environment,Value=${ENVIRONMENT}"

        log_info "Waiting for RDS instance to be available..."
        aws rds wait db-instance-available --db-instance-identifier "${DB_INSTANCE_ID}"

        DB_ENDPOINT=$(aws rds describe-db-instances \
            --db-instance-identifier "${DB_INSTANCE_ID}" \
            --query "DBInstances[0].Endpoint.Address" \
            --output text)

        log_info "RDS instance created: ${DB_ENDPOINT}"
    fi

    export DB_HOST="${DB_ENDPOINT}"
}

# ============================================================================
# Create ECR Repository
# ============================================================================
create_ecr_repository() {
    log_step "Creating ECR repository..."

    ECR_REPO_NAME="${APP_NAME}"

    if aws ecr describe-repositories --repository-names "${ECR_REPO_NAME}" &> /dev/null; then
        log_info "ECR repository already exists"
    else
        aws ecr create-repository \
            --repository-name "${ECR_REPO_NAME}" \
            --image-scanning-configuration scanOnPush=true \
            --tags "Key=Application,Value=${APP_NAME}"
        log_info "ECR repository created"
    fi

    ECR_REPO_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"
    export ECR_REPO_URI
}

# ============================================================================
# Build and Push Docker Image
# ============================================================================
build_and_push_image() {
    log_step "Building and pushing Docker image..."

    cd "${PROJECT_DIR}"

    # Login to ECR
    aws ecr get-login-password --region "${AWS_REGION}" | \
        docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Build image
    IMAGE_TAG="$(date +%Y%m%d%H%M%S)"
    docker build \
        --target production \
        --platform linux/amd64 \
        -t "${ECR_REPO_URI}:latest" \
        -t "${ECR_REPO_URI}:${IMAGE_TAG}" \
        .

    # Push images
    docker push "${ECR_REPO_URI}:latest"
    docker push "${ECR_REPO_URI}:${IMAGE_TAG}"

    log_info "Docker image pushed: ${ECR_REPO_URI}:${IMAGE_TAG}"
    export DOCKER_IMAGE_TAG="${IMAGE_TAG}"
}

# ============================================================================
# Create IAM Role for App Runner
# ============================================================================
create_apprunner_role() {
    log_step "Creating IAM role for App Runner..."

    ROLE_NAME="${APP_NAME}-apprunner-role"
    INSTANCE_ROLE_NAME="${APP_NAME}-apprunner-instance-role"

    # Access role (for ECR access)
    if ! aws iam get-role --role-name "${ROLE_NAME}" &> /dev/null; then
        log_info "Creating App Runner access role..."

        cat > /tmp/apprunner-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "build.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

        aws iam create-role \
            --role-name "${ROLE_NAME}" \
            --assume-role-policy-document file:///tmp/apprunner-trust-policy.json

        aws iam attach-role-policy \
            --role-name "${ROLE_NAME}" \
            --policy-arn "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"

        log_info "App Runner access role created"
    else
        log_info "App Runner access role already exists"
    fi

    # Instance role (for Secrets Manager access)
    if ! aws iam get-role --role-name "${INSTANCE_ROLE_NAME}" &> /dev/null; then
        log_info "Creating App Runner instance role..."

        cat > /tmp/apprunner-instance-trust-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "tasks.apprunner.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

        aws iam create-role \
            --role-name "${INSTANCE_ROLE_NAME}" \
            --assume-role-policy-document file:///tmp/apprunner-instance-trust-policy.json

        # Create policy for Secrets Manager access
        cat > /tmp/secrets-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:${AWS_REGION}:${AWS_ACCOUNT_ID}:secret:${APP_NAME}/*"
            ]
        }
    ]
}
EOF

        aws iam put-role-policy \
            --role-name "${INSTANCE_ROLE_NAME}" \
            --policy-name "SecretsManagerAccess" \
            --policy-document file:///tmp/secrets-policy.json

        log_info "App Runner instance role created"
    else
        log_info "App Runner instance role already exists"
    fi

    # Wait for role propagation
    sleep 10

    ACCESS_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"
    INSTANCE_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${INSTANCE_ROLE_NAME}"
    export ACCESS_ROLE_ARN INSTANCE_ROLE_ARN
}

# ============================================================================
# Create App Runner Service
# ============================================================================
create_apprunner_service() {
    log_step "Creating App Runner service..."

    SERVICE_NAME="${APP_NAME}-api"

    # Check if service exists
    EXISTING_SERVICE=$(aws apprunner list-services \
        --query "ServiceSummaryList[?ServiceName=='${SERVICE_NAME}'].ServiceArn" \
        --output text)

    if [ -n "${EXISTING_SERVICE}" ] && [ "${EXISTING_SERVICE}" != "None" ]; then
        log_info "App Runner service already exists, updating..."

        aws apprunner update-service \
            --service-arn "${EXISTING_SERVICE}" \
            --source-configuration '{
                "ImageRepository": {
                    "ImageIdentifier": "'"${ECR_REPO_URI}:latest"'",
                    "ImageRepositoryType": "ECR",
                    "ImageConfiguration": {
                        "Port": "8000",
                        "RuntimeEnvironmentVariables": {
                            "ENVIRONMENT": "'"${ENVIRONMENT}"'",
                            "DEBUG": "false",
                            "DB_HOST": "'"${DB_HOST}"'",
                            "DB_PORT": "5432",
                            "DB_USER": "'"${DB_USER}"'",
                            "DB_PASSWORD": "'"${DB_PASSWORD}"'",
                            "DB_NAME": "'"${DB_NAME}"'",
                            "JWT_SECRET_KEY": "'"${JWT_SECRET}"'",
                            "AWS_REGION": "'"${AWS_REGION}"'"
                        }
                    }
                },
                "AutoDeploymentsEnabled": false,
                "AuthenticationConfiguration": {
                    "AccessRoleArn": "'"${ACCESS_ROLE_ARN}"'"
                }
            }'

        SERVICE_ARN="${EXISTING_SERVICE}"
    else
        log_info "Creating new App Runner service..."

        SERVICE_ARN=$(aws apprunner create-service \
            --service-name "${SERVICE_NAME}" \
            --source-configuration '{
                "ImageRepository": {
                    "ImageIdentifier": "'"${ECR_REPO_URI}:latest"'",
                    "ImageRepositoryType": "ECR",
                    "ImageConfiguration": {
                        "Port": "8000",
                        "RuntimeEnvironmentVariables": {
                            "ENVIRONMENT": "'"${ENVIRONMENT}"'",
                            "DEBUG": "false",
                            "DB_HOST": "'"${DB_HOST}"'",
                            "DB_PORT": "5432",
                            "DB_USER": "'"${DB_USER}"'",
                            "DB_PASSWORD": "'"${DB_PASSWORD}"'",
                            "DB_NAME": "'"${DB_NAME}"'",
                            "JWT_SECRET_KEY": "'"${JWT_SECRET}"'",
                            "AWS_REGION": "'"${AWS_REGION}"'"
                        }
                    }
                },
                "AutoDeploymentsEnabled": false,
                "AuthenticationConfiguration": {
                    "AccessRoleArn": "'"${ACCESS_ROLE_ARN}"'"
                }
            }' \
            --instance-configuration '{
                "Cpu": "'"${APP_RUNNER_CPU}"'",
                "Memory": "'"${APP_RUNNER_MEMORY}"'",
                "InstanceRoleArn": "'"${INSTANCE_ROLE_ARN}"'"
            }' \
            --health-check-configuration '{
                "Protocol": "HTTP",
                "Path": "/api/v1/health",
                "Interval": 10,
                "Timeout": 5,
                "HealthyThreshold": 1,
                "UnhealthyThreshold": 5
            }' \
            --tags "Key=Application,Value=${APP_NAME}" "Key=Environment,Value=${ENVIRONMENT}" \
            --query "Service.ServiceArn" \
            --output text)
    fi

    log_info "Waiting for App Runner service to be running..."

    # Poll for service status
    while true; do
        STATUS=$(aws apprunner describe-service \
            --service-arn "${SERVICE_ARN}" \
            --query "Service.Status" \
            --output text)

        log_info "Service status: ${STATUS}"

        if [ "${STATUS}" == "RUNNING" ]; then
            break
        elif [ "${STATUS}" == "CREATE_FAILED" ] || [ "${STATUS}" == "DELETE_FAILED" ]; then
            log_error "Service creation failed!"
            exit 1
        fi

        sleep 15
    done

    # Get service URL
    API_URL=$(aws apprunner describe-service \
        --service-arn "${SERVICE_ARN}" \
        --query "Service.ServiceUrl" \
        --output text)

    export API_URL="https://${API_URL}"
    log_info "App Runner service URL: ${API_URL}"
}

# ============================================================================
# Create S3 Bucket for Frontend
# ============================================================================
create_frontend_bucket() {
    log_step "Creating S3 bucket for frontend..."

    # Use a unique bucket name
    PATIENT_BUCKET="${APP_NAME}-patient-pwa-${AWS_ACCOUNT_ID}"
    DOCTOR_BUCKET="${APP_NAME}-doctor-pwa-${AWS_ACCOUNT_ID}"

    for BUCKET in "${PATIENT_BUCKET}" "${DOCTOR_BUCKET}"; do
        if aws s3api head-bucket --bucket "${BUCKET}" 2>/dev/null; then
            log_info "Bucket ${BUCKET} already exists"
        else
            log_info "Creating bucket ${BUCKET}..."

            if [ "${AWS_REGION}" == "us-east-1" ]; then
                aws s3api create-bucket --bucket "${BUCKET}"
            else
                aws s3api create-bucket \
                    --bucket "${BUCKET}" \
                    --create-bucket-configuration LocationConstraint="${AWS_REGION}"
            fi

            # Enable static website hosting
            aws s3 website "s3://${BUCKET}" \
                --index-document index.html \
                --error-document index.html

            # Set bucket policy for public read
            cat > /tmp/bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::${BUCKET}/*"
        }
    ]
}
EOF

            # Disable block public access
            aws s3api put-public-access-block \
                --bucket "${BUCKET}" \
                --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

            sleep 2

            aws s3api put-bucket-policy \
                --bucket "${BUCKET}" \
                --policy file:///tmp/bucket-policy.json

            log_info "Bucket ${BUCKET} created and configured"
        fi
    done

    export PATIENT_BUCKET DOCTOR_BUCKET
}

# ============================================================================
# Build and Deploy Frontend
# ============================================================================
build_and_deploy_frontend() {
    log_step "Building and deploying frontend applications..."

    cd "${PROJECT_DIR}"

    # Build Patient PWA
    log_info "Building Patient PWA..."
    cd "${PROJECT_DIR}/frontend/patient"

    # Create .env file with API URL
    echo "VITE_API_URL=${API_URL}" > .env

    npm install
    npm run build

    # Upload to S3
    aws s3 sync dist/ "s3://${PATIENT_BUCKET}/" --delete
    log_info "Patient PWA deployed to S3"

    # Build Doctor PWA
    log_info "Building Doctor PWA..."
    cd "${PROJECT_DIR}/frontend/doctor"

    echo "VITE_API_URL=${API_URL}" > .env

    npm install
    npm run build

    aws s3 sync dist/ "s3://${DOCTOR_BUCKET}/" --delete
    log_info "Doctor PWA deployed to S3"

    # Get website URLs
    PATIENT_URL="http://${PATIENT_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"
    DOCTOR_URL="http://${DOCTOR_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"

    export PATIENT_URL DOCTOR_URL
}

# ============================================================================
# Create CloudFront Distribution (for HTTPS)
# ============================================================================
create_cloudfront_distributions() {
    log_step "Creating CloudFront distributions for HTTPS..."

    for APP_TYPE in "patient" "doctor"; do
        if [ "${APP_TYPE}" == "patient" ]; then
            BUCKET="${PATIENT_BUCKET}"
        else
            BUCKET="${DOCTOR_BUCKET}"
        fi

        DIST_NAME="${APP_NAME}-${APP_TYPE}-cf"

        # Check if distribution exists by checking for a tag
        EXISTING_DIST=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[?Comment=='${DIST_NAME}'].Id" \
            --output text 2>/dev/null || echo "")

        if [ -n "${EXISTING_DIST}" ] && [ "${EXISTING_DIST}" != "None" ]; then
            log_info "CloudFront distribution for ${APP_TYPE} already exists"
            DIST_ID="${EXISTING_DIST}"
        else
            log_info "Creating CloudFront distribution for ${APP_TYPE}..."

            cat > /tmp/cf-config-${APP_TYPE}.json << EOF
{
    "CallerReference": "${DIST_NAME}-$(date +%s)",
    "Comment": "${DIST_NAME}",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-${BUCKET}",
                "DomainName": "${BUCKET}.s3-website-${AWS_REGION}.amazonaws.com",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only",
                    "OriginSslProtocols": {
                        "Quantity": 1,
                        "Items": ["TLSv1.2"]
                    }
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-${BUCKET}",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "DefaultRootObject": "index.html",
    "PriceClass": "PriceClass_100"
}
EOF

            DIST_ID=$(aws cloudfront create-distribution \
                --distribution-config file:///tmp/cf-config-${APP_TYPE}.json \
                --query "Distribution.Id" \
                --output text)

            log_info "CloudFront distribution created: ${DIST_ID}"
        fi

        # Get distribution domain
        DIST_DOMAIN=$(aws cloudfront get-distribution \
            --id "${DIST_ID}" \
            --query "Distribution.DomainName" \
            --output text)

        if [ "${APP_TYPE}" == "patient" ]; then
            PATIENT_CF_URL="https://${DIST_DOMAIN}"
            export PATIENT_CF_URL
        else
            DOCTOR_CF_URL="https://${DIST_DOMAIN}"
            export DOCTOR_CF_URL
        fi

        log_info "${APP_TYPE} CloudFront URL: https://${DIST_DOMAIN}"
    done
}

# ============================================================================
# Verify Deployment
# ============================================================================
verify_deployment() {
    log_step "Verifying deployment..."

    # Test API health endpoint
    log_info "Testing API health endpoint..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/api/v1/health" || echo "000")

    if [ "${HTTP_CODE}" == "200" ]; then
        log_info "API health check passed!"
        HEALTH_RESPONSE=$(curl -s "${API_URL}/api/v1/health")
        log_info "Health response: ${HEALTH_RESPONSE}"
    else
        log_warn "API health check returned HTTP ${HTTP_CODE}"
        log_warn "The service might still be starting up. Check logs with:"
        log_warn "  aws logs tail /aws/apprunner/${APP_NAME}-api/application --follow"
    fi
}

# ============================================================================
# Print Summary
# ============================================================================
print_summary() {
    log_step "Deployment Summary"
    echo ""
    echo "============================================================"
    echo "  PUAR-Patients Deployment Complete!"
    echo "============================================================"
    echo ""
    echo "  API (Backend):"
    echo "    URL: ${API_URL}"
    echo "    Health: ${API_URL}/api/v1/health"
    echo ""
    echo "  Patient PWA:"
    echo "    S3 URL: ${PATIENT_URL}"
    echo "    CloudFront (HTTPS): ${PATIENT_CF_URL:-pending}"
    echo ""
    echo "  Doctor PWA:"
    echo "    S3 URL: ${DOCTOR_URL}"
    echo "    CloudFront (HTTPS): ${DOCTOR_CF_URL:-pending}"
    echo ""
    echo "  Database:"
    echo "    Host: ${DB_HOST}"
    echo "    Database: ${DB_NAME}"
    echo "    User: ${DB_USER}"
    echo ""
    echo "============================================================"
    echo ""
    echo "  Note: CloudFront distributions may take 10-15 minutes to"
    echo "  fully propagate. Use S3 URLs for immediate testing."
    echo ""
    echo "============================================================"

    # Save URLs to file for reference
    cat > "${PROJECT_DIR}/scripts/aws/deployment-info.txt" << EOF
# PUAR-Patients Deployment Info
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

API_URL=${API_URL}
PATIENT_URL=${PATIENT_URL}
PATIENT_CF_URL=${PATIENT_CF_URL:-pending}
DOCTOR_URL=${DOCTOR_URL}
DOCTOR_CF_URL=${DOCTOR_CF_URL:-pending}
DB_HOST=${DB_HOST}
EOF

    log_info "Deployment info saved to scripts/aws/deployment-info.txt"
}

# ============================================================================
# Main
# ============================================================================
main() {
    log_info "Starting PUAR-Patients AWS deployment..."
    echo ""

    check_prerequisites
    setup_database_secret
    setup_jwt_secret
    create_security_group
    create_rds_instance
    create_ecr_repository
    build_and_push_image
    create_apprunner_role
    create_apprunner_service
    create_frontend_bucket
    build_and_deploy_frontend
    create_cloudfront_distributions
    verify_deployment
    print_summary

    log_info "Deployment complete!"
}

# Run
main "$@"
