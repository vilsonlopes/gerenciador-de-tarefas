from django import forms
from django.core.validators import EmailValidator


email_validator = EmailValidator(message="Um ou mais endereços de e-mail não são válidos")


class EmailsListField(forms.CharField):
    def to_python(self, value):
        """Normalizar dados em uma lista de cadeias de caracteres."""
        # Return an empty list if no input was given.
        if not value:
            return []
        return [email.strip() for email in value.split(",")]

    def validate(self, value):
        """Check if value consists only of valid emails."""
        super().validate(value)
        for email in value:
            email_validator(email)
