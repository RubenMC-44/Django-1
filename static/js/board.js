/**
 * board.js – Drag & Drop para el tablero Kanban
 * Usa la API nativa de HTML5 (no requiere librerías externas).
 */

document.addEventListener('DOMContentLoaded', () => {
  let draggedCard = null;

  // ── Inicializar listeners ──────────────────────────────────────────────
  function init() {
    document.querySelectorAll('.task-card').forEach(addCardListeners);
    document.querySelectorAll('.task-list-body').forEach(addColumnListeners);
  }

  // ── Listeners de la tarjeta ───────────────────────────────────────────
  function addCardListeners(card) {
    card.addEventListener('dragstart', onDragStart);
    card.addEventListener('dragend', onDragEnd);
  }

  function onDragStart(e) {
    draggedCard = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    // Guardar el id de la tarea (por si se necesita en el futuro)
    e.dataTransfer.setData('text/plain', this.dataset.taskId);
  }

  function onDragEnd() {
    this.classList.remove('dragging');
    document.querySelectorAll('.task-list-body').forEach(col => {
      col.classList.remove('drag-over');
    });
    draggedCard = null;
  }

  // ── Listeners de la columna ───────────────────────────────────────────
  function addColumnListeners(column) {
    column.addEventListener('dragover', onDragOver);
    column.addEventListener('dragenter', onDragEnter);
    column.addEventListener('dragleave', onDragLeave);
    column.addEventListener('drop', onDrop);
  }

  function onDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  }

  function onDragEnter() {
    this.classList.add('drag-over');
  }

  function onDragLeave(e) {
    // Solo quitar la clase si salimos realmente de la columna
    if (!this.contains(e.relatedTarget)) {
      this.classList.remove('drag-over');
    }
  }

  function onDrop(e) {
    e.preventDefault();
    this.classList.remove('drag-over');

    if (!draggedCard) return;

    const oldListId = draggedCard.dataset.listId;
    const newListId = this.dataset.listId;
    const taskId = draggedCard.dataset.taskId;

    // Calcular la nueva posición dentro de la columna
    const siblings = [...this.querySelectorAll('.task-card:not(.dragging)')];
    let newOrder = 0;
    const dropY = e.clientY;

    for (let i = 0; i < siblings.length; i++) {
      const rect = siblings[i].getBoundingClientRect();
      const midpoint = rect.top + rect.height / 2;
      if (dropY < midpoint) {
        newOrder = i;
        break;
      }
      newOrder = i + 1;
    }

    // Mover la tarjeta en el DOM
    const referenceCard = siblings[newOrder] || null;
    this.insertBefore(draggedCard, referenceCard);

    // Actualizar el data-list-id de la tarjeta movida
    draggedCard.dataset.listId = newListId;

    // ── Gestión del placeholder "Sin tareas" ──────────────────────────────

    // 1. Eliminar placeholder de la columna destino (acaba de recibir una tarjeta)
    const destPlaceholder = this.querySelector('.empty-column');
    if (destPlaceholder) destPlaceholder.remove();

    // 2. Si la columna origen quedó sin tarjetas, mostrar su placeholder
    if (oldListId !== newListId) {
      const sourceColumn = document.querySelector(
        `.task-list-body[data-list-id="${oldListId}"]`
      );
      if (sourceColumn && !sourceColumn.querySelector('.task-card')) {
        const placeholder = document.createElement('p');
        placeholder.className = 'text-muted small text-center py-3 empty-column';
        placeholder.textContent = 'Sin tareas';
        sourceColumn.appendChild(placeholder);
      }
    }

    // Enviar al servidor
    sendMoveRequest(taskId, newListId, newOrder);
  }

  // ── Petición AJAX al servidor ─────────────────────────────────────────
  function sendMoveRequest(taskId, listId, order) {
    fetch('/tasks/move/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({
        task_id: parseInt(taskId, 10),
        list_id: parseInt(listId, 10),
        order: order,
      }),
    })
      .then(response => response.json())
      .then(data => {
        if (!data.success) {
          console.error('Error al mover la tarea:', data.error);
          // En caso de error se podría hacer un reload para revertir el estado visual
        }
      })
      .catch(err => console.error('Error de red:', err));
  }

  // ── Helper: obtener el token CSRF de la cookie ─────────────────────────
  function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        return decodeURIComponent(trimmed.substring(name.length + 1));
      }
    }
    return '';
  }

  init();
});
