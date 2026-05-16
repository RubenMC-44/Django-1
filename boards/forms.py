from django import forms
from django.contrib.auth.models import User
from .models import Board, TaskList, Task, Label


class BoardForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Miembros',
        help_text='Selecciona los usuarios que tendrán acceso a este tablero.',
    )

    class Meta:
        model = Board
        fields = ['title', 'description', 'members']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tablero',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional...',
            }),
        }


class TaskListForm(forms.ModelForm):
    class Meta:
        model = TaskList
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la columna',
            }),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'task_list', 'priority', 'due_date', 'assigned_to', 'labels']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional...',
            }),
            'task_list': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'labels': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, board, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limitar listas al tablero actual
        self.fields['task_list'].queryset = TaskList.objects.filter(board=board)
        # Limitar asignación a propietario + miembros
        all_member_ids = list(board.members.values_list('pk', flat=True)) + [board.owner_id]
        self.fields['assigned_to'].queryset = User.objects.filter(pk__in=all_member_ids)
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = '— Sin asignar —'
        # Limitar etiquetas al tablero actual
        self.fields['labels'].queryset = Label.objects.filter(board=board)
        self.fields['labels'].required = False


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la etiqueta',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control form-control-color',
                'type': 'color',
            }),
        }
