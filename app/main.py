from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="DevOps Pipeline for FastAPI",
    description=(
        "Small FastAPI service used to demonstrate Docker, CI, SonarQube, "
        "and blue-green deployment."
    ),
    version="1.0.0",
)


class Message(BaseModel):
    message: str = Field(..., min_length=1, max_length=200)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "FastAPI CI/CD project is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/greet")
def greet(name: Annotated[str, Query(min_length=1, max_length=50)] = "DevOps") -> dict[str, str]:
    return {"message": f"Hello, {name}!"}


@app.post("/echo")
def echo(payload: Message) -> Message:
    return payload
