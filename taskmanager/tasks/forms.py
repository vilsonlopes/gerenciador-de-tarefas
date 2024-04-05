from django import forms
from .fields import EmailsListField

from .models import Task, SubscribeEmail


class TaskForm(forms.ModelForm):

    watchers = EmailsListField(required=False)

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'watchers', 'file_upload', 'image_upload']

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['watchers'].initial = ', '.join(email.email for email in self.instance.watchers.all())

    def save(self, commit=True):
        task = super().save(commit)
        if commit:
            task.watchers.all().delete()

            for email_str in self.cleaned_data['watchers']:
                SubscribeEmail.objects.create(email=email_str, task=task)
        return task


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
