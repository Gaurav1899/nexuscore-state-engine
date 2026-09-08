# Google Cloud Deployment Guide - NexusCore State Engine

## 📋 Prerequisites

1. **Google Cloud Account** - [Create Free Account](https://cloud.google.com/free)
2. **gcloud CLI** - [Install](https://cloud.google.com/sdk/docs/install)
3. **Docker** - [Install](https://docs.docker.com/install/)
4. **Project Repository** - Already set up at `Gaurav1899/nexuscore-state-engine`

---

## 🚀 Deployment Steps

### Step 1: Set Up Google Cloud Project

```bash
# Create a new project
gcloud projects create nexuscore-engine --name="NexusCore State Engine"

# Set the project as active
gcloud config set project nexuscore-engine

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  container.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com
```

### Step 2: Configure Authentication

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set up application default credentials
gcloud auth application-default login
```

### Step 3: Clone Repository

```bash
git clone https://github.com/Gaurav1899/nexuscore-state-engine.git
cd nexuscore-state-engine
```

### Step 4: Build and Push Docker Image

```bash
# Set your project ID
export PROJECT_ID=nexuscore-engine
export SERVICE_NAME=nexuscore-chat
export REGION=us-central1

# Build Docker image
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### Step 5: Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars ENVIRONMENT=production
```

### Step 6: Get Service URL

```bash
# Retrieve your service URL
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)'
```

---

## 🌐 Accessing Your Deployment

Once deployed, access your NexusCore State Engine at:

- **Chat Interface**: `https://your-service-url.run.app/chat.html`
- **Dashboard**: `https://your-service-url.run.app/webapp.html`
- **Original UI**: `https://your-service-url.run.app/index.html`
- **API Endpoint**: `https://your-service-url.run.app/api`

---

## 📊 Monitoring & Logs

### View Logs

```bash
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION

# Stream live logs
gcloud run services logs read $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --limit 100 \
  --follow
```

### Monitor Performance

```bash
# View service metrics
gcloud monitoring dashboards create --config-from-file=- <<EOF
{
  "displayName": "NexusCore State Engine",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" resource.label.service_name=\"$SERVICE_NAME\""
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
```

---

## 💾 Database Setup (Optional)

For persistent storage, set up Cloud SQL:

```bash
# Create Cloud SQL instance
gcloud sql instances create nexuscore-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create nexuscore \
  --instance=nexuscore-db

# Create user
gcloud sql users create nexuscore \
  --instance=nexuscore-db \
  --password=your-secure-password
```

Update `app.py` to use Cloud SQL connection string.

---

## 🔐 Security Best Practices

### 1. Add Authentication

```python
# In app.py
from google.auth.transport import requests
from google.oauth2 import id_token

@app.middleware("http")
async def verify_token(request, call_next):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    try:
        id_token.verify_oauth2_token(token, requests.Request())
    except:
        return JSONResponse({"detail": "Invalid token"}, status_code=401)
    return await call_next(request)
```

### 2. Set Environment Variables

```bash
# Store sensitive data in Secret Manager
gcloud secrets create nexuscore-api-key --data-file=- <<< "your-secret-key"

# Reference in Cloud Run
gcloud run deploy $SERVICE_NAME \
  --update-secrets=API_KEY=nexuscore-api-key:latest
```

### 3. Enable CORS Properly

```python
# Update CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Scaling Configuration

### Auto-scaling Settings

```bash
gcloud run services update $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --min-instances=1 \
  --max-instances=100 \
  --concurrency=80
```

### Environment Variables

```bash
gcloud run services update $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --set-env-vars=\
MAX_WORKERS=4,\
MEMORY_LIMIT=1024,\
LOG_LEVEL=INFO
```

---

## 💰 Cost Optimization

### Cloud Run Pricing
- **Compute**: $0.00002400 per CPU-second
- **Requests**: $0.40 per million requests
- **Networking**: $0.12 per GB (egress)

### Reduce Costs

1. **Use smaller instances**
   ```bash
   gcloud run deploy $SERVICE_NAME --memory=256Mi --cpu=0.5
   ```

2. **Set minimum instances to 0**
   ```bash
   gcloud run services update $SERVICE_NAME --min-instances=0
   ```

3. **Enable VPC Connector (if needed)**
   ```bash
   gcloud run services update $SERVICE_NAME \
     --vpc-connector=nexuscore-connector \
     --vpc-egress=private-ranges-only
   ```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Integration

Create `.github/workflows/deploy-gcp.yml`:

```yaml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v0
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Build and Push Docker Image
        run: |
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/nexuscore-chat
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy nexuscore-chat \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/nexuscore-chat \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
```

---

## 🛠️ Troubleshooting

### Service Won't Start

```bash
# Check logs
gcloud run services logs read $SERVICE_NAME --limit 50

# Verify image exists
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Test locally first
docker run -p 8000:8000 gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
```

### High Latency

```bash
# Increase memory
gcloud run services update $SERVICE_NAME --memory=1Gi

# Increase CPU
gcloud run services update $SERVICE_NAME --cpu=2

# Check concurrency
gcloud run services describe $SERVICE_NAME --format="value(spec.template.spec.containerConcurrency)"
```

### Out of Memory

```bash
# Check current memory allocation
gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format="value(spec.template.spec.containers[0].resources.limits.memory)"

# Increase memory to 1GB
gcloud run services update $SERVICE_NAME --memory=1Gi
```

---

## 🚀 Advanced Deployment Options

### Option 1: Cloud Run with Cloud Build

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_SERVICE_NAME=$SERVICE_NAME,_REGION=$REGION
```

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME', '.']
  
  # Push
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/$_SERVICE_NAME']
  
  # Deploy
  - name: 'gcr.io/cloud-builders/gke-deploy'
    args:
      - run
      - --filename=k8s/
      - --image=gcr.io/$PROJECT_ID/$_SERVICE_NAME
      - --location=$_REGION
      - --cluster=nexuscore-cluster

images:
  - gcr.io/$PROJECT_ID/$_SERVICE_NAME
```

### Option 2: Kubernetes Engine (GKE)

```bash
# Create cluster
gcloud container clusters create nexuscore-cluster \
  --region=$REGION \
  --num-nodes=3 \
  --machine-type=n1-standard-1

# Deploy
kubectl apply -f k8s/deployment.yaml

# Expose service
kubectl expose deployment nexuscore-chat \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8000
```

---

## 📱 Custom Domain

### Set Up Custom Domain

```bash
# Add custom domain
gcloud run domain-mappings create \
  --service=$SERVICE_NAME \
  --domain=yourdomain.com \
  --region=$REGION

# Update DNS records (in your domain registrar)
# Add CNAME: yourdomain.com -> ghs.googleusercontent.com
```

---

## 🧹 Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete $SERVICE_NAME --region=$REGION

# Delete Docker image
gcloud container images delete gcr.io/$PROJECT_ID/$SERVICE_NAME

# Delete project (if needed)
gcloud projects delete $PROJECT_ID
```

---

## 📞 Support & Resources

- **Google Cloud Documentation**: https://cloud.google.com/docs
- **Cloud Run Quickstart**: https://cloud.google.com/run/docs/quickstarts
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Docker Documentation**: https://docs.docker.com/

---

## ✅ Deployment Checklist

- [ ] Google Cloud Account created
- [ ] gcloud CLI installed and authenticated
- [ ] Docker installed
- [ ] Repository cloned
- [ ] APIs enabled (Cloud Run, Container Registry, Cloud Build)
- [ ] Docker image built successfully
- [ ] Image pushed to Container Registry
- [ ] Cloud Run service deployed
- [ ] Service URL obtained
- [ ] Frontend tested (chat, webapp, dashboard)
- [ ] API endpoints working
- [ ] Logs monitored
- [ ] Security configured
- [ ] Custom domain set up (optional)
- [ ] Backups configured (if using database)

---

## 🎉 Success!

Your NexusCore State Engine is now live on Google Cloud! 🚀

**Access your services:**
- Chat: `https://your-service.run.app/chat.html`
- Dashboard: `https://your-service.run.app/webapp.html`
- API: `https://your-service.run.app/api`

**Next Steps:**
1. Share the URL with your team
2. Configure monitoring and alerts
3. Set up backups
4. Document your deployment
5. Plan for scaling

---

Last Updated: 2026-09-08
