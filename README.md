# FastAPI CI/CD Pipeline with Docker and SonarQube

This project is a small FastAPI service prepared for a DevOps exam assignment. It includes a production-style Dockerfile, automated tests, SonarQube analysis, and a GitHub Actions pipeline with lint, test, build, scan, and deploy stages.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

The app exposes:

- `GET /` - basic application response
- `GET /health` - health endpoint for Docker and deployment checks
- `GET /greet?name=DevOps` - sample query endpoint
- `POST /echo` - sample JSON endpoint

## Test and Lint

```powershell
ruff check .
coverage run -m pytest
coverage xml
coverage report
```

## Docker

Build and run:

```powershell
docker build -t fastapi-devops-pipeline:latest .
docker run --rm -p 8000:8000 fastapi-devops-pipeline:latest
```

The Dockerfile uses a builder stage for dependency installation and a runtime stage with only the virtual environment plus application code. The runtime container uses a non-root user and a `/health`-based Docker health check.

## SonarQube

`sonar-project.properties` points SonarQube to:

- source code in `app`
- tests in `tests`
- coverage report at `coverage.xml`
- Python version `3.11`

The CI pipeline expects these GitHub secrets:

- `SONAR_HOST_URL`
- `SONAR_TOKEN`

The quality gate is mandatory. If SonarQube reports a failed gate, the `sonar` job fails and the `deploy` job is blocked because it depends on `sonar`.

## CI/CD Pipeline

The GitHub Actions workflow in `.github/workflows/ci-cd.yml` runs this flow:

1. `lint`: installs development dependencies and runs Ruff.
2. `test`: runs pytest with coverage and uploads `coverage.xml`.
3. `build`: builds the Docker image and pushes it to GitHub Container Registry on pushes to `main`.
4. `sonar`: runs SonarQube scan and enforces the quality gate.
5. `deploy`: deploys only after both Docker build and SonarQube quality gate pass.

## Blue-Green Deployment

The local blue-green setup uses Docker Compose profiles:

- blue environment: `app-blue` on host port `8001`
- green environment: `app-green` on host port `8002`

Deploy the inactive environment:

```powershell
docker build -t fastapi-devops-pipeline:latest .
.\scripts\blue_green_deploy.ps1 -Image fastapi-devops-pipeline:latest -Target green
```

After the target environment passes `/health`, traffic can be switched to that environment. If the new environment fails health checks, the script exits with failure and the previous environment keeps running, which provides rollback capability.
