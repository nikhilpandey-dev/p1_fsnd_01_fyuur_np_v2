#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cgitb import text
from curses import meta
from distutils.log import error
import json
from unicodedata import name
from wsgiref import validate
import dateutil.parser
import babel
# Implemented as per the suggestions of the Udacity reviewer.
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify
    )
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from helpers import sqlalchemy_config
from datetime import datetime
from flask_migrate import Migrate
from models import db, Venue, Artist, Show
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Replaced with real venues data.
    locals = []
    venues = db.session.query(Venue).all()
    places = db.session.query(Venue).distinct(Venue.city, Venue.state).all()
    for place in places:
        locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
    return render_template('pages/venues.html', areas=locals);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Implemented search on venues with partial string search. Ensured it is case-insensitive.

    search_term = request.form.get('search_term', '').lower()
    result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(result),
        "data": result
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
    venue = db.session.query(Venue).get_or_404(venue_id)
    print("Type of Genres is: ", type(venue.genres))
    upcoming_shows = []
    past_shows = []
    for show in venue.shows:
        temp_show = {
            'artist_id': show.artist_id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)
    # object class to dictionary
    venue_data = vars(venue)
    # Add additional fields to the dictionary
    venue_data['past_shows'] = past_shows
    venue_data['upcoming_shows'] = upcoming_shows
    venue_data['past_shows_count'] = len(past_shows)
    venue_data['upcoming_shows_count'] = len(upcoming_shows)
    return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # Inserts form data as a new Venue record in the db
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
          venue = Venue(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        address=form.address.data,
                        phone=form.phone.data,
                        genres=request.form.getlist('genres'),
                        facebook_link=form.facebook_link.data,
                        image_link=form.image_link.data,
                        website=form.website_link.data,
                        seeking_talent=form.seeking_talent.data,
                        seeking_description=form.seeking_description.data
                        )
          db.session.add(venue)
          db.session.commit()
          # on successful db insert, flashes success
          flash('Venue ' + request.form['name'] + ' was successfully listed!')
      except ValueError as e:
          print(e)
          db.session.rollback()
          # on unsuccessful db insert, flash success
          flash('Venue ' + request.form['name'] + ' was unsuccessful and could not be listed!')
      finally:
          db.session.close()
          
          
  else:
      message = []
      for field, errors in form.errors.items():
          error_message = f"{field}: {errors}"
          message.append(error_message)
             
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Completed this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    db.session.query(Venue).filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Real data returned from querying the database
  real_artists_data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=real_artists_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implements search on artists with partial string search.
    search_term = request.form.get('search_term', '').lower()
    results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {
        "count": len(results),
        "data": results
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
    artist = db.session.query(Artist).get_or_404(artist_id)
    past_shows = list(filter(lambda x: x.start_time < datetime.today(), artist.shows))
    upcoming_shows = list(filter(lambda x: x.start_time >= datetime.today(), artist.shows))
    upcoming_shows = []
    past_shows = []
    for show in artist.shows:
        temp_show = {
            'venue_id': show.venue_id,
            'venue_name': show.venue.name,
            'venue_image_link': show.venue.image_link,
            'start_time': show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if show.start_time <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)
    
    artist_data = vars(artist)
    artist_data['past_shows'] = past_shows
    artist_data['upcoming_shows'] = upcoming_shows
    artist_data['past_shows_count'] = len(past_shows)
    artist_data['upcoming_shows_count'] = len(upcoming_shows)
    
    return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = db.session.query(Artist).filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artist)
    # Populates form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # Takes values from the form submitted, and update existing artist data
    artist = db.session.query(Artist).filter_by(id=artist_id).first_or_404()
    form = ArtistForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            artist.name=form.name.data
            artist.city=form.city.data
            artist.state=form.state.data
            artist.phone=form.phone.data
            artist.genres=request.form.getlist('genres')
            artist.facebook_link=form.facebook_link.data
            artist.image_link=form.image_link.data
            artist.website=form.website_link.data
            artist.seeking_venue=form.seeking_venue.data
            artist.seeking_description=form.seeking_description.data
            db.session.commit()
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully edited!')
        except ValueError as e:
            print(e)
            db.session.rollback()
            # on unsuccessful db insert, flash success
            flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
        finally:
            db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.query(Venue).filter_by(id=venue_id).first_or_404()
    form = VenueForm(obj=venue)
    # Populates form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # Take values from the form submitted, and update existing
    venue = db.session.query(Venue).filter_by(id=venue_id).first_or_404()
    form = VenueForm(request.form, meta={'csrf': False})
    if form.validate():
        try:
            venue.name=form.name.data
            venue.city=form.city.data
            venue.state=form.state.data
            venue.address=form.address.data
            venue.phone=form.phone.data
            venue.genres=request.form.getlist('genres')
            venue.facebook_link=form.facebook_link.data
            venue.image_link=form.image_link.data
            venue.website=form.website_link.data
            venue.seeking_talent=form.seeking_talent.data
            venue.seeking_description=form.seeking_description.data
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + request.form['name'] + ' was successfully edited and updated!')
        except ValueError as e:
            print(e)
            db.session.rollback()
            # on unsuccessful db insert, flash failures
            flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited and updated.')
        finally:
            db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  # Inserted form data as a new Venue record in the db, instead
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Inserts form data as a new Venue record in the db
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
      try:
          artist = Artist(name=form.name.data,
                        city=form.city.data,
                        state=form.state.data,
                        phone=form.phone.data,
                        genres=request.form.getlist('genres'),
                        facebook_link=form.facebook_link.data,
                        image_link=form.image_link.data,
                        website=form.website_link.data,
                        seeking_venue=form.seeking_venue.data,
                        seeking_description=form.seeking_description.data
                        )
          db.session.add(artist)
          db.session.commit()
          # on successful db insert, flash success
          flash('Artist ' + request.form['name'] + ' was successfully listed!')
      except ValueError as e:
          print(e)
          db.session.rollback()
          # on unsuccessful db insert, flash failures
          flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
          db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = db.session.query(Show).all()
  show_data = []
  for show in shows:
      data_dict = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
      }
      
      show_data.append(data_dict)
  return render_template('pages/shows.html', shows=show_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  venues = db.session.query(Venue).all()
  artists = db.session.query(Artist).all()
  form = ShowForm(venues=venues, artists=artists)
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # creates new shows in the db, upon submitting new show listing form
    venues = db.session.query(Venue).all()
    artists = db.session.query(Artist).all()
    form = ShowForm(request.form, meta={'csrf': False}, venues=venues, artists=artists)
    if form.validate():
        try:
            created_show = Show()
            form.populate_obj(created_show)
            db.session.add(created_show)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except ValueError as e:
            print(e)
            db.session.rollback()
            # on unsuccessful db insert, flash failures
            flash('Show could not be listed.')
        finally:
            db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
