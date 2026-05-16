from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='owned_boards',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Propietario',
                )),
                ('members', models.ManyToManyField(
                    blank=True,
                    related_name='member_boards',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Miembros',
                )),
            ],
            options={
                'verbose_name': 'Tablero',
                'verbose_name_plural': 'Tableros',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('color', models.CharField(default='#6c757d', max_length=7, verbose_name='Color')),
                ('board', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='labels',
                    to='boards.board',
                    verbose_name='Tablero',
                )),
            ],
            options={
                'verbose_name': 'Etiqueta',
                'verbose_name_plural': 'Etiquetas',
            },
        ),
        migrations.CreateModel(
            name='TaskList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('board', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='task_lists',
                    to='boards.board',
                    verbose_name='Tablero',
                )),
            ],
            options={
                'verbose_name': 'Lista de tareas',
                'verbose_name_plural': 'Listas de tareas',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('priority', models.CharField(
                    choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')],
                    default='medium',
                    max_length=10,
                    verbose_name='Prioridad',
                )),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha límite')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('task_list', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='boards.tasklist',
                    verbose_name='Lista',
                )),
                ('assigned_to', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_tasks',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Asignada a',
                )),
                ('labels', models.ManyToManyField(
                    blank=True,
                    related_name='tasks',
                    to='boards.label',
                    verbose_name='Etiquetas',
                )),
            ],
            options={
                'verbose_name': 'Tarea',
                'verbose_name_plural': 'Tareas',
                'ordering': ['order'],
            },
        ),
    ]
