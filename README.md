# Automated Dockerfile Generator

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

## Usage Workflow

1. **Add Projects**: Place your programming projects in the inputs/ directory
2. **Run Analysis**: Execute `python main.py` to analyze project structure
3. **Generate Dockerfiles**: Execute `python Ollama-code.py` to create Dockerfiles
4. **Review Results**: Check outputs/PROJECT_NAME/Dockerfile for generated configurations
5. **Test Containers**: Build and run your Docker containers:
   ```bash
   cd outputs/PROJECT_NAME
   docker build -t my-project .
   docker run my-project
   ```

## Example Output

**Input Project Structure:**
```
inputs/my-python-app/
├── main.py
├── requirements.txt
└── utils.py
```

**Generated Analysis:**
```
my-python-app: Python project with requirements.txt
- Language: PYTHON
- Files: main.py, utils.py
- Dependencies: with requirements.txt
- Interactive: non-interactive
```

**Generated Dockerfile:**
```dockerfile
FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]
```
