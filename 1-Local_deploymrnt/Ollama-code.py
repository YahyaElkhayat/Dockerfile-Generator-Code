import ollama
from main import main

# Analyze projects
analyses = main()
first_project = analyses[0]

# Generate Dockerfile
prompt = f"Generate a Dockerfile for {first_project['description']}"
res = ollama.generate(model="DockerGenerator", prompt=prompt)
print(res["response"])