docker build -t vizro-dashboard . --no-cache
docker build -t core-server -f "CoreDockerfile" . --no-cache