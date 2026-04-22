from django import forms
from .models import tasks  

class TaskForm(forms.ModelForm):
    class Meta:
        model = tasks  
        fields = ['title', 'description', 'priority', 'status', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        from django.utils import timezone
        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due_date