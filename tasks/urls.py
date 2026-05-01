from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),

    # Original toggle (used by dashboard forms)
    path('tasks/toggle/<int:task_id>/', views.toggle_task, name='toggle_task'),

    # NEW: Fetch API endpoint (used by task_list.html via JS)
    path('tasks/toggle-ajax/<int:task_id>/', views.toggle_task_ajax, name='toggle_task_ajax'),

    path('tasks/delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('about/', views.about, name='about'),
]
