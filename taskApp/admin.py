from django.contrib import admin
from .models import Task

class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'author', 'created']
    list_filter = ['status', 'author']
    search_fields = ['title', 'description']
    readonly_fields = ['created', 'finished']

admin.site.register(Task, TaskAdmin)