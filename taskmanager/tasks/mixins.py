from django.http import HttpResponseBadRequest


from .services import can_add_task_to_sprint


class SprintTaskMixin:
    """
    Mixin para garantir que uma tarefa que está sendo criada ou atualizada esteja dentro
    do intervalo de datas de seu sprint associado.
    """

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object() if hasattr(self, "get_object") else None
        sprint_id = request.POST.get("sprint")

        if sprint_id:
            # Se uma tarefa existir (para UpdateView) ou estiver prestes a ser criada (para CreateView)
            if task or request.method == "POST":
                if not can_add_task_to_sprint(task, sprint_id):
                    return HttpResponseBadRequest("A data de criação da tarefa está fora do"
                                                  " intervalo de datas do sprint associado.")
        return super().dispatch(request, *args, **kwargs)
