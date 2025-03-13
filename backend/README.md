# Bundle AI - Backend

## Requirements

- [Docker](https://www.docker.com/) for containerizing applications and managing environments.
- [uv](https://docs.astral.sh/uv/) for managing Python packages and environments.

## Setup

1. From `./backend/`, install all the dependencies with:

```bash
$ uv sync
```

2. Activate the virtual environment with:

```bash
$ source .venv/bin/activate
```

3. Create `.env` file and add necessary environment variables.

```bash
$ cp .env.example .env
```

## Development

1. **Start the development server:**

```bash
$ uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or develop with `Docker`

```bash
$ docker compose watch
```

2. Access the API documentation at `http://localhost:8000/docs`.