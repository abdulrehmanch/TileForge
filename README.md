# TileForge

TileForge is a Django-based application designed for generating, managing, and serving map tiles from geospatial databases. It allows you to connect to PostgreSQL/PostGIS databases, extract geographical data, and convert it into Mapbox Vector Tiles (MVT) format for efficient web mapping applications.

## Features

- Connect to PostgreSQL/PostGIS databases and automatically discover spatial tables
- Convert spatial data into Mapbox Vector Tiles (MVT) format
- Support for asynchronous tile generation with task management
- Generate MBTiles files for offline map usage
- RESTful API for managing database connections and tile layers
- Web interface for configuration and monitoring

## Architecture

TileForge consists of several components:

- **Django Web Application**: Provides the web interface and API endpoints
- **Database Connector**: Handles connections to PostgreSQL/PostGIS databases
- **Tile Generator**: Processes spatial data and generates vector tiles
- **Task Manager**: Handles asynchronous processing of tile generation tasks
- **Tile Server**: Serves generated tiles to web mapping clients

## Prerequisites

- Python 3.10.12 or higher
- PostgreSQL with PostGIS extension
- Docker and Docker Compose (for containerized deployment)
- GDAL

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TileForge.git
   cd TileForge
   ```

2. Build and start the Docker containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application at http://localhost:8000

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TileForge.git
   cd TileForge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   cd tileforge
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://localhost:8000

## Usage

### Connecting to a Spatial Database

1. Log in to the admin interface at http://localhost:8000/admin
2. Navigate to the "Database Connections" section
3. Click "Add Database Connection" and fill in the required fields:
   - Host: The database server hostname or IP
   - Database Name: The name of the spatial database
   - User & Password: Database credentials
   - Driver: Select "PostgreSQL"
   - Port: Database port (default: 5432)
4. Save the connection. The system will automatically detect spatial tables in the database.

### Creating a Vector Tile Layer

1. Navigate to the "MVT Layers" section in the admin interface
2. Click "Add MVT Layer" and fill in the required fields:
   - Database Connection: Select a previously configured connection
   - Layer Name: A name for your tile layer
   - Geometry Type: The type of geometry (point, line, polygon)
   - Scheme: The tile scheme (default: TMS)
3. Save the layer. The system will start generating tiles.

### Accessing Tiles

Generated tiles can be accessed through the following URL pattern: