# This script deploys our backend to Google Cloud Run.

REGION=${REGION:-"us-central1"}
PROJECT_ID=${PROJECT_ID:-"rede-labs"}
# Need to be exported for sudo to work
export IMAGE="gcr.io/$PROJECT_ID/marketplace-backend:latest"

# Get all environment variables except PORT
#
# We use --set-env-vars and not Google Secret Manager because we don't want to
# pay for Google Secret Manager and this is only a student project.
ENV_VARS=$(awk -F'=' '$1 != "PORT" {printf "%s=%s,",$1,$2}' .env | sed 's/,$//')

set -e # Exit on error

sudo docker buildx build --platform linux/amd64 -t $IMAGE --push .
sudo docker push $IMAGE

gcloud run deploy marketplace-backend \
    --image $IMAGE \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --set-env-vars="$ENV_VARS" \
    --project $PROJECT_ID \
    --timeout 15m \
    --memory 512Mi
