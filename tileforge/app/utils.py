import psycopg2


def get_geom_type(db_connection, table_name):
    # Get a geometry type from a database

    conn = psycopg2.connect(
        host=db_connection.host,
        database=db_connection.database_name,
        user=db_connection.user,
        password=db_connection.password,
        port=db_connection.port
    )
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT type
            FROM geometry_columns
            WHERE f_table_schema = 'public'
              AND f_table_name = %s
            """,
            (table_name,)
        )
        geom_type = cursor.fetchone()[0]
    conn.close()

    if geom_type == 'POINT' or geom_type == 'MULTIPOINT':
        geom_type = 'circle'
    elif geom_type == 'LINESTRING' or geom_type == 'MULTILINESTRING':
        geom_type = 'line'
    elif geom_type == 'POLYGON' or geom_type == 'MULTIPOLYGON':
        geom_type = 'fill'
    else:
        geom_type = 'fill'

    return geom_type
