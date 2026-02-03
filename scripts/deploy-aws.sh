#!/usr/bin/env bash
# PUAR-Patients AWS Deployment Script
# Deploys to AWS ECS with RDS PostgreSQL

set -euo pipefail

# Configuration
APP_NAME="${APP_NAME:-puar-patients}"
AWS_REGION="${AWS_REGION:-eu-west-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${APP_NAME}"
ENVIRONMENT="${ENVIRONMENT:-production}"
CLUSTER_NAME="${APP_NAME}-cluster"
SERVICE_NAME="${APP_NAME}-service"

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Create ECR repository if it doesn't exist
create_ecr_repo() {
    log_info "Checking ECR repository..."

    if ! aws ecr describe-repositories --repository-names "${APP_NAME}" --region "${AWS_REGION}" &> /dev/null; then
        log_info "Creating ECR repository ${APP_NAME}..."
        aws ecr create-repository \
            --repository-name "${APP_NAME}" \
            --region "${AWS_REGION}" \
            --image-scanning-configuration scanOnPush=true
    else
        log_info "ECR repository exists"
    fi
}

# Build and push Docker image
build_and_push() {
    log_info "Building Docker image..."

    # Login to ECR
    aws ecr get-login-password --region "${AWS_REGION}" | \
        docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Build image
    docker build \
        --target production \
        -t "${APP_NAME}:latest" \
        -t "${ECR_REPO}:latest" \
        -t "${ECR_REPO}:$(git rev-parse --short HEAD)" \
        .

    # Push to ECR
    log_info "Pushing image to ECR..."
    docker push "${ECR_REPO}:latest"
    docker push "${ECR_REPO}:$(git rev-parse --short HEAD)"

    log_info "Image pushed successfully"
}

# Create ECS task definition
create_task_definition() {
    log_info "Creating/updating ECS task definition..."

    cat > /tmp/task-definition.json << EOF
{
    "family": "${APP_NAME}",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
    "taskRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskRole",
    "containerDefinitions": [
        {
            "name": "${APP_NAME}",
            "image": "${ECR_REPO}:latest",
            "essential": true,
            "portMappings": [
                {
                    "containerPort": 8000,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {"name": "ENVIRONMENT", "value": "${ENVIRONMENT}"},
                {"name": "DEBUG", "value": "false"}
            ],
            "secrets": [
                {"name": "DB_HOST", "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/${APP_NAME}/db-host"},
                {"name": "DB_USER", "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/${APP_NAME}/db-user"},
                {"name": "DB_PASSWORD", "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/${APP_NAME}/db-password"},
                {"name": "DB_NAME", "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/${APP_NAME}/db-name"},
                {"name": "JWT_SECRET_KEY", "valueFrom": "arn:aws:ssm:${AWS_REGION}:${AWS_ACCOUNT_ID}:parameter/${APP_NAME}/jwt-secret"}
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/${APP_NAME}",
                    "awslogs-region": "${AWS_REGION}",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:8000/api/v1/health || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF

    aws ecs register-task-definition \
        --cli-input-json file:///tmp/task-definition.json \
        --region "${AWS_REGION}"

    log_info "Task definition registered"
}

# Update or create ECS service
update_service() {
    log_info "Updating ECS service..."

    if aws ecs describe-services --cluster "${CLUSTER_NAME}" --services "${SERVICE_NAME}" --region "${AWS_REGION}" | grep -q "ACTIVE"; then
        # Update existing service
        aws ecs update-service \
            --cluster "${CLUSTER_NAME}" \
            --service "${SERVICE_NAME}" \
            --task-definition "${APP_NAME}" \
            --force-new-deployment \
            --region "${AWS_REGION}"
        log_info "Service updated"
    else
        log_warn "Service doesn't exist. Please create the ECS cluster and service manually or via CloudFormation."
        log_info "To create a service, you'll need:"
        log_info "  1. VPC with public/private subnets"
        log_info "  2. Security groups"
        log_info "  3. Application Load Balancer"
        log_info "  4. ECS Cluster"
        log_info "  5. RDS PostgreSQL instance"
    fi
}

# Wait for deployment
wait_for_deployment() {
    log_info "Waiting for deployment to complete..."

    aws ecs wait services-stable \
        --cluster "${CLUSTER_NAME}" \
        --services "${SERVICE_NAME}" \
        --region "${AWS_REGION}"

    log_info "Deployment completed successfully!"
}

# Main deployment flow
main() {
    log_info "Starting deployment of ${APP_NAME} to AWS..."
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Region: ${AWS_REGION}"

    check_prerequisites
    create_ecr_repo
    build_and_push
    create_task_definition
    update_service
    wait_for_deployment

    log_info "Deployment complete!"
    log_info "Check your load balancer for the public URL"
}

# Run
main "$@"
