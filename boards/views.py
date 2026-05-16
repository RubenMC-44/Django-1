import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BoardForm, LabelForm, TaskForm, TaskListForm
from .models import Board, Label, Task, TaskList


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _user_can_access_board(user, board):
    """Comprueba si el usuario es propietario o miembro del tablero."""
    return user == board.owner or board.members.filter(pk=user.pk).exists()


# ──────────────────────────────────────────────
# Tableros
# ──────────────────────────────────────────────

@login_required
def board_list(request):
    """Lista todos los tableros a los que el usuario tiene acceso."""
    boards = Board.objects.filter(
        models.Q(owner=request.user) | models.Q(members=request.user)
    ).distinct()
    return render(request, 'boards/board_list.html', {'boards': boards})


@login_required
def board_create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.owner = request.user
            board.save()
            form.save_m2m()
            messages.success(request, 'Tablero creado correctamente.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm()
    return render(request, 'boards/board_form.html', {'form': form, 'action': 'Crear tablero'})


@login_required
def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    task_lists = board.task_lists.prefetch_related(
        'tasks__labels',
        'tasks__assigned_to',
    ).order_by('order')

    return render(request, 'boards/board_detail.html', {
        'board': board,
        'task_lists': task_lists,
        'can_edit': request.user == board.owner,
    })


@login_required
def board_update(request, pk):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tablero actualizado.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = BoardForm(instance=board)
    return render(request, 'boards/board_form.html', {
        'form': form,
        'board': board,
        'action': 'Editar tablero',
    })


@login_required
def board_delete(request, pk):
    board = get_object_or_404(Board, pk=pk, owner=request.user)
    if request.method == 'POST':
        board.delete()
        messages.success(request, 'Tablero eliminado.')
        return redirect('board_list')
    return render(request, 'boards/board_confirm_delete.html', {'board': board})


# ──────────────────────────────────────────────
# Columnas (TaskList)
# ──────────────────────────────────────────────

@login_required
def tasklist_create(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk)
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    if request.method == 'POST':
        form = TaskListForm(request.POST)
        if form.is_valid():
            task_list = form.save(commit=False)
            task_list.board = board
            # Asignar orden al final
            last_order = board.task_lists.aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            task_list.order = last_order + 1
            task_list.save()
            messages.success(request, f'Columna "{task_list.title}" creada.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskListForm()

    return render(request, 'boards/tasklist_form.html', {
        'form': form,
        'board': board,
        'action': 'Añadir columna',
    })


@login_required
def tasklist_update(request, board_pk, pk):
    board = get_object_or_404(Board, pk=board_pk)
    task_list = get_object_or_404(TaskList, pk=pk, board=board)
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    if request.method == 'POST':
        form = TaskListForm(request.POST, instance=task_list)
        if form.is_valid():
            form.save()
            messages.success(request, 'Columna actualizada.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskListForm(instance=task_list)

    return render(request, 'boards/tasklist_form.html', {
        'form': form,
        'board': board,
        'task_list': task_list,
        'action': 'Editar columna',
    })


@login_required
@require_POST
def tasklist_delete(request, board_pk, pk):
    board = get_object_or_404(Board, pk=board_pk)
    task_list = get_object_or_404(TaskList, pk=pk, board=board)
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    task_list.delete()
    messages.success(request, 'Columna eliminada.')
    return redirect('board_detail', pk=board.pk)


# ──────────────────────────────────────────────
# Tareas
# ──────────────────────────────────────────────

@login_required
def task_create(request, board_pk, list_pk):
    board = get_object_or_404(Board, pk=board_pk)
    task_list = get_object_or_404(TaskList, pk=list_pk, board=board)
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    if request.method == 'POST':
        form = TaskForm(board, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # Asignar orden al final de la lista
            last_order = task_list.tasks.aggregate(
                max_order=models.Max('order')
            )['max_order'] or 0
            task.order = last_order + 1
            task.save()
            form.save_m2m()
            messages.success(request, f'Tarea "{task.title}" creada.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(board, initial={'task_list': task_list})

    return render(request, 'boards/task_form.html', {
        'form': form,
        'board': board,
        'task_list': task_list,
        'action': 'Crear tarea',
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')
    return render(request, 'boards/task_detail.html', {'task': task, 'board': board})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    if request.method == 'POST':
        form = TaskForm(board, request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea actualizada.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = TaskForm(board, instance=task)

    return render(request, 'boards/task_form.html', {
        'form': form,
        'board': board,
        'task': task,
        'action': 'Editar tarea',
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    board = task.task_list.board
    if not _user_can_access_board(request.user, board):
        messages.error(request, 'No tienes acceso a este tablero.')
        return redirect('board_list')

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tarea eliminada.')
        return redirect('board_detail', pk=board.pk)

    return render(request, 'boards/task_confirm_delete.html', {'task': task, 'board': board})


# ──────────────────────────────────────────────
# Drag & Drop (AJAX)
# ──────────────────────────────────────────────

@login_required
@require_POST
def task_move(request):
    """
    Endpoint AJAX para mover una tarea a otra columna o posición.
    Recibe JSON: { task_id, list_id, order }
    """
    try:
        data = json.loads(request.body)
        task_id = int(data['task_id'])
        new_list_id = int(data['list_id'])
        new_order = int(data['order'])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)

    task = get_object_or_404(Task, pk=task_id)
    new_list = get_object_or_404(TaskList, pk=new_list_id)
    board = new_list.board

    # Verificar acceso
    if not _user_can_access_board(request.user, board):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    # Verificar que la tarea y la lista nueva pertenecen al mismo tablero
    if task.task_list.board != board:
        return JsonResponse({'success': False, 'error': 'Tablero diferente'}, status=403)

    with transaction.atomic():
        old_list = task.task_list
        old_order = task.order

        if old_list == new_list:
            # Reordenar dentro de la misma columna
            if old_order < new_order:
                Task.objects.filter(
                    task_list=new_list,
                    order__gt=old_order,
                    order__lte=new_order,
                ).exclude(pk=task.pk).update(order=models.F('order') - 1)
            elif old_order > new_order:
                Task.objects.filter(
                    task_list=new_list,
                    order__gte=new_order,
                    order__lt=old_order,
                ).exclude(pk=task.pk).update(order=models.F('order') + 1)
        else:
            # Mover a otra columna: compactar la columna de origen
            Task.objects.filter(
                task_list=old_list,
                order__gt=old_order,
            ).update(order=models.F('order') - 1)
            # Hacer hueco en la columna destino
            Task.objects.filter(
                task_list=new_list,
                order__gte=new_order,
            ).update(order=models.F('order') + 1)
            task.task_list = new_list

        task.order = new_order
        task.save(update_fields=['task_list', 'order'])

    return JsonResponse({'success': True})


# ──────────────────────────────────────────────
# Etiquetas
# ──────────────────────────────────────────────

@login_required
def label_create(request, board_pk):
    board = get_object_or_404(Board, pk=board_pk, owner=request.user)
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.board = board
            label.save()
            messages.success(request, f'Etiqueta "{label.name}" creada.')
            return redirect('board_detail', pk=board.pk)
    else:
        form = LabelForm()
    return render(request, 'boards/label_form.html', {'form': form, 'board': board})


@login_required
def label_delete(request, board_pk, pk):
    board = get_object_or_404(Board, pk=board_pk, owner=request.user)
    label = get_object_or_404(Label, pk=pk, board=board)
    if request.method == 'POST':
        label.delete()
        messages.success(request, 'Etiqueta eliminada.')
        return redirect('board_detail', pk=board.pk)
    return render(request, 'boards/label_confirm_delete.html', {'label': label, 'board': board})
