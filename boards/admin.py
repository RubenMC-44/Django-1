from django.contrib import admin
from .models import Board, TaskList, Task, Label


class TaskListInline(admin.TabularInline):
    model = TaskList
    extra = 0


class LabelInline(admin.TabularInline):
    model = Label
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'owner__username']
    inlines = [TaskListInline, LabelInline]


@admin.register(TaskList)
class TaskListAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'order']
    list_filter = ['board']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task_list', 'priority', 'assigned_to', 'due_date']
    list_filter = ['priority', 'task_list__board']
    search_fields = ['title', 'description']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'board']
