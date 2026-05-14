# Questions to Answer

## 1. Why are multi-stage builds used in the Dockerfile, and how do they improve image size and security?

Multi-stage builds are used to separate the image build process into different stages with different responsibilities. In this project, the builder stage prepares the Python virtual environment and installs dependencies, while the final runtime stage only contains what is required to run the FastAPI application.

This improves image size because temporary build files, package manager caches, compiler tools, and other build-time artifacts do not need to be copied into the final image. The runtime image only keeps the application source code and installed runtime dependencies, so the final image is smaller, faster to pull, and easier to deploy.

It also improves security by reducing the attack surface of the container. A smaller runtime image contains fewer tools, fewer files, and fewer unnecessary packages that an attacker could abuse. In addition, the Dockerfile runs the application as a non-root user, which limits the impact if the application or container is compromised. The health check also helps the platform detect unhealthy containers automatically.

In short, multi-stage builds make the final Docker image smaller, cleaner, and safer by keeping build-time concerns separate from runtime execution.

## 2. Describe the complete CI/CD pipeline flow from a developer pushing code to production deployment.

The CI/CD pipeline starts when a developer pushes code to the repository or opens a pull request. The pipeline automatically checks out the latest source code and runs a sequence of validation, build, analysis, and deployment stages.

First, the lint stage runs static checks using Ruff. This stage detects formatting issues, unused imports, simple bugs, and style violations before the code moves further in the pipeline. If linting fails, the pipeline stops early because the code does not meet the required quality standard.

Next, the test stage installs the application and development dependencies, then runs the pytest unit tests with coverage collection. The generated coverage report is exported as `coverage.xml` so it can be used by SonarQube during code analysis. If any test fails, the Docker image is not built and no deployment can happen.

After the tests pass, the build stage creates a Docker image using the multi-stage Dockerfile. On pushes to the main branch, the image is tagged with the commit SHA and also as `latest`, then pushed to the container registry. Tagging with the commit SHA is important because it allows each deployment to be traced back to the exact source code version.

In parallel with or after testing, the SonarQube scan stage analyzes the source code, tests, and coverage report. SonarQube checks for bugs, vulnerabilities, code smells, duplicated code, maintainability issues, and insufficient test coverage. The pipeline then waits for the SonarQube quality gate result.

Finally, the deploy stage runs only if both the Docker build and SonarQube quality gate pass. The deployment uses a blue-green style strategy: a new version is started in the inactive environment, its `/health` endpoint is verified, and only after the new environment is healthy should traffic be switched to it. If the new version fails health checks, traffic remains on the old environment, which provides rollback capability and avoids downtime.

The complete flow is:

```text
Developer push / pull request
        -> lint
        -> test with coverage
        -> Docker build and image push
        -> SonarQube scan and quality gate
        -> blue-green deployment
        -> health check verification
        -> traffic switch
```

## 3. How does the SonarQube quality gate integrate with the pipeline, and what happens when the gate fails?

The SonarQube quality gate is integrated as a mandatory stage in the CI/CD pipeline. After the test stage produces the coverage report, the SonarQube scan reads the project configuration from `sonar-project.properties`, analyzes the application source code, includes test coverage data from `coverage.xml`, and sends the analysis results to the SonarQube server.

The quality gate is a set of pass/fail rules that define whether the code is acceptable for release. Common quality gate conditions include minimum code coverage, no critical bugs, no critical vulnerabilities, acceptable maintainability rating, limited duplicated code, and no serious code smells. These rules are evaluated by SonarQube after the scan finishes.

In the pipeline, the quality gate is not only informational. It is enforced as a blocking condition before deployment. The deploy job depends on the SonarQube job, so deployment can start only when the SonarQube scan succeeds and the quality gate status is passed.

If the quality gate fails, the SonarQube job exits with an error and the CI/CD pipeline is marked as failed. Because the deployment stage depends on that job, deployment is automatically blocked. The Docker image may have been built, but it must not be promoted to production because the code did not satisfy the required quality, reliability, or security standards.

When the quality gate fails, the correct action is to inspect the SonarQube report, fix the reported issues, add or improve tests if coverage is too low, commit the fixes, and run the pipeline again. Only after the quality gate passes should the application be deployed.
