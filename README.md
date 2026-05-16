# TaskBoard – Gestor de Tareas Avanzado

Aplicación web tipo Trello desarrollada con Django 5 como proyecto del Máster de Desarrollo Full Stack.

## Descripción

TaskBoard permite organizar tareas en tableros kanban con columnas personalizables. Las tarjetas se pueden mover entre columnas mediante drag & drop, asignar a usuarios, etiquetar con colores y establecer fechas límite y prioridades.

## Tecnologías

- Python 3.12
- Django 5.2
- SQLite
- Bootstrap 5
- Vanilla JavaScript (drag & drop)

## Modelos

- **Board** – Tablero principal con propietario y miembros
- **TaskList** – Columna dentro de un tablero
- **Task** – Tarea con prioridad, etiquetas, fecha límite y asignación
- **Label** – Etiqueta de color asociada a un tablero

## Funcionalidades

- Registro, login y logout de usuarios
- CRUD completo de tableros, columnas y tareas
- Asignación de tareas a miembros del tablero
- Prioridad (baja, media, alta) con badges de color
- Etiquetas personalizadas con color por tablero
- Fechas límite por tarea
- Drag & drop entre columnas con actualización en tiempo real (AJAX)
- Panel de administración Django en `/admin/`

## Instalación local

```bash
# 1. Clonar el repositorio
git clone https://github.com/RubenMC-44/Django-1.git
cd "Proyecto 1"

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario (opcional)
python manage.py createsuperuser

# 6. Arrancar el servidor
python manage.py runserver
```

Abre el navegador en `http://127.0.0.1:8000`

## Demo

[rubenmc44.pythonanywhere.com](http://rubenmc44.pythonanywhere.com)
