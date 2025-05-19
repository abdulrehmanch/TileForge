import json

from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from .models import DatabaseConnection, Task, MVTLayer
from .tasks import generate_mbtiles, check_task_status  # Background task

admin.site.site_header = "TileForge Admin Portal"
admin.site.site_title = "TileForge"
admin.site.index_title = "Welcome to the Admin Dashboard"


class TableSelectionForm(forms.Form):
    """
    Display a dropdown in the Django Admin to select a geometry table for MBTiles generation.
    """
    table_name = forms.ChoiceField(label="Select Table")

    def __init__(self, *args, table_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if table_choices:
            self.fields["table_name"].choices = table_choices


@admin.register(DatabaseConnection)
class DatabaseConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'database_name', 'host', 'port', 'user', 'password', 'generate_mbtiles_link')

    def generate_mbtiles_link(self, obj):
        from django.utils.html import format_html
        return format_html(
            '<a class="button" href="{}">Generate MBTiles</a>',
            f"{obj.id}/generate-mbtiles/"
        )

    generate_mbtiles_link.short_description = "Generate MBTiles"

    # change_list_template = "admin/databaseconnection_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:connection_id>/generate-mbtiles/',
                self.admin_site.admin_view(self.generate_mbtiles_view),
                name="generate_mbtiles",
            ),
        ]
        return custom_urls + urls

    def generate_mbtiles_view(self, request, connection_id):
        """
        Admin view to generate MBTiles for the selected database connection.
        """
        db_connection = DatabaseConnection.objects.get(pk=connection_id)

        # Get tables from table_names JSON
        try:
            table_names = json.loads(db_connection.table_names)
            table_choices = [(table, table) for table in table_names]
        except Exception as e:
            self.message_user(request, f"Error fetching table names: {e}", level="error")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Handle form submission
        if request.method == "POST":
            form = TableSelectionForm(request.POST, table_choices=table_choices)
            if form.is_valid():
                table_name = form.cleaned_data["table_name"]

                # Trigger the background task to generate MBTiles
                task = generate_mbtiles.delay(
                    host=db_connection.host,
                    db_name=db_connection.database_name,
                    user=db_connection.user,
                    password=db_connection.password,
                    port=db_connection.port,
                    table_name=table_name,
                )

                Task.objects.create(
                    task_id=task.id,
                    table_name=table_name,
                    database_name=db_connection.database_name,
                )

                self.message_user(request, f"MBTiles generation started for table '{table_name}' (Task ID: {task.id}).")
                # return HttpResponseRedirect("../..")
        else:
            form = TableSelectionForm(table_choices=table_choices)

        tasks = Task.objects.filter(database_name=db_connection.database_name).order_by('-started_at')
        task_data = []
        for task in tasks:
            task_info = {
                'task_id': task.task_id,
                'table_name': task.table_name,
                'status': 'Unknown',
                'started_at': task.started_at,
                'completed_at': task.completed_at,
                'result': "",
            }
            task_status = check_task_status(task.task_id)
            task_info['status'] = task_status['status']
            task_info['result'] = task_status['result']
            task_data.append(task_info)

        context = {
            "form": form,
            "connection": db_connection,
            "title": "Generate MBTiles",
            "tasks": task_data,
        }
        return render(request, "admin/generate_mbtiles.html", context)


@admin.register(MVTLayer)
class MVTLayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'db_connection', 'layer_name', 'url', 'mbtiles_path', 'geometry_type')
    list_filter = ('db_connection', 'geometry_type')
    search_fields = ('layer_name', 'url', 'mbtiles_path')
