# STACHAT API

This is a FastAPI-based application for querying datasets using LangChain and Neo4j. It provides a webhook endpoint for processing questions and returning responses.

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

## Create a Virtual Environment

```bash
python -m venv venv

# Project Setup and Execution Guide

This guide provides detailed instructions for setting up and running the project. Follow the steps below to get started.

## Install Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt

# Project Setup and Execution Guide

This guide provides step-by-step instructions for setting up and running the project. Follow the steps below to configure the environment, run the application, and access the API documentation.

---

## Create a `.env` File

In the root directory of the project, create a `.env` file and add the following environment variables:

```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
WEBHOOK_SECRET=your_webhook_secret
# Activate Virtual Environment


To activate the virtual environment, use the appropriate command for your operating system:

- **On Windows:**
  ```bash
  .\venv\Scripts\activate
# FastAPI Application Setup and Deployment Guide

This guide provides instructions for updating dependencies, running the FastAPI application locally, and deploying it using Docker.

## Update Requirements

If you install new dependencies, update the `requirements.txt` file by running the following command:

```bash
pip freeze > requirements.txt

Run the Application Locally

```bash
uvicorn app.main:app --reload

# Docker Commands

If you prefer to run the application using Docker, follow these steps:

## 1. Stop Containers (if running)
To stop any running Docker containers, use the following command:

```bash
docker-compose down

Rebuild Docker Images (without cache)
```bash
docker-compose build --no-cache

Start Containers
```bash
docker-compose up
