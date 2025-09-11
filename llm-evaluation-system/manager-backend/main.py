import os
import random
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import docker

app = FastAPI()

# Image name to launch
AUTOMATED_RT_IMAGE = os.environ.get('AUTOMATED_RT_IMAGE', 'automated-rt-app:latest')
# Initialize Docker client
# Connect to Docker socket
docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
HOST = os.environ.get('HOST', 'localhost')
PORT = "18001"

def find_existing_container():
    for c in docker_client.containers.list():
        # Get PortBindings, use empty dict if None
        port_bindings = c.attrs['HostConfig'].get('PortBindings') or {}
        # Check if 8000/tcp is bound to HostPort=18001
        if "8000/tcp" in port_bindings:
            host_port = port_bindings["8000/tcp"][0]['HostPort']
            if host_port == PORT:
                return c
    return None

@app.post("/llm-eval-launch")
def launch():    container = find_existing_container()
    print(container)    url = f"http://{HOST}:{PORT}"
    if container:
        # If a container is already running on port 18001, return its URL
        return {"url": url}
    # Otherwise, run a new container
    try:
        container = docker_client.containers.run(
            image=AUTOMATED_RT_IMAGE,
            detach=True,
            ports={'8000/tcp': PORT},
            remove=True,
            name=f"llm-eval-{PORT}",  # Name also linked to port (optional)
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch: {e}")


# Enable CORS (modify as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify here if you need to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

