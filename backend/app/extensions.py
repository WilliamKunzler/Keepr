"""Instâncias das extensões Flask.

Mantidas fora do factory pra permitir que models, services e blueprints
importem (`from app.extensions import db`) sem ciclo de importação.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler

db = SQLAlchemy()
jwt = JWTManager()
scheduler = APScheduler()
