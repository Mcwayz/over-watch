# Project Configuration Files

## Python Code Style (.flake8)

Create `.flake8`:

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    .venv,
    venv,
    node_modules,
    migrations
per-file-ignores =
    __init__.py:F401
    tests/*:F401
```

## Python Formatting (setup.cfg)

Create `setup.cfg`:

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = over_watch.settings
python_files = tests.py test_*.py *_tests.py
testpaths = tests

[isort]
profile = django
multi_line_mode = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensemble_line_length = 100
skip_glob = */migrations/*

[black]
line-length = 100
target-version = ['py39', 'py310', 'py311']
exclude = '/(\.git|\.hg|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist|migrations)/'
```

## Python Type Checking (pyproject.toml)

Create `pyproject.toml`:

```toml
[tool.poetry]
name = "courier-management-system"
version = "1.0.0"
description = "Production-ready Courier Management System"
authors = ["Your Name <your@email.com>"]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.mypy]
python_version = "3.11"
django_db_module = "django.db"
check_untyped_defs = true
no_implicit_optional = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
disallow_untyped_defs = false
plugins = ["mypy_django_plugin.main"]

[tool.django-stubs]
django_settings_module = "over_watch.settings"

[tool.coverage.run]
source = ["."]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "manage.py",
    "venv/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
    "if __name__ == .__main__.:"
]
```

## Pre-commit Hooks (.pre-commit-config.yaml)

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        additional_dependencies: [flake8-django]
        args: ['--config=.flake8']

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--settings-path=setup.cfg']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: ['djangorestframework-stubs', 'django-stubs']
        args: [--config-file=pyproject.toml]
```

## EditorConfig (.editorconfig)

Create `.editorconfig`:

```ini
# EditorConfig helps maintain consistent coding styles across different editors
root = true

# All files
[*]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

# Python files
[*.py]
indent_size = 4
max_line_length = 100

# YAML files
[*.{yml,yaml}]
indent_size = 2

# Markdown files
[*.md]
trim_trailing_whitespace = false

# JSON files
[*.json]
indent_size = 2
```

## Git Ignore (.gitignore)

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
*.log

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Django
*.sqlite3
media/
staticfiles/
local_settings.py
.env
.env.local

# Testing
.coverage
.pytest_cache/
htmlcov/
.tox/

# Node
frontend/node_modules/
frontend/build/
frontend/dist/

# Docker
docker-compose.override.yml

# Celery
celerybeat-schedule

# IDE specific
*.sublime-project
*.sublime-workspace

# OS
Thumbs.db
.DS_Store

# Backup files
*.bak
*.backup
*~

# System files
.directory
```

## GitHub Actions CI/CD

Create `.github/workflows/python-tests.yml`:

```yaml
name: Python Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: courier_test
          POSTGRES_USER: courier
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt coverage
    
    - name: Run migrations
      env:
        DATABASE_URL: postgres://courier:postgres@localhost:5432/courier_test
      run: python manage.py migrate
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://courier:postgres@localhost:5432/courier_test
      run: |
        coverage run --source='.' manage.py test
        coverage report --fail-under=80
```

Create `.github/workflows/frontend-tests.yml`:

```yaml
name: Frontend Tests

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node
      uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run tests
      working-directory: ./frontend
      run: npm test -- --coverage --watchAll=false
    
    - name: Build
      working-directory: ./frontend
      run: npm run build
```

## Docker Ignore (.dockerignore)

Create `.dockerignore`:

```
.git
.gitignore
.dockerignore
*.log
venv/
.venv/
node_modules/
.pytest_cache/
.coverage
htmlcov/
.env
.env.local
.DS_Store
__pycache__/
*.pyc
*.pyo
*.pyd
.tox/
.mypy_cache/
.hypothesis/
.env.example
TODO.md
NOTES.md
```

## Makefile for Common Tasks

Create `Makefile`:

```makefile
.PHONY: help install setup migrate test lint format clean run docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make setup            - Setup development environment"
	@echo "  make migrate          - Run database migrations"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Run linting"
	@echo "  make format           - Format code"
	@echo "  make clean            - Clean up temporary files"
	@echo "  make run              - Run development server"
	@echo "  make docker-up        - Start Docker containers"
	@echo "  make docker-down      - Stop Docker containers"

install:
	pip install -r requirements.txt
	cd frontend && npm install

setup: install
	python manage.py migrate
	python manage.py createsuperuser

migrate:
	python manage.py makemigrations
	python manage.py migrate

test:
	python manage.py test
	cd frontend && npm test

lint:
	flake8 .
	black --check .
	isort --check-only .

format:
	black .
	isort .

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	find . -type d -name '.coverage' -delete
	rm -rf htmlcov/
	rm -rf dist/ build/ *.egg-info/

run:
	python manage.py runserver

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
```

## VS Code Workspace Settings (.vscode/settings.json)

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "python.linting.flake8Args": ["--max-line-length=100"],
  "editor.defaultFormatter": "ms-python.python",
  "editor.formatOnSave": true,
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/*.pyc": true
  },
  "search.exclude": {
    "venv": true,
    "node_modules": true,
    ".git": true
  },
  "python.analysis.extraPaths": ["${workspaceFolder}"],
  "python.analysis.typeCheckingMode": "basic"
}
```

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.isort",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.extension-pack-for-java",
    "ms-vscode.rest-client",
    "GitHub.copilot"
  ]
}
```

## Environment Variables Template (.env.example)

Already created, but here's the complete list:

**Backend (.env.example)**:
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=courier_db
DB_USER=courier
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=24
JWT_REFRESH_TOKEN_LIFETIME=7

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# AWS S3 (Optional)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/courier/django.log
```

**Frontend (.env.example)**:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```
