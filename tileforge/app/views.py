import io
import os
import sqlite3
import threading

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from app.models import MVTLayer

# Use thread-local storage for connections
mbtiles_connections = threading.local()


def get_tile(z, x, y, db, table):
    # Initialize the thread-local dictionary if it doesn't exist
    if not hasattr(mbtiles_connections, 'connections'):
        mbtiles_connections.connections = {}

    # Create a new connection for this thread if needed
    if db not in mbtiles_connections.connections:
        mbtiles_path = f"../mbtiles/{db}/{table}.mbtiles"
        mbtiles_connections.connections[db] = sqlite3.connect(mbtiles_path)

    """Fetch a tile from the MBTiles database."""
    sql = f"SELECT tile_data FROM tiles WHERE zoom_level={z} AND tile_column={x} AND tile_row={y}"

    # Don't use context manager, manually create and close cursor
    cursor = mbtiles_connections.connections[db].cursor()
    tile_data = None
    try:
        cursor.execute(str(sql))
        row = cursor.fetchone()
        if row:
            tile_data = row[0]  # Return the tile data
        else:
            tile_data = b""
        cursor.close()

    except Exception as e:
        print(f"Error fetching tile: {e}")

    return tile_data


def serve_tile(request, db, table, z, x, y):
    """Serve vector tiles in PBF format."""
    mbtiles_path = f"../mbtiles/{db}/{table}.mbtiles"
    if not os.path.exists(mbtiles_path):
        return JsonResponse({"error": "MBTiles file not found"}, status=404)
    tile_data = get_tile(z, x, y, db, table)
    if tile_data:
        return HttpResponse(
            io.BytesIO(tile_data),
            content_type="application/x-protobuf",
            headers={"Content-Encoding": "gzip"}
        )
    else:
        return JsonResponse({"error": "Tile not found"}, status=204)


def map_view(request, db):
    """Render a map showing all MVTLayer records."""
    # Fetch all MVTLayer records from the database
    mvt_layers = MVTLayer.objects.filter(db_connection__database_name=db)

    # Prepare the layer data for the template
    layers = []
    for layer in mvt_layers:
        # Prepare paint properties - assuming paint is stored as a JSON string
        # If not already in JSON format, you may need to adjust this
        # try:
        #     paint = json.loads(layer.paint) if hasattr(layer, 'paint') and layer.paint else {}
        # except (json.JSONDecodeError, TypeError):
        #     paint = {}

        layers.append({
            'name': layer.layer_name if hasattr(layer, 'layer_name') else f"layer_{layer.id}",
            'db': layer.db_connection.database_name if hasattr(layer, 'db_connection') else "default",
            'table': layer.layer_name if hasattr(layer, 'layer_name') else "default",
            'min_zoom': layer.min_zoom if hasattr(layer, 'min_zoom') else 0,
            'max_zoom': layer.max_zoom if hasattr(layer, 'max_zoom') else 14,
            'geom_type': layer.geometry_type if hasattr(layer, 'geometry_type') else "fill",
            'scheme': layer.scheme if hasattr(layer, 'scheme') else 'tms',
        })

    return render(request, 'MVTLayerMap.html', {'layers': layers})
