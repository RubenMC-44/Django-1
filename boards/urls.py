from django.urls import path
from . import views

urlpatterns = [
    # Tableros
    path('', views.board_list, name='board_list'),
    path('boards/create/', views.board_create, name='board_create'),
    path('boards/<int:pk>/', views.board_detail, name='board_detail'),
    path('boards/<int:pk>/edit/', views.board_update, name='board_update'),
    path('boards/<int:pk>/delete/', views.board_delete, name='board_delete'),

    # Columnas (TaskList)
    path('boards/<int:board_pk>/lists/create/', views.tasklist_create, name='tasklist_create'),
    path('boards/<int:board_pk>/lists/<int:pk>/edit/', views.tasklist_update, name='tasklist_update'),
    path('boards/<int:board_pk>/lists/<int:pk>/delete/', views.tasklist_delete, name='tasklist_delete'),

    # Tareas
    path('boards/<int:board_pk>/lists/<int:list_pk>/tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),

    # Drag & Drop AJAX
    path('tasks/move/', views.task_move, name='task_move'),

    # Etiquetas
    path('boards/<int:board_pk>/labels/create/', views.label_create, name='label_create'),
    path('boards/<int:board_pk>/labels/<int:pk>/delete/', views.label_delete, name='label_delete'),
]
