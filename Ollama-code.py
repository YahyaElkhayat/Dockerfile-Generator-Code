import ollama
from main import main

# Analyze projects
analyses = main()
first_project = analyses[0]

# Save the modelfile to disk
modelfile = """
FROM codegemma7
SYSTEM You are a senior DevOps engineer who creates Dockerfiles. 
When a user asks you to create a Dockerfile for a specific project, 
you will use the latest stable version for Docker base images.

Here is a list of the latest stable Docker base image versions:
- python:3.12 for Python
- node:20 for Node.js  
- node:20-slim for TypeScript
- openjdk:21 for Java
- golang:1.23 for Go
- rust:1.81 for Rust
- gcc:14 for C
- gcc:14 for C++
- ubuntu:24.04 for Bash/Shell
- php:8.3 for PHP
- ruby:3.3 for Ruby
- dotnet:8.0 for C#/.NET

PARAMETER temperature 0.3
"""

with open("Modelfile", "w") as f:
    f.write(modelfile)

# Create the model
ollama.create(model="knowitall", modelfile="Modelfile")

# Generate Dockerfile
prompt = f"Generate a Dockerfile for {first_project['description']}"
res = ollama.generate(model="knowitall", prompt=prompt)

print(res["response"])
