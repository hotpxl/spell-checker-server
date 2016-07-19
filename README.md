# Spell Checker Server

API providing spell checker service.

## Build

[Git LFS](https://git-lfs.github.com/) is used to store binary files.

Run `git lfs pull` to download the files needed.

Run the following command to build the Docker image.

```bash
docker build -t spell-checker-server .
```

## Run

```bash
docker run -d -p 8082:80 --log-opt max-file=8 --log-opt max-size=8m --name spell-checker-server spell-checker-server
```

This will open an HTTP server on port 8082. Try the following for a demonstration.

```bash
curl -H "Content-Type: application/json" -X POST -d '{"word": "helllo"}' localhost:8082/spell-check
```
