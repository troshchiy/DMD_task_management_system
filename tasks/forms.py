from django import forms
from tasks.models import Task


EMPTY_TITLE_ERROR = "You can't create a task with empty title"


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title',)
        widgets = {
            'title': forms.fields.TextInput(attrs={
                'placeholder': 'Title',
            })
        }
        error_messages ={
            'title': {'required': EMPTY_TITLE_ERROR}
        }
