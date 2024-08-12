# FastAPI Admin

FastAPI Admin is a management backend framework based on FastAPI, designed to provide an efficient, flexible, and extensible solution. This project implements a series of features suitable for building complex backend management systems.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Installation Instructions](#installation-instructions)
- [Usage Example](#usage-example)
- [License](#license)
- [Contact Information](#contact-information)

## Project Description

FastAPI Admin offers a structured FastAPI project template that integrates commonly used components, helping developers quickly set up and manage backend services. By utilizing FastAPI's powerful features, this project aims to enhance development efficiency and reduce boilerplate code.

## Features

This project implements the following key features:

1. **FastAPI Directory Structure**: A well-organized directory structure for better project management and extensibility.
2. **FastAPI Route Classes**: A flexible class design for routes, facilitating organization and management.
3. **Route Function Logging Context**: Automatic logging of route function execution for easier debugging and tracking.
4. **Caching and Request Queue Decorators**: Provide caching mechanisms and queue handling capabilities to enhance performance.
5. **Loguru Encapsulation**: Simplifies logging functions through Loguru integration.
6. **Redis Connection for Standalone and Sentinel**: Supports both standalone Redis and Sentinel mode connections.
7. **Redis Distributed Locks**: Implements distributed locks to ensure data consistency and safety.
8. **Redis Streams Publish/Subscribe Interface**: Offers publish/subscribe functionality based on Redis Streams.
9. **PostgreSQL Standalone and Master-Slave Connections**: Supports standalone and master-slave configurations for PostgreSQL databases.
10. **PostgreSQL DAO**: Provides a Data Access Object (DAO) pattern to simplify database operations.
11. **HTTP Request Encapsulation**: Unified HTTP request encapsulation, supporting both synchronous and asynchronous code.

## Installation Instructions

```bash
git clone https://github.com/kai-railg/fastapi-admin.git
cd fastapi-admin
pip install requirements.txt
bash run.sh
```


## Usage Example
Here is a basic example of how to use the FastAPI Admin project:

1. create a src/api/views/your_api_view.py file
```python

# -*- encoding: utf-8 -*-

from src.oop.api_view import BaseApiView

class YourApiView(BaseApiView):
    def get(self, body: dict) -> dict:
        return

    def get(self, body: dict) -> dict:
        return
```
2. update src/api/urls.py
```python
# insert your api route
route_list = [
    (
        "/api/yourapipath",
        YourApiView,
        {
            "summary": "the api summary", "desc": "the api desc"
        },
    ),
]
```
3. view the api docs
http://127.0.0.1:8000/docs

## License
This project is licensed under the MIT License.

## Contact Information
For any questions or suggestions, please contact Your Name.