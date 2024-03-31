from django.urls import path, register_converter
from django.views.generic import TemplateView
from .views import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    create_task_on_sprint,
    task_by_date,
    task_home,
)
from . import views, converters


app_name = 'tasks'
register_converter(converters.DateConverter, "yyyymmdd")


urlpatterns = [
    path('', TemplateView.as_view(template_name='tasks/home.html'), name='home'),
    path("tasks/home/", task_home, name="task-home"),
    path('help/', TemplateView.as_view(template_name='tasks/help.html'), name='help'),
    path('tasks/', TaskListView.as_view(), name='task-list'), # GET
    path('tasks/<yyymmdd:date>/', views.task_by_date),
    path('tasks/new/', TaskCreateView.as_view(), name='task-create'), # POST
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'), # GET
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task-update'), # PUT/PATCH
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'), # DELETE
]
