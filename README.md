# KilimoSTAT - Open Data Platform for the Ministry of Agriculture and Livestock Development.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0.3-green.svg)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

KilimoSTAT is an open data and analytics platform developed by the Ministry of Agriculture and Livestock Development to support evidence-based decision-making in agriculture. It aggregates data from multiple sources and presents it through dashboards, reports, and downloadable datasets.

## Features

- 📊 **Comprehensive Data Models**: Areas, Indicators, Data Providers, Sources, Sectors, and more
- 🌳 **Hierarchical Area Management**: MPTT-based tree structure for geographic areas
- 🔍 **Advanced Filtering**: Django Filter backends for complex queries
- 📈 **RESTful API**: Full-featured API with OpenAPI 3 documentation
- 📝 **Metadata Management**: Comprehensive metadata tracking for data lineage
- 🔐 **Authentication**: Token-based authentication with Axes for security
- 📤 **Import/Export**: Bulk data operations with django-import-export
- 📱 **Responsive Admin**: Enhanced Django admin interface
- 🚀 **Celery Integration**: Async task processing (optional)

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: Relational (production), SQLite (development)
- **API Documentation**: drf-spectacular (OpenAPI 3)
- **Authentication**: Token Authentication, django-axes
- **Task Queue**: Celery with Redis
- **GIS**: django-mptt for tree structures


## Installation
### Prerequisites

- Python 3.11 or higher
- PostgreSQL (optional, SQLite works for development)
- Redis (optional, for Celery)
- Git

### Quick Start

1. **Clone the repository**
git clone https://github.com/yourusername/kilimostat-backend.git
cd kilimostat-backend


### Virtual Environment
python -m venv k-stat-env
source k-stat-env/bin/activate  # On Windows: k-stat-env\Scripts\activate
### Install dependencies
pip install -r requirements.txt

### Configure environment variables
cp .env.example .env
# Edit .env with your configuration

### Run migrations
python manage.py migrate

### Create superuser
python manage.py createsuperuser

### Run development server
python manage.py runserver

### Access the application

Admin interface: http://localhost:8000/admin/

API root: http://localhost:8000/api/

API documentation: http://localhost:8000/api/swagger/

### Git
git remote add origin https://github.com/KalroDevs/kilimostat-backend.git
git branch -M main
git push -u origin main

echo "# kilimostat-backend" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/KalroDevs/kilimostat-backend.git
git push -u origin main