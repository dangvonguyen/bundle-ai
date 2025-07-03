# Bundle AI

A full-stack application that provides a system of specialized AI agents through a modern web interface.

## Overview

Bundle AI is built with a React frontend and FastAPI backend, both containerized with Docker for easy development and deployment.

## Project Structure

- **frontend/** - React application built with:
  - TypeScript
  - React 19
  - Material UI
  - TailwindCSS
  - Vite

- **backend/** - FastAPI application using:
  - Python 3.12
  - FastAPI
  - LangChain
  - LangGraph
  - OpenAI integration
  - Pinecone vector database

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- [Node.js](https://nodejs.org/) (for frontend development)
- [Python 3.12+](https://www.python.org/) with [uv](https://docs.astral.sh/uv/) (for backend development)

### Environment Setup

1. Clone the repository
2. Set up environment variables:

```bash
# Create and configure backend environment variables
cp backend/.env.example backend/.env

# Create root environment file for Docker
touch .env
```

### Running with Docker

Start the entire application stack:

```bash
docker compose up
```

For development with hot reloading:

```bash
docker compose watch
```
