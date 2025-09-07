import ollama
import os
from main import main

# Analyze projects
analyses = main()

# Check if any projects were found
if not analyses or len(analyses) == 0:
    print("No projects found in the directory.")
    print("Please make sure there are project directories to analyze.")
    exit(1)

first_project = analyses[0]

# Extract project name from the description
# The description format is: "The project 'project-name':"
description = first_project['description']
project_name = description.split("'")[1]  # Extract name between single quotes

# Model configuration
model = "codegemma:7b"

# Create the simplified prompt
prompt = f"""You are a senior DevOps engineer. Create a Dockerfile based on the project description.

RULES:
1. Use WORKDIR /app
2. Use COPY . . no matter what the description says,always use this command 
3. Read the project description carefully - if it says "without dependencies" then NO dependency installation,if there is no dependencies,do not add them inside the dockerfile
4. If it says "HAS MAKEFILE" use RUN make, then CMD ["./executable_name"]
5. If no Makefile, use appropriate language commands ( for js and typecript use  ["npm","start"] and so on for other languages), Do NOT USE run make if there is no Makefile
6. Use these latest stable Docker base images:
   - python:3.12 for Python
   - node:20 for Node.js/JavaScript
   - node:20-slim for TypeScript
   - openjdk:21 for Java
   - golang:1.23 for Go
   - rust:latest for Rust
   - gcc:14 for C
   - gcc:14 for C++
   - php:8.3 for PHP
   - ruby:3.3 for Ruby
   - dotnet:8.0 for C#/.NET

PROJECT DESCRIPTION:
{first_project['description']}

Generate only the Dockerfile content, no explanations."""

# Save Dockerfile inside the specific project directory
project_dir = os.path.join("outputs", project_name)
output_file = os.path.join(project_dir, "Dockerfile")

# Ensure the project directory exists
os.makedirs(project_dir, exist_ok=True)

# Send the prompt and get the response
try:
    print(f"Generating Dockerfile for: {project_name}")
    print(f"Saving to: {output_file}")
    print("=" * 60)
    
    response = ollama.generate(
        model=model, 
        prompt=prompt,
        options={
            "temperature": 0.3,
            "top_p": 0.9,
            "top_k": 40
        }
    )
    
    generated_text = response.get("response", "")
    
    # Clean up the response
    dockerfile_content = generated_text.strip()
    
    # Remove markdown code block markers
    if dockerfile_content.startswith("```dockerfile"):
        dockerfile_content = dockerfile_content[len("```dockerfile"):].strip()
    elif dockerfile_content.startswith("```"):
        dockerfile_content = dockerfile_content[3:].strip()
    
    if dockerfile_content.endswith("```"):
        dockerfile_content = dockerfile_content[:-3].strip()
    
    print("Generated Dockerfile:")
    print("=" * 30)
    print(dockerfile_content)
    print("=" * 30)

    # Write the Dockerfile to the output file
    with open(output_file, "w") as f:
        f.write(dockerfile_content)

    print(f"\nDockerfile has been saved to '{output_file}'")
    
except Exception as e:
    print(f"An error occurred: {str(e)}")