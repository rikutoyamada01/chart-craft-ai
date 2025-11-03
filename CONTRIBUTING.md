# Contributing to Circuit Craft AI

We welcome contributions to Cuircuit Craft AI! By following these guidelines, you can help us maintain a high-quality codebase and a smooth development process.

## Table of Contents

1.  [Getting Started](#1-getting-started)
2.  [Code Style and Formatting](#2-code-style-and-formatting)
3.  [Running Tests](#3-running-tests)
4.  [Commit Messages](#4-commit-messages)
5.  [Submitting Changes (Pull Requests)](#5-submitting-changes-pull-requests)
6.  [Reporting Bugs](#6-reporting-bugs)
7.  [Suggesting Enhancements](#7-suggesting-enhancements)

## 1. Getting Started

To set up your development environment and get the project running, please refer to the comprehensive [development documentation](development.md).

For a quick start, you can typically bring up the entire local stack using Docker Compose:

```bash
docker compose watch
```

This command will start the frontend, backend, database, and other services. Once started, you can access:

*   **Frontend:** `http://localhost:5173`
*   **Backend API:** `http://localhost:8000`
*   **Swagger UI (API Docs):** `http://localhost:8000/docs`

For more details on local development, stopping/starting individual services, and advanced configurations, please see `development.md`.

## 2. Code Style and Formatting

We use linters and formatters to ensure consistent code style across the project. Please ensure your code adheres to these standards.

*   **Backend (Python):**
    *   Linter: Ruff
    *   Formatter: Black
*   **Frontend (TypeScript/React):**
    *   Linter/Formatter: Biome

We use [pre-commit](https://pre-commit.com/) hooks to automatically check and format code before each commit.

### Installing Pre-commit Hooks

To install the pre-commit hooks in your local repository, run:

```bash
uv run pre-commit install
```

This will ensure that checks run automatically before each commit. If any issues are found, you'll be prompted to fix them and re-stage the files.

### Running Pre-commit Hooks Manually

You can also run all pre-commit hooks manually on all files at any time:

```bash
uv run pre-commit run --all-files
```

Please ensure all checks pass before submitting your changes.

## 3. Running Tests

Tests are crucial for maintaining code quality and preventing regressions. Please ensure all tests pass before submitting your changes.

### Backend Tests

To run the backend tests and generate a coverage report, navigate to the `backend` directory and execute:

```bash
./scripts/test.sh
```

This command uses `pytest` for testing and `coverage.py` for reporting.

### Frontend Tests

Frontend tests are written using Playwright. To run them, navigate to the `frontend` directory and execute:

```bash
npx playwright test
```

(The exact command for frontend tests will be confirmed from `frontend/package.json`.)

## 4. Commit Messages

Please follow a consistent commit message convention. We recommend using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

Examples:
*   `feat: Add new user authentication feature`
*   `fix: Correct typo in login form`
*   `docs: Update README with installation instructions`
*   `refactor: Restructure API routes`

## 5. Submitting Changes (Pull Requests)

1.  Fork the repository and create your branch from `main`.
2.  Ensure your code adheres to the style guidelines and passes all tests.
3.  Write clear, concise commit messages.
4.  Open a Pull Request (PR) to the `main` branch.
5.  Provide a clear description of your changes in the PR.

## 6. Reporting Bugs

If you find a bug, please open an issue using the provided bug report template.

## 7. Suggesting Enhancements

For feature requests or suggestions, please open an issue using the provided feature request template.
