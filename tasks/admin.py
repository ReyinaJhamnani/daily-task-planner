from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'priority', 'completed', 'created_at']
    list_filter = ['completed', 'priority', 'date']
    search_fields = ['title', 'description']
    list_editable = ['completed', 'priority']
