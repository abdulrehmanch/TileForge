import json

import psycopg2
from django.core.exceptions import ValidationError
from django.db import models


class DatabaseConnection(models.Model):
    DRIVER_CHOICES = [
        ('postgres', 'PostgreSQL'),
    ]

    host = models.CharField(max_length=255, help_text="Hostname or IP address of the database server")
    database_name = models.CharField(max_length=255, help_text="Name of the database")
    user = models.CharField(max_length=255, help_text="Database username")
    password = models.CharField(max_length=255, help_text="Database password")
    driver = models.CharField(max_length=50, choices=DRIVER_CHOICES, help_text="Database driver")
    port = models.PositiveIntegerField(default=5432, help_text="Port number of the database server")
    table_names = models.TextField(blank=True, null=True, help_text="JSON list of table names in the database")

    def __str__(self):
        return f"{self.database_name} at {self.host} ({self.get_driver_display()})"

    def clean(self):
        """Custom validation for database connectivity and fetching table names."""
        if self.driver == 'postgres':
            try:
                # Attempt connection using psycopg2
                connection = psycopg2.connect(
                    host=self.host,
                    database=self.database_name,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )

                # Fetch table names from the connected database
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT f_table_name AS table_name
                        FROM geometry_columns
                        WHERE f_table_schema = 'public';
                        """
                    )
                    tables = cursor.fetchall()

                # Extract table names and store as JSON
                self.table_names = json.dumps([table[0] for table in tables])

                connection.close()  # Close the connection if it is successful
            except psycopg2.OperationalError as e:
                raise ValidationError(f"Unable to connect to PostgreSQL database: {e}")
            except Exception as e:
                raise ValidationError(f"An error occurred while fetching table names: {e}")
        else:
            raise ValidationError(f"Connection validation is only implemented for PostgreSQL at the moment.")

    def save(self, *args, **kwargs):
        # Calls the clean method to validate connection and fetch table names before saving
        self.clean()
        super().save(*args, **kwargs)


class Task(models.Model):
    task_id = models.CharField(max_length=36, unique=True)
    table_name = models.CharField(max_length=255)
    started_at = models.DateTimeField(auto_now_add=True)
    database_name = models.CharField(max_length=255, help_text="Name of the database")
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.task_id


class MVTLayer(models.Model):
    db_connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE)
    layer_name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    mbtiles_path = models.CharField(max_length=255)
    geometry_type = models.CharField(max_length=255)

    def __str__(self):
        return self.layer_name
