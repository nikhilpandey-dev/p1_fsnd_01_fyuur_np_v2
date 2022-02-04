#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cgitb import text
from distutils.log import error
import json
from unicodedata import name
from wsgiref import validate
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from helpers import sqlalchemy_config
from datetime import datetime
from flask_migrate import Migrate

""" Source:https://knowledge.udacity.com/questions/649441"""
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False,unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False, server_default="{}")
    """ Changed name as per this knowedge based question:
        https://knowledge.udacity.com/questions/545169
    """
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('venue',lazy='joined'), cascade="all, delete")
    

    def __repr__(self):
        return f"<Venue id: {self.id}, name: {self.name}, genres: {self.genres}>"


    # Implemented any missing fields like seeking_description, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False, server_default="{}")
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    """ Changed name as per this knowedge based question:
        https://knowledge.udacity.com/questions/545169
    """
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=db.backref('artist',lazy='joined'), cascade="all, delete")

    def __repr__(self) -> str:
        return f"<Artist id: {self.id}, name: {self.name}, genres: {self.genres}>"



    # Implemented any missing fields like seeking_description, as a database migration using Flask-Migrate

# Implemented Show and Artist models, and completed all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, primary_key=True)

