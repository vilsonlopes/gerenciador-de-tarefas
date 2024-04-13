import uuid

from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.forms import modelformset_factory
from .fields import EmailsListField

from .models import Task, SubscribeEmail, FormSubmission


class TaskFormWithModel(forms.ModelForm):
    uuid = forms.UUIDField(required=False, widget=forms.HiddenInput())

    watchers = EmailsListField(required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'watchers', 'file_upload', 'image_upload']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['watchers'].initial = ', '.join(email.email for email in self.instance.watchers.all())
        self.fields["uuid"].initial = uuid.uuid4()

    def clean_uuid(self):
        uuid_value = self.cleaned_data.get("uuid")

        with transaction.atomic():
            # Tente registrar o envio do formulário por UUID
            try:
                FormSubmission.objects.create(uuid=uuid_value)
            except IntegrityError:
                # O UUID já existe, portanto o formulário já foi enviado
                raise ValidationError("This form has already been submitted.")

        return uuid_value

    def save(self, commit=True):
        task = super().save(commit)
        if commit:
            task.watchers.all().delete()

            for email_str in self.cleaned_data['watchers']:
                SubscribeEmail.objects.create(email=email_str, task=task)
        return task


class TaskFormWithRedis(forms.ModelForm):
    uuid = forms.UUIDField(required=False, widget=forms.HiddenInput())
    watchers = EmailsListField(required=False)

    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "status",
            "watchers",
            "file_upload",
            "image_upload",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["watchers"].initial = ", ".join(
                email.email for email in self.instance.watchers.all()
            )
        self.fields["uuid"].initial = uuid.uuid4()

    def clean_uuid(self):
        uuid_value = str(self.cleaned_data.get("uuid"))

        was_set = cache.set(uuid_value, "submitted", nx=True)
        if not was_set:
            # Se 'was_set' for False, o UUID já existe no cache.
            # Isso indica um envio de formulário duplicado.
            raise ValidationError("This form has already been submitted.")
        return uuid_value


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


EpicFormSet = modelformset_factory(Task, form=TaskForm, extra=0)
