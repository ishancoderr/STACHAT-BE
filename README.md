# STACHAT API

This is a FastAPI-based application for querying datasets using LangChain and Neo4j. It provides a webhook endpoint for processing questions and returning responses.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Activate Virtual Environment](#activate-virtual-environment)
4. [Update Requirements](#update-requirements)
5. [Run the Application](#run-the-application)
6. [Docker Commands](#docker-commands)
7. [API Documentation](#api-documentation)
8. [Project Structure](#project-structure)
9. [License](#license)

---

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python 3.8 or higher**
- **Docker** (optional, for running with Docker)
- **Docker Compose** (optional, for running with Docker)

---

## Setup

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
Create a virtual environment:

bash
Copy
python -m venv venv
Install dependencies:

bash
Copy
pip install -r requirements.txt
Create a .env file:

In the root directory, create a .env file and add the following environment variables:

env
Copy
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
WEBHOOK_SECRET=your_webhook_secret
Activate Virtual Environment
To activate the virtual environment, run:

On Windows:

bash
Copy
.\venv\Scripts\activate
On macOS/Linux:

bash
Copy
source venv/bin/activate
Update Requirements
If you install new dependencies, update the requirements.txt file using:

bash
Copy
pip freeze > requirements.txt
Run the Application
To run the FastAPI application locally, use:

bash
Copy
uvicorn app.main:app --reload
The application will be available at http://127.0.0.1:8000.

Docker Commands
If you prefer to run the application using Docker, follow these steps:

Stop Containers (if running):

bash
Copy
docker-compose down
Rebuild Docker Images (without cache):

bash
Copy
docker-compose build --no-cache
Start Containers:

bash
Copy
docker-compose up
The application will be available at http://127.0.0.1:8000.

API Documentation
Once the application is running, you can access the interactive API documentation:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc
This project is licensed under the MIT License. See the LICENSE file for details.

This README.md file provides a comprehensive guide for setting up and running the project. It includes instructions for both local development and Docker-based deployment, making it easy for new contributors to get started.
