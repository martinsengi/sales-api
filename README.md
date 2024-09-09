# Sales API Project

![Python Version](https://img.shields.io/badge/python-3.11-blue)

## Overview

The project is currently set up for **development** only.  
Production features such as Gunicorn, secure HTTPS configuration, environment variable separation, image generation, autodeployment are not included.  

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Build & Start the services

```bash
docker compose up --build
```

### Step 3: Create a Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Step 4: Access links
API: `http://localhost:8000/api/`  
Admin Panel: `http://localhost:8000/admin/`  
Swagger Documentation: `http://localhost:8000/api/docs/`  


## Running Tests

### To run the test suite, use:

```bash
docker compose exec web python manage.py test
```

### To check test coverage:

```bash
docker compose exec web coverage run --source='.' manage.py test
docker compose exec web coverage report
```
