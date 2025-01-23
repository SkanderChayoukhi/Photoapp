# Photo Sharing Application

## Overview
This project is a **photo-sharing application** built using **FastAPI** for backend services and **MongoDB** for database management. The architecture follows a **microservices** approach deployed on **Kubernetes** with services exposed via **Gravitee API Gateway** and secured with **Keycloak**.

## Features
- User authentication via **Keycloak**
- API Gateway using **Gravitee**
- Microservices-based architecture:
  - **Photo Service**: Handles photo uploads and retrieval
  - **Albums Service**: Manages photo albums
  - **Photographer Service**: Handles user profiles
  - **Tags Service**: Supports photo tagging
- Containerized using **Docker** and orchestrated with **Kubernetes**

## Technologies Used
- **Backend**: FastAPI, Python, Uvicorn, gRPC
- **Database**: MongoDB
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Authentication**: Keycloak
- **API Gateway**: Gravitee
- **CI/CD**: GitLab CI/CD

## Setup & Installation
### Prerequisites
- Install **Docker** and **Docker Compose**
- Install **Kubernetes (Minikube or K3s)**
- Install **kubectl** for Kubernetes management
- Install **Helm** for package management

### Clone the Repository
```sh
git clone https://github.com/yourusername/photo-sharing-app.git
cd photo-sharing-app
```

### Environment Variables
```
MONGO_HOST=mongo-service
PHOTOGRAPHER_HOST=photographer-service
PHOTO_HOST=photo-service
TAGS_HOST=tags-service
```

### Docker Setup
To build and run the services using **Docker Compose**:
```sh
docker-compose up --build
```

### Kubernetes Deployment
Apply the Kubernetes manifests:
```sh
kubectl apply -f k8s-photo.yml
kubectl apply -f k8s-album.yml
kubectl apply -f k8s-photographer.yml
kubectl apply -f k8s-tags.yml
```

### API Gateway Configuration
- Configure **Gravitee API Gateway** to route requests to microservices.
- Set up authentication with **Keycloak**.
- Ensure JWT tokens are properly validated.

## Usage
### Testing API Endpoints
Use **cURL** or **Postman** to interact with the API.

#### Example: Create a new album
```sh
curl -X POST \
  'http://album-service:8002/photographers/{photographer_id}/albums' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "My Album",
    "description": "Collection of travel photos",
    "cover_photo_id": "photo123"

  }'
```

## Troubleshooting
- **Photo Service Not Reachable**: Ensure the service is running and accessible inside Kubernetes (`kubectl get pods -o wide`).
- **JWT Authentication Issues**: Validate token using `jwt.io` and ensure Keycloak configuration is correct.
- **DNS Resolution Issues**: Verify Kubernetes DNS using `nslookup service-name.default.svc.cluster.local`.



