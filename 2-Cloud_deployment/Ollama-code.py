import ollama
import os
from main import main
import requests
import subprocess
import base64
import subprocess
import base64
import sys

def get_fresh_token():
    result = subprocess.run(['gcloud', 'auth', 'print-access-token'], 
                          capture_output=True, text=True)
    return result.stdout.strip()

def analyse_dockerfile_with_vertexai(output_file, dockerfile_content):
    try:
        access_token = get_fresh_token()
        
        endpoint = "https://us-central1-aiplatform.googleapis.com/v1/projects/your-gcp-project/locations/us-central1/publishers/google/models/gemini-2.0-flash-001:generateContent"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""Analyze this Dockerfile for:
        1. Security vulnerabilities
        2. Best practices violations  
        3. Image size optimizations
        4. Specific recommendations
        Response directly without starting to analyze in the response    
        Provide explanation for each suggestion.
        Dockerfile content: {dockerfile_content}
        """
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 1024,
                "temperature": 0.2,
                "topP": 0.8,
                "topK": 40
            }
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raises exception for bad status codes
        
        analysis_result = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        print("\nDockerfile Analysis with Vertex AI Gemini 1.5 Pro:")
        print("=" * 50)
        print(analysis_result)
        print("=" * 50)
        
        # Save analysis to a file
        analysis_file = os.path.join(os.path.dirname(output_file), "Dockerfile_Analysis.txt")
        with open(analysis_file, "w") as f:
            f.write("Dockerfile Analysis with Vertex AI Gemini 2.0 Flash\n")
            f.write("=" * 50 + "\n\n")
            f.write(analysis_result)
        
        print(f"\nDockerfile analysis has been saved to '{analysis_file}'")
        
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        return

def build_and_push_to_artifact_registry(project_dir, project_name):
    """
    Build and push Docker image to Google Artifact Registry
    """
    project_name = project_name.lower()
    project_id = "xxxxxxxxxxxxx" # Change it to your GCP project ID
    region = "us-central1"  # or your preferred region
    repository_name = "docker-images"  # name of the repo to store docker images
    docker_image_name = f'{project_name}_image'
    
    # Artifact Registry URL format
    ar_image = f'{region}-docker.pkg.dev/{project_id}/{repository_name}/{docker_image_name}:latest'

    try:
        print("Configuring Docker authentication for Artifact Registry...")
        # Configure Docker to use gcloud as credential helper
        auth_cmd = ['sudo','gcloud', 'auth', 'configure-docker', f'{region}-docker.pkg.dev', '--quiet']
        result = subprocess.run(auth_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Authentication configuration failed: {result.stderr}")
            return False

        print("Building the Docker image...")
        build_cmd = ['sudo', 'docker', 'build', '-t', docker_image_name, '.']
        result = subprocess.run(build_cmd, cwd=project_dir, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Build failed: {result.stderr}")
            return False
        
        print("Build successful. Tagging the image for Artifact Registry...")
        tag_cmd = ['sudo', 'docker', 'tag', docker_image_name, ar_image]
        result = subprocess.run(tag_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Tagging failed: {result.stderr}")
            return False

        print("Pushing the image to Artifact Registry...")
        push_cmd = ['sudo', 'docker', 'push', ar_image]
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Push failed: {result.stderr}")
            print("1. Make sure you have the required IAM permissions:")
            return False

        print(f" The image has been successfully pushed to Artifact Registry:")
        print(f"   {ar_image}")
        return True
        
    except Exception as e:
        print(f"Error in build_and_push_to_artifact_registry: {e}")
        return False


def create_artifact_registry_repository(project_id, region, repository_name):
    """
    Create an Artifact Registry repository if it doesn't exist
    """
    try:
        print(f"Creating Artifact Registry repository: {repository_name}")
        create_cmd = [
            'gcloud', 'artifacts', 'repositories', 'create', repository_name,
            '--repository-format=docker',
            f'--location={region}',
            f'--project={project_id}',
            '--description=Docker images for automated builds'
        ]
        
        result = subprocess.run(create_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Repository '{repository_name}' created successfully")
            return True
        elif "already exists" in result.stderr:
            print(f"Repository '{repository_name}' already exists")
            return True
        else:
            print(f"Failed to create repository: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating repository: {e}")
        return False

def push_code_back_to_github(project_name, project_dir):
    GITHUB_TOKEN = "xxxxxxxxxxxxxxxxxxxx" # Get the credentials from github
    repo_name = "xxxxxxxxxxxxx" # Change it to the project you want to push back to github
    GITHUB_USERNAME = "xxxxxxxxxxxxxx" # Your github username
    branch_name = f"add-dockerfile-{project_name.lower()}"
    base_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    try:
        # Step 1: Get main branch SHA
        print("Getting main branch SHA...")
        main_ref_response = requests.get(f"{base_url}/git/refs/heads/main", headers=headers)
        if main_ref_response.status_code != 200:
            print(f"Failed to get main branch: {main_ref_response.json()}")
            return False
        
        main_branch_sha = main_ref_response.json()["object"]["sha"]
        print(f"Main branch SHA: {main_branch_sha}")

        # Step 2: Create new branch
        print(f"Creating branch '{branch_name}'...")
        create_branch_payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": main_branch_sha
        }
        
        branch_response = requests.post(f"{base_url}/git/refs", json=create_branch_payload, headers=headers)
        if branch_response.status_code == 201:
            print(f"Branch '{branch_name}' created successfully.")
        elif branch_response.status_code == 422:
            print(f"Branch '{branch_name}' already exists.")
        else:
            print(f" Failed to create branch: {branch_response.json()}")
            return False

        # Step 3: Push Dockerfile
        print("Uploading Dockerfile...")
        dockerfile_path = os.path.join(project_dir, "Dockerfile")
        
        if not os.path.exists(dockerfile_path):
            print(f" Dockerfile not found at {dockerfile_path}")
            return False
            
        with open(dockerfile_path, "r") as file:
            dockerfile_content = file.read()
        
        dockerfile_base64 = base64.b64encode(dockerfile_content.encode()).decode()
        
        dockerfile_payload = {
            "message": f"Add auto-generated Dockerfile for {project_name}",
            "content": dockerfile_base64,
            "branch": branch_name
        }
        
        dockerfile_response = requests.put(f"{base_url}/contents/Dockerfile", 
                                         json=dockerfile_payload, headers=headers)
        
        if dockerfile_response.status_code in [200, 201]:
            print(" Dockerfile uploaded successfully.")
        else:
            print(f" Failed to upload Dockerfile: {dockerfile_response.json()}")
            return False

        # Step 4: Push Dockerfile Analysis
        print("Uploading Dockerfile Analysis...")
        analysis_path = os.path.join(project_dir, "Dockerfile_Analysis.txt")
        
        print(f"Looking for analysis file at: {analysis_path}")
        print(f"File exists: {os.path.exists(analysis_path)}")
        
        if not os.path.exists(analysis_path):
            print(f" Analysis file not found at {analysis_path}")
            # Try alternative path - current directory
            alt_analysis_path = os.path.join(os.getcwd(), "Dockerfile_Analysis.txt")
            print(f"Trying alternative path: {alt_analysis_path}")
            if os.path.exists(alt_analysis_path):
                analysis_path = alt_analysis_path
                print(" Found analysis file in current directory")
            else:
                print(" Skipping analysis file upload...")
                analysis_path = None
        
        if analysis_path:
            with open(analysis_path, "r") as file:
                analysis_content = file.read()
            
            analysis_base64 = base64.b64encode(analysis_content.encode()).decode()
            
            # Check if analysis file already exists to get its SHA
            existing_analysis_response = requests.get(f"{base_url}/contents/Dockerfile_Analysis.txt?ref={branch_name}", headers=headers)
            
            analysis_payload = {
                "message": f"Add Dockerfile analysis for {project_name}",
                "content": analysis_base64,
                "branch": branch_name
            }
            
            # If file exists, add its SHA to the payload
            if existing_analysis_response.status_code == 200:
                analysis_payload["sha"] = existing_analysis_response.json()["sha"]
                print("Updating existing analysis file...")
            else:
                print("Creating new analysis file...")
            
            analysis_response = requests.put(f"{base_url}/contents/Dockerfile_Analysis.txt", 
                                           json=analysis_payload, headers=headers)
            
            if analysis_response.status_code in [200, 201]:
                print("Dockerfile Analysis uploaded successfully.")
            else:
                print(f"Failed to upload Analysis: {analysis_response.json()}")

        # Step 5: Create Pull Request
        print("Creating Pull Request...")
        pr_payload = {
            "title": f" Auto-generated Dockerfile for {project_name}",
            "head": branch_name,
            "base": "main",  # Use detected default branch
            "body": f"""##  Auto-generated Dockerfile

This PR was automatically created by the DevOps pipeline for project: **{project_name}**

### What's included:
- Dockerfile - Generated using Ollama CodeGemma
- Dockerfile_Analysis.txt - Security & optimization analysis by Vertex AI
- Docker Image - Built and pushed to Google Artifact Registry

### Pipeline Steps:
1. Project detection and analysis
2. Dockerfile generation with AI
3. Security analysis with Vertex AI Gemini
4. Docker build and push to Artifact Registry
5. Automated PR creation

Ready for review! """
        }
        
        pr_response = requests.post(f"{base_url}/pulls", json=pr_payload, headers=headers)
        
        if pr_response.status_code == 201:
            pr_url = pr_response.json()["html_url"]
            print(f"Pull request created successfully!")
            print(f" PR URL: {pr_url}")
            return True
        else:
            print(f"Failed to create pull request: {pr_response.json()}")
            return False
            
    except Exception as e:
        print(f" Error in GitHub push: {e}")
        return False
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
model = "codegemma:7b" # Change the model if you want to use another one

# The prompt(You can modify it based on your needs)
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
    
    # Analyze the generated Dockerfile with Vertex AI
    analyse_dockerfile_with_vertexai(output_file, dockerfile_content)
    # Create repository for storing images inside artifct registry
    create_artifact_registry_repository("total-treat-466514-k4", "us-central1", "docker-images")

    # Build and push to GAR
    build_and_push_to_artifact_registry(project_dir, project_name)
    #Push the code to Github as Pull Request
    push_code_back_to_github(project_name,project_dir)
except Exception as e:
    print(f"An error occurred: {str(e)}")
