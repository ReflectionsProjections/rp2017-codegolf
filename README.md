# Code Golf
Competition to write the shortest and fastest programs to solve problems in a variety of languages, including Javascript, Python, C++, and Java. Built on Flask (Python 3.6) and uses SQLAlchemy and Docker

## Setup
Clone repository with 
```git clone https://github.com/ReflectionsProjections/rp2017-codegolf```

### Python
Navigate to main directory and install dependencies with
```pip3 install -r requirements.txt```

### Docker
Install and set up Docker for your system [link](https://docs.docker.com/engine/installation/#supported-platforms)

- Add Docker to path variables, if not performed automatically by installer
- Test Docker install with `docker run hello-world`
	- If an error message appears, ensure that virtualization is enabled
	- Ensure that Docker host is properly configured with `docker-machine ls`
		- There should be at least one host, called "default"
		- Export environment variables with `eval "$(docker-machine env default)"
	- For Windows, HyperV must be enabled
	- If errors persist, run Docker as a VirtualBox image and try the above steps again
- Get list of current Docker images with `docker images`
	- Download the following images from Docker Hub if not already present: `node:boron`, `python`
	- Other images can be downloaded with: `docker pull`
- Run containers from images
	- Initialize a container with: `docker run -id python bash`. It will print a container ID to stdout
	- Get all running containers with: `docker ps`. The recently created Python container should appear
	- Kill the container with: `docker kill [id]`
	- This should not be necessary, since the server will automatically start and kill docker containers



## Running
Deploy using Python
```python3 app.py```

Open using web browser on 0.0.0.0:21337

__README IS STILL A WIP__
