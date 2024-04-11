from collections import defaultdict
from datetime import date

from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import redirect, render
from django.template import loader
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import FormView

from . import services
from .forms import TaskForm, ContactForm, EpicFormSet
from .mixins import SprintTaskMixin
from .models import Task


class TaskListView(ListView):
    model = Task
    template_name = "task_list.html"
    context_object_name = "tasks"


class TaskDetailView(DetailView):
    model = Task
    template_name = "tasks/task_detail.html"
    context_object_name = "task"


class TaskCreateView(CreateView):
    model = Task
    template_name = "tasks/task_form.html"
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskUpdateView(SprintTaskMixin, UpdateView):
    model = Task
    template_name = "tasks/task_form.html"
    fields = ("title", "description")

    def get_success_url(self):
        return reverse_lazy("tasks:task-detail", kwargs={"pk": self.object.id})


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "tasks/task_confirm_delete.html"
    success_url = reverse_lazy("tasks:task-list")


def task_home(request):
    # Obter todas as tarefas de uma só vez
    tasks = Task.objects.filter(
        status__in=["UNASSIGNED", "IN_PROGRESS", "DONE", "ARCHIVED"]
    )

    # Inicializar dicionários para manter as tarefas por status
    context = defaultdict(list)

    # Categorizar as tarefas em suas respectivas listas
    for task in tasks:
        if task.status == "UNASSIGNED":
            context["unassigned_tasks"].append(task)
        elif task.status == "IN_PROGRESS":
            context["in_progress_tasks"].append(task)
        elif task.status == "DONE":
            context["done_tasks"].append(task)
        elif task.status == "ARCHIVED":
            context["archived_tasks"].append(task)

    return render(request, "tasks/home.html", context)


def task_by_date(request: HttpRequest, by_date: date) -> HttpResponse:
    template = loader.get_template("task_list.html")
    tasks = services.get_task_by_date(by_date)
    context = {"tasks": tasks}  # dados a serem injetados no template
    html = template.render(context, request)
    return HttpResponse(html)


def create_task_on_sprint(request: HttpRequest, sprint_id: int) -> HttpResponseRedirect:
    if request.method == "POST":
        task_data: dict[str, str] = {
            "title": request.POST["title"],
            "description": request.POST.get("description", ""),
            "status": request.POST.get("status", "UNASSIGNED"),
        }
        task = services.create_task_and_add_to_sprint(
            task_data, sprint_id, request.user
        )
        return redirect("tasks:task-detail", task_id=task.id)
    raise Http404("Not found")


def claim_task_view(request, task_id):
    user_id = (
        request.user.id
    )  # Supondo que você tenha acesso ao ID do usuário da solicitação

    try:
        services.claim_task(user_id, task_id)
        return JsonResponse({"message": "Task successfully claimed."})
    except Task.DoesNotExist:
        return HttpResponse("Task does not exist.", status=404)
    except services.TaskAlreadyClaimedException:
        return HttpResponse("Task is already claimed or completed.", status=400)


def custom_404(request, exception):
    return render(request, "404.html", {}, status=404)


class ContactFormView(FormView):
    template_name = "tasks/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("tasks:contact-success")

    def form_valid(self, form):
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")
        from_email = form.cleaned_data.get("from_email")
        services.send_contact_email(subject, message, from_email, ['your-email@example.com'])
        return super().form_valid(form)


def manage_epic_tasks(request, epic_pk):
    epic = services.get_epic_by_id(epic_pk)
    if not epic:
        raise Http404("Epic não existe.")
    if request.method == "POST":
        formset = EpicFormSet(request.POST, queryset=services.get_tasks_for_epic(epic))       
        if formset.is_valid():
            tasks = formset.save(commit=False)
            services.save_tasks_form_epic(epic, tasks)
            formset.save_m2m()
            return redirect('tasks:task-list')
    else:
        formset = EpicFormSet(queryset=services.get_tasks_for_epic(epic))       
    return render(request, 'tasks/manage.epic.html', {'formset': formset, 'epic': epic})
