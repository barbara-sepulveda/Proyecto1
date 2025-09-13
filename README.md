# 🗳️ Proyecto Encuestas

Este es un sistema de **encuestas e incidencias** desarrollado con **Django + PostgreSQL**, que permite gestionar usuarios, roles y diferentes módulos de organización.

## 🚀 Funcionalidades principales
- **Usuarios y Roles**: Administrador, Dirección, Departamento, Jefe de Cuadrilla, Territorial.
- **Gestión de Usuarios**: El administrador puede crear, editar y eliminar usuarios.
- **Encuestas**: Crear encuestas con preguntas y registrar respuestas.
- **Incidencias**: Registrar incidencias, asignarlas a cuadrillas y hacer seguimiento.
- **Departamentos y Direcciones**: Organización jerárquica de la institución.
- **Territorial**: Asignar incidencias por zona a responsables.

## 📂 Estructura del Proyecto
- `personas/` → Usuarios, perfiles y roles.
- `organizacion/` → Dirección y Departamento.
- `encuestas_app/` → Encuestas, preguntas y respuestas.
- `incidencias/` → Casos reportados, tipos y derivaciones.
- `territorial_app/` → Asignación de incidencias por territorio.
- `encuestas/` → Configuración principal del proyecto (settings, urls, wsgi/asgi).
- `templates/` → Vistas base, login/logout, etc.

## Instalación rápida
conda create -n encuestas_env python==3.11
conda activate encuestas_env
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
