# Automated Dockerfile Generator

<p align="center">
  <img src="path/to/your/header-image.png" alt="Dockerfile Generator Pipeline" width="800">
</p>

<p align="center">
  Smart containerization for your programming projects. Built with AI.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/ollama-powered-green.svg" alt="Ollama Powered">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
</p>

## Table of Contents

- [Overview](#overview)
- [Purpose](#purpose)
- [Limitations](#limitations)
- [Supported Languages](#supported-languages)
- [Project Structure](#project-structure)
- [Local Deployment](#local-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Usage Workflow](#usage-workflow)
- [Example Output](#example-output)

## Overview

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/dockerfile-generator)
[![Language Support](https://img.shields.io/badge/languages-7-orange.svg)](#supported-languages)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

This project automatically generates Dockerfiles for simple programming projects using AI. It analyzes project structure and creates appropriate Docker configurations without requiring manual Dockerfile creation.

## Purpose

- Automate containerization for learning projects and simple applications
- Reduce setup time for developers working with multiple programming languages
- Generate consistent Docker configurations based on project analysis
- Support continuous integration workflows with automated Docker builds

## Limitations

**Important**: This tool is designed for simple projects and has several limitations:

- **Simple Projects Only**: Designed for basic learning projects and single-language applications. Complex enterprise applications are not supported.
- **No Hybrid Language Support**: Projects mixing multiple programming languages will not work correctly, unless you have a clear main entry point (e.g., Python project with main.py).
- **No Code Analysis**: The generator does not analyze your actual code logic or dependencies. It only examines file structure and common configuration files.
- **Manual Customization Required**: If your project requires special configurations, custom build steps, or non-standard setups, you must manually modify the generated Dockerfile.
- **Limited Dependency Detection**: Only detects standard dependency files (requirements.txt, package.json, Makefile, etc.). Custom build systems are not supported.
- **No Runtime Configuration**: Does not predict special runtime requirements, environment variables, or custom startup procedures.

## Supported Languages

- Python (with/without requirements.txt)
- JavaScript/Node.js (with/without package.json)
- TypeScript (with tsconfig.json)
- Java (basic projects)
- C/C++ (with/without Makefile)
- Go (basic projects)
- Rust (basic projects)

## Project Structure

```
├── inputs/          # Place your projects here for processing
├── outputs/         # Generated Dockerfiles and moved projects
├── main.py          # Project analysis engine
├── Ollama-code.py   # Dockerfile generation script
└── README.md
```

## Local Deployment

### Prerequisites

- Python 3.8+
- Ollama installed locally

### Installation Steps

1. **Install Ollama:**
   ```bash
   # Linux/Mac
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai
   ```

2. **Pull AI Model:**
   ```bash
   # Default model (recommended)
   ollama pull codegemma:7b
   
   # Alternative models (you can choose any):
   ollama pull codellama:7b
   ollama pull llama2:7b
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install ollama
   # Add any other dependencies from your requirements.txt
   ```

4. **Customize Model (Optional):**
   
   Edit Ollama-code.py and change the model name:
   ```python
   model = "codegemma:7b"  # Change to your preferred model
   ```

### How to Run

**Project Analysis Only:**
```bash
python main.py
```

**Expected Output:**
- Analyzes projects in inputs/ directory
- Moves projects to outputs/ directory
- Displays project structure analysis
- No Dockerfile generation

**Full Dockerfile Generation:**
```bash
python Ollama-code.py
```

**Expected Output:**
- Analyzes the first project in outputs/
- Generates Dockerfile using AI model
- Saves Dockerfile in the project directory
- Displays generated Dockerfile content

### Automated Processing (Cron Job)

```bash
# Edit crontab
crontab -e

# Add this line for processing every 5 minutes
*/5 * * * * cd /path/to/project && ./venv/bin/python Ollama-code.py >> /tmp/docker-gen.log 2>&1
```

## Cloud Deployment

### Overview

The cloud deployment extends the local functionality with a complete DevOps pipeline that includes automated Dockerfile generation, security analysis, Docker image building, and automated GitHub integration.

### Architecture

The cloud pipeline consists of several Google Cloud Platform services working together:

1. **Compute Engine**: Hosts the main application and Ollama AI model
2. **Vertex AI**: Provides advanced security analysis using Gemini 2.0 Flash
3. **Artifact Registry**: Stores built Docker images
4. **Cloud Scheduler**: Triggers automated pipeline execution
5. **Cloud Functions**: Handles webhook events and notifications
6. **Cloud Pub/Sub**: Manages message queuing between services

### How It Works

The automated pipeline follows this workflow:

1. **Project Detection**: When a new project is pushed to GitHub, a webhook triggers the pipeline
2. **AI Analysis**: Ollama CodeGemma analyzes the project structure and generates an optimized Dockerfile
3. **Security Scanning**: Vertex AI Gemini performs comprehensive security analysis of the generated Dockerfile
4. **Image Building**: Docker builds and tags the image automatically
5. **Registry Push**: The built image is pushed to Google Artifact Registry
6. **GitHub Integration**: Creates a pull request with the generated Dockerfile and security analysis
7. **Notification**: Sends completion status via configured channels

### Prerequisites

- Google Cloud Platform account with billing enabled
- GitHub repository access token
- Docker installed on Compute Engine instance
- Required IAM permissions for all services

### Step-by-Step Setup Guide

#### 1. Google Cloud Project Setup

```bash
# Create new project
gcloud projects create dockerfile-generator-project

# Set project
gcloud config set project dockerfile-generator-project

# Enable required APIs
gcloud services enable compute.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable pubsub.googleapis.com
```

#### 2. Artifact Registry Setup

```bash
# Create Docker repository
gcloud artifacts repositories create docker-images \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker images for automated builds"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

#### 3. Compute Engine Instance Setup

```bash
# Create compute instance
gcloud compute instances create dockerfile-generator \
    --zone=us-central1-a \
    --machine-type=e2-standard-4 \
    --boot-disk-size=50GB \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --scopes=cloud-platform

# SSH into instance
gcloud compute ssh dockerfile-generator --zone=us-central1-a
```

#### 4. Install Dependencies on Compute Engine

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Python dependencies
sudo apt install python3-pip git -y
pip3 install ollama requests google-cloud-aiplatform

# Install and setup Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull codegemma:7b

# Install Google Cloud SDK (if not present)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### 5. Deploy Application Code

```bash
# Clone your repository
git clone https://github.com/YahyaElkhayat/Python-Project-v2.git
cd Python-Project-v2

# Set up environment variables
export GOOGLE_CLOUD_PROJECT="dockerfile-generator-project"
export GITHUB_TOKEN="your_github_token_here"

# Make scripts executable
chmod +x *.py
```

#### 6. Service Account and IAM Setup

```bash
# Create service account
gcloud iam service-accounts create dockerfile-generator-sa \
    --description="Service account for Dockerfile generator" \
    --display-name="Dockerfile Generator SA"

# Grant necessary permissions
gcloud projects add-iam-policy-binding dockerfile-generator-project \
    --member="serviceAccount:dockerfile-generator-sa@dockerfile-generator-project.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding dockerfile-generator-project \
    --member="serviceAccount:dockerfile-generator-sa@dockerfile-generator-project.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding dockerfile-generator-project \
    --member="serviceAccount:dockerfile-generator-sa@dockerfile-generator-project.iam.gserviceaccount.com" \
    --role="roles/compute.instanceAdmin"

# Create and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=dockerfile-generator-sa@dockerfile-generator-project.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="key.json"
```

#### 7. Cloud Functions Setup (Optional - for webhook handling)

```bash
# Create Pub/Sub topic
gcloud pubsub topics create dockerfile-generation-trigger

# Deploy Cloud Function
gcloud functions deploy dockerfile-webhook \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --entry-point handle_webhook \
    --source ./cloud-functions \
    --set-env-vars PUBSUB_TOPIC=dockerfile-generation-trigger
```

#### 8. Cloud Scheduler Setup

```bash
# Create scheduled job to run pipeline daily
gcloud scheduler jobs create http dockerfile-daily-check \
    --schedule="0 2 * * *" \
    --uri="http://COMPUTE_ENGINE_EXTERNAL_IP:8080/trigger" \
    --http-method=POST \
    --description="Daily Dockerfile generation check"
```

#### 9. Testing the Pipeline

```bash
# Run manual test
python3 Ollama-code.py

# Check logs
tail -f /var/log/dockerfile-generator.log

# Verify Artifact Registry
gcloud artifacts docker images list --repository=docker-images --location=us-central1
```

### Configuration Files

#### Environment Variables
```bash
# Create .env file
cat << EOF > .env
GOOGLE_CLOUD_PROJECT=dockerfile-generator-project
GITHUB_TOKEN=your_github_token_here
ARTIFACT_REGISTRY_LOCATION=us-central1
ARTIFACT_REGISTRY_REPOSITORY=docker-images
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash-001
EOF
```

