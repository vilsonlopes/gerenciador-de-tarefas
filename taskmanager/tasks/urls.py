from django.urls import path, register_converter
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from . import converters
from .views import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
    create_task_on_sprint,
    manage_epic_tasks,
    task_by_date,
    task_home,
    ContactFormView,
)

app_name = "tasks"
register_converter(converters.DateConverter, "yyyymmdd")
handler404 = "tasks.views.custom_404"


urlpatterns = [
    path("", TemplateView.as_view(template_name="tasks/home.html"), name="home"),
    path("tasks/home/", task_home, name="task-home"),
    path("help/", TemplateView.as_view(template_name="tasks/help.html"), name="help"),
    path("tasks/", TaskListView.as_view(), name="task-list"),  # GET
    path("tasks/new/", TaskCreateView.as_view(), name="task-create"),  # POST
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),  # GET
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-update"),  # PUT/PATCH
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),  # DELETE
    path("tasks/<yyyymmdd:date>/", task_by_date, name="task-get-by-date"),
    path("tasks/sprint/add_task/<int:pk>/", create_task_on_sprint, name="task-add-to-sprint",),
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("contact-success/", TemplateView.as_view(template_name="contact_success.html"), name="contact-success",),
    path("epic/<int:epic_pk>/", manage_epic_tasks, name="task-batch-create"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
