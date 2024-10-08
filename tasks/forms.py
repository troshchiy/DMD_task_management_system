from django import forms
from tasks.models import Task


class EmptyFieldErrorMessage:
    def __init__(self, field_name):
        self.message = f"You can't create a task with empty {field_name}"

    def __str__(self):
        return self.message


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'performers', 'deadline', 'status')
        widgets = {
            'title': forms.fields.TextInput(attrs={
                'placeholder': 'Title',
            }),
            'description': forms.fields.Textarea(attrs={
                'placeholder': 'Description',
                'rows': 1,
                'oninput': 'autoGrow(this)'
            }),
            'performers': forms.fields.TextInput(attrs={
                'placeholder': 'Performers',
            }),
            'deadline': forms.fields.DateTimeInput(attrs={
                'placeholder': 'e.g. 2025-01-25 14:30',
            }, format='%Y-%m-%d %H:%M'),
            'status': forms.fields.Select(choices=Task.Status.choices)
        }
        error_messages ={
            'title': {'required': str(EmptyFieldErrorMessage('title'))},
            'description': {'required': str(EmptyFieldErrorMessage('description'))},
            'performers': {'required': str(EmptyFieldErrorMessage('performers'))},
            'deadline': {'required': str(EmptyFieldErrorMessage('deadline'))},
            'status': {'required': str(EmptyFieldErrorMessage('status'))},
        }

    def __init__(self, *args, **kwargs):
        forms.ModelForm.__init__(self, *args, **kwargs)
        self.fields['status'].widget.choices.blank_choice = []
