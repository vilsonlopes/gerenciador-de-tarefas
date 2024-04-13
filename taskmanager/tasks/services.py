import datetime
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail

from .models import Sprint, Task, Epic


class TaskAlreadyClaimedException(Exception):
    pass


def can_add_task_to_sprint(task, sprint_id):
    """
    Verifica se uma tarefa pode ser adicionada a um sprint com base no intervalo de datas do sprint.
    """
    sprint = get_object_or_404(Sprint, id=sprint_id)
    return sprint.start_date <= task.created_at.date() <= sprint.end_date


def get_task_by_date(by_date: date) -> list[Task]:
    return Task.objects.annotate(date_created=TruncDate("created_at")).filter(
        date_created=by_date
    )


def create_task_and_add_to_sprint(task_data: dict[str, str], sprint_id: int, creator: User) -> Task:
    """
    Crie uma nova tarefa e associe-a a um sprint.
    """

    # Buscar o sprint por sua ID
    sprint = Sprint.objects.get(id=sprint_id)

    # Obter a data e a hora atuais
    now = datetime.now()

    # Verificar se a data e a hora atuais estão dentro das datas de início e término do sprint
    if not (sprint.start_date <= now <= sprint.end_date):
        raise ValidationError(
            "Não é possível adicionar tarefa ao sprint: \
                               A data atual não está dentro do limite de \
                               datas de início e término do sprint."
        )
    with transaction.atomic():
        # Criar a tarefa
        task = Task.objects.create(
            title=task_data["title"],
            description=task_data.get("description", ""),
            status=task_data.get("status", "UNASSIGNED"),
            creator=creator,
        )

        # Adicionar a tarefa ao sprint
        sprint.tasks.add(task)

    return task


@transaction.atomic
def claim_task(user_id: int, task_id: int) -> None:
    # Bloquear a linha da tarefa para impedir que outras transações a utilizem simultaneamente
    task = Task.objects.select_for_update().get(id=task_id)

    # Verificar se a tarefa já foi reivindicada
    if task.owner_id:
        raise TaskAlreadyClaimedException("A tarefa já foi reivindicada ou concluída.")

    # Reivindicar a tarefa
    task.status = "IN_PROGRESS"
    task.owner_id = user_id
    task.save()


def claim_task_optimistically(user_id: int, task_id: int) -> None:
    try:
        # Etapa 1: Leia a tarefa e sua versão
        task = Task.objects.get(id=task_id)
        original_version = task.version

        # Etapa 2: Verifique se a tarefa já foi reivindicada
        if task.owner_id:
            raise ValidationError("A tarefa já foi reivindicada ou concluída.")

        # Etapa 3: Reivindicar a tarefa
        task.status = "IN_PROGRESS"
        task.owner_id = user_id

        # Etapa 4: Salve a tarefa e atualize a versão, mas somente se a versão não tiver sido alterada
        updated_rows = Task.objects.filter(id=task_id, version=original_version).update(
            status=task.status,
            owner_id=task.owner_id,
            version=F("version") + 1,  # Increment version field
        )

        # Se nenhuma linha foi atualizada, isso significa que outra transação alterou a tarefa
        if updated_rows == 0:
            raise ValidationError("A tarefa foi atualizada por outra transação.")

    except Task.DoesNotExist:
        raise ValidationError("A tarefa não existe.")


def send_contact_email(subject: str, message: str, from_email: str, to_email: str) -> None:
    send_mail(subject, message, from_email, [to_email])


def get_epic_by_id(epic_id: int) -> Epic | None:
    return Epic.objects.filter(pk=epic_id).first()


def get_tasks_for_epic(epic: Epic) -> list[Task]:
    return Task.objects.filter(epics=epic)


def save_tasks_for_epic(epic: Epic, tasks: list[Task]) -> None:
    for task in tasks:
        task.save()
        task.epics.add(epic)
