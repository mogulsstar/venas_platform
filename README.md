# VENAS Platform - Autonomous Driving Compliance Platform

VENAS Platform is a comprehensive solution for managing autonomous driving compliance, including regulations, test cases, and data analysis.

## Features

### Regulations Module
- PDF processing pipeline with text extraction & semantic segmentation
- Multi-language translation support (English, Chinese, German)
- Version-controlled review workflow (draft → reviewed → published)
- Regulation mapping system with geo-fencing based search
- Cross-regulation similarity analysis

### TestCase Management
- Hierarchical structure: TestSuite > TestCluster > TestCase
- Dual creation modes: Manual editor and AI generator
- Review lifecycle with notifications and audit trails

### Project System
- Nested project architecture with main projects and subprojects
- Role-based access control (Owner/Editor/Observer)
- Cross-project visibility rules

### Advanced Data Analysis
- Longitudinal analysis: Single case multi-batch analysis
- Horizontal analysis: Multi-case single-batch comparison
- Template system with drag-and-drop pipeline builder

### Dashboard
- Customizable dashboards with various widget types
- Real-time data visualization
- User-specific dashboard preferences

### System Monitoring
- Performance metrics tracking
- User activity monitoring
- Task execution tracking
- Alert system

### Help Center
- Categorized help articles and FAQs
- User feedback collection
- Support request management

## Technical Stack

### Backend
- Django 4.2
- Django REST Framework
- Celery for asynchronous tasks
- MySQL database

### Frontend (Planned)
- React 18 with TypeScript
- D3.js for data visualization
- Material-UI for components

## Getting Started

### Prerequisites
- Python 3.11+
- Poetry for dependency management
- MySQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-organization/venas-platform.git
cd venas-platform
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up the database:
```bash
poetry run python manage.py migrate
```

4. Create a superuser:
```bash
poetry run python manage.py createsuperuser
```

5. Run the development server:
```bash
poetry run python manage.py runserver
```

## API Documentation

API documentation is available at `/swagger/` and `/redoc/` endpoints when the server is running.

## License

Proprietary - All rights reserved.

## Contact

For more information, please contact [contact@venas.com](mailto:contact@venas.com).
