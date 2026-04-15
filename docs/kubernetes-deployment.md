# Kubernetes Deployment Guide

## Prerequisites

1. **Docker Desktop** - Running
2. **k3d** - Lightweight Kubernetes
   ```powershell
   winget install k3d
   ```
3. **kubectl** - Kubernetes CLI
   ```powershell
   winget install kubectl
   ```

## Quick Start

### 1. Update Secrets

Edit `k8s/secrets.yaml` and replace placeholder values:
- GEMINI_API_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- OWNER_PHONE
- GMAIL_USER

### 2. Deploy to k3d

**Windows (PowerShell):**
```powershell
.\deploy.ps1
```

**Windows (Git Bash):**
```bash
bash deploy.sh
```

**Mac/Linux:**
```bash
bash deploy.sh
```

### 3. Test Deployment

**Windows:**
```powershell
.\test-k8s.ps1
```

**Mac/Linux:**
```bash
# Run manual tests
kubectl get pods -n nur-scents
kubectl get services -n nur-scents
curl http://localhost:8080/health
```

## Architecture

```
┌─────────────────────────────────────────┐
│           k3d Cluster                   │
│  ┌───────────────────────────────────┐  │
│  │  nur-scents Namespace             │  │
│  │                                   │  │
│  │  ┌──────────────┐                │  │
│  │  │  Ingress     │                │  │
│  │  └──────┬───────┘                │  │
│  │         │                         │  │
│  │  ┌──────▼───────┐                │  │
│  │  │   Service    │                │  │
│  │  └──────┬───────┘                │  │
│  │         │                         │  │
│  │  ┌──────▼─────────────────────┐  │  │
│  │  │  API Deployment (3 pods)    │  │  │
│  │  │  ┌─────┐ ┌─────┐ ┌─────┐   │  │  │
│  │  │  │Pod1 │ │Pod2 │ │Pod3 │   │  │  │
│  │  │  └─────┘ └─────┘ └─────┘   │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ Worker Deployment (3 pods)  │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  ┌──────────────┐                │  │
│  │  │   Kafka      │                │  │
│  │  └──────────────┘                │  │
│  │                                   │  │
│  │  ┌──────────────┐                │  │
│  │  │   Redis      │                │  │
│  │  └──────────────┘                │  │
│  │                                   │  │
│  │  ┌──────────────┐                │  │
│  │  │  PostgreSQL  │                │  │
│  │  └──────────────┘                │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Components

### Deployments
- **nur-scents-api**: FastAPI backend (3 replicas)
- **nur-scents-worker**: Message processor (3 replicas)
- **nurscents-postgres**: PostgreSQL with pgvector
- **nurscents-kafka**: Apache Kafka broker
- **nurscents-redis**: Redis cache

### Services
- **nur-scents-api-service**: ClusterIP for API pods
- **nurscents-postgres**: PostgreSQL internal
- **nurscents-kafka**: Kafka internal
- **nurscents-redis**: Redis internal

### Autoscaling
- **API HPA**: 2-10 replicas based on CPU/memory
- **Worker HPA**: 2-6 replicas based on CPU

## Configuration

### Environment Variables (ConfigMap)
- KAFKA_BOOTSTRAP_SERVERS
- REDIS_URL
- DATABASE_URL
- BUSINESS_NAME
- LOG_LEVEL

### Secrets
- GEMINI_API_KEY
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- OWNER_PHONE
- GMAIL_USER
- POSTGRES_PASSWORD

## Monitoring

### Check Pod Status
```bash
kubectl get pods -n nur-scents
kubectl describe pod <pod-name> -n nur-scents
```

### View Logs
```bash
# All API pods
kubectl logs -l app=nur-scents-api -n nur-scents

# Specific pod
kubectl logs <pod-name> -n nur-scents -f

# Worker logs
kubectl logs -l app=nur-scents-worker -n nur-scents
```

### Check Services
```bash
kubectl get services -n nur-scents
kubectl describe service nur-scents-api-service -n nur-scents
```

### Check HPA Status
```bash
kubectl get hpa -n nur-scents
kubectl describe hpa nur-scents-api-hpa -n nur-scents
```

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n nur-scents

# Describe pod
kubectl describe pod <pod-name> -n nur-scents

# Check logs
kubectl logs <pod-name> -n nur-scents
```

### Image Pull Errors
```bash
# Re-import images to k3d
k3d image import nur-scents-api:latest -c nur-scents
k3d image import nur-scents-worker:latest -c nur-scents

# Restart deployment
kubectl rollout restart deployment nur-scents-api -n nur-scents
```

### Port Already in Use
```bash
# Check what's using port 8080
netstat -ano | findstr :8080

# Or recreate cluster with different port
k3d cluster delete nur-scents
k3d cluster create nur-scents --port "9090:80@loadbalancer" --agents 2
```

### Database Connection Issues
```bash
# Check PostgreSQL pod
kubectl get pods -l app=nurscents-postgres -n nur-scents

# Check PostgreSQL logs
kubectl logs -l app=nurscents-postgres -n nur-scents

# Test connection
kubectl exec -it <postgres-pod> -n nurscents -- psql -U nurscents_user -d nurscents
```

## Scaling

### Manual Scaling
```bash
# Scale API to 5 replicas
kubectl scale deployment nur-scents-api --replicas=5 -n nur-scents

# Scale worker to 4 replicas
kubectl scale deployment nur-scents-worker --replicas=4 -n nur-scents
```

### Auto-Scaling (HPA)
HPA automatically scales based on CPU/memory usage. Configure ranges in `k8s/hpa.yaml`.

## Cleanup

### Stop Deployment
**PowerShell:**
```powershell
.\teardown.ps1
```

**Bash:**
```bash
bash teardown.sh
```

### Delete Entire Cluster
```bash
k3d cluster delete nur-scents
```

## Performance

### Resource Limits
- API Pods: 256Mi-512Mi RAM, 250m-500m CPU
- Worker Pods: 256Mi-512Mi RAM, 250m-500m CPU

### Expected Performance
- 3 API pods: ~1500 requests/second
- 3 Worker pods: ~900 messages/minute
- Auto-scaling up to 10 API pods under load

## Security

- Non-root user in containers
- Resource limits to prevent DoS
- Secrets for sensitive data
- Network policies (internal-only for databases)
- Health checks for pod recovery

## Next Steps

1. Configure external DNS for production
2. Set up monitoring (Prometheus/Grafana)
3. Configure TLS certificates
4. Set up centralized logging (ELK/Loki)
5. Configure backup/restore for PostgreSQL
6. Set up CI/CD pipeline
