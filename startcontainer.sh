docker build -t arena .

mkdir mount
docker run -v ${PWD}/mount:/arenalog --rm arena
