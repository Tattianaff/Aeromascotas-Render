#!/usr/bin/env bash

# Instalar dependencias necesarias (por si acaso)
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# (Render se encarga de ejecutar gunicorn luego)
