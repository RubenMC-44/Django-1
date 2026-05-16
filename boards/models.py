from django.db import models
from django.contrib.auth.models import User


class Board(models.Model):
    """Tablero principal, equivalente a un tablero de Trello."""
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards',
        verbose_name='Propietario',
    )
    members = models.ManyToManyField(
        User,
        related_name='member_boards',
        blank=True,
        verbose_name='Miembros',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tablero'
        verbose_name_plural = 'Tableros'

    def __str__(self):
        return self.title

    def get_all_members(self):
        """Devuelve todos los usuarios con acceso (propietario + miembros)."""
        return User.objects.filter(
            models.Q(owned_boards=self) | models.Q(member_boards=self)
        ).distinct()


class Label(models.Model):
    """Etiqueta de color asociada a un tablero."""
    name = models.CharField(max_length=50, verbose_name='Nombre')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='Color')
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='labels',
        verbose_name='Tablero',
    )

    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'

    def __str__(self):
        return f'{self.name} ({self.board.title})'


class TaskList(models.Model):
    """Columna dentro de un tablero (ej: 'Por hacer', 'En progreso', 'Hecho')."""
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='task_lists',
        verbose_name='Tablero',
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')

    class Meta:
        ordering = ['order']
        verbose_name = 'Lista de tareas'
        verbose_name_plural = 'Listas de tareas'

    def __str__(self):
        return f'{self.board.title} › {self.title}'


class Task(models.Model):
    """Tarea dentro de una columna."""
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Baja'),
        (PRIORITY_MEDIUM, 'Media'),
        (PRIORITY_HIGH, 'Alta'),
    ]

    task_list = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Lista',
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Asignada a',
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        verbose_name='Prioridad',
    )
    labels = models.ManyToManyField(
        Label,
        blank=True,
        related_name='tasks',
        verbose_name='Etiquetas',
    )
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha límite')
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.title

    def get_priority_badge(self):
        """Devuelve la clase Bootstrap para el badge de prioridad."""
        return {
            self.PRIORITY_LOW: 'success',
            self.PRIORITY_MEDIUM: 'warning',
            self.PRIORITY_HIGH: 'danger',
        }.get(self.priority, 'secondary')
