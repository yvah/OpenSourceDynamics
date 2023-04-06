# Create an account on dockerHub
# Build docker image
docker build -t <dockerHubUsername>/SwEng-app .

# Run docker image
# docker run -it <dockerHubUsername>/SwEng-app

# Push docker image to dockerHub
docker login -u <dockerHubUsername> -p <dockerHubPassword>

docker push <dockerHubUsername>/SwEng-app
