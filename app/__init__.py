from datetime import datetime, timedelta, UTC
import os

from dateutil.tz import gettz
from flask_bootstrap import Bootstrap5
from flask import Flask, flash, request, redirect, render_template, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
import timeago
from werkzeug.security import check_password_hash, generate_password_hash

from src.streeteasymonitor.database import Database

from .forms import SearchForm

from main import main


def create_app():
    paddaddy_base_url = 'https://paddaddy.app'
    offermate_lookup_api = 'https://offermate.app/unit_lookup'

    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    db = Database()

    # Configuration
    class FlaskConfig:
        SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')

        # Require ADMIN_PASSWORD to be set explicitly
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if not admin_password:
            raise ValueError(
                'ADMIN_PASSWORD environment variable must be set. '
                'Add it to your .env file or set it in your deployment configuration.'
            )
        ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH') or generate_password_hash(admin_password)

    app.config.from_object(FlaskConfig())

    # Initialize rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'

    # Simple User class for single-user authentication
    class User(UserMixin):
        def __init__(self, id):
            self.id = id

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == app.config['ADMIN_USERNAME']:
            return User(user_id)
        return None

    @app.template_filter()
    def usd(value):
        """Format value as USD."""
        return f'${int(value):,}'

    @app.template_filter()
    def format_datetime(created_at):
        """Format date and time for current timezone."""
        local_tz = gettz()
        now = datetime.now(local_tz)
        parsed = datetime.fromisoformat(created_at).replace(tzinfo=UTC).astimezone()

        time_ago = timeago.format(parsed, now)

        date_formatted = parsed.strftime('%B %e, %Y')
        time_formatted = parsed.strftime('%l:%M %p')
        datetime_formatted = f'{date_formatted} {time_formatted}'

        return time_ago if now - parsed < timedelta(hours=8) else datetime_formatted
    
    @app.route('/login', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if (username == app.config['ADMIN_USERNAME'] and
                check_password_hash(app.config['ADMIN_PASSWORD_HASH'], password)):
                user = User(username)
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page if next_page else url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'success')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def dashboard():
        """Dashboard home page with statistics and recent listings."""
        all_listings = db.get_listings_sorted()

        # Calculate statistics
        total_listings = len(all_listings)
        recent_listings = [l for l in all_listings[:10]]  # Last 10

        # Calculate average price if there are listings
        avg_price = sum(l['price'] for l in all_listings) / total_listings if total_listings > 0 else 0

        # Get unique neighborhoods
        neighborhoods = set(l['neighborhood'] for l in all_listings if l['neighborhood'])

        stats = {
            'total_listings': total_listings,
            'avg_price': avg_price,
            'neighborhoods_count': len(neighborhoods),
            'recent_count': len(recent_listings)
        }

        return render_template('dashboard.html', stats=stats, recent_listings=recent_listings)

    @app.route('/search', methods=['GET', 'POST'])
    @login_required
    @limiter.limit("5 per minute")
    def search():
        """Search page with form."""
        form = SearchForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                kwargs = {
                    field.name: field.data or field.default
                    for field in form
                    if field.name != 'csrf_token' and field.name != 'submit'
                }
                session['data'] = kwargs

                try:
                    main(**kwargs)
                    flash('Search completed successfully!', 'success')
                    return render_template('table.html', listings=db.get_listings_sorted())
                except ValueError as e:
                    flash(f'Validation error: {str(e)}', 'danger')
                    return redirect(url_for('search'))
                except Exception as e:
                    flash(f'Search failed: {str(e)}', 'danger')
                    return redirect(url_for('search'))

            flash('Invalid form submission', 'danger')
            return redirect(url_for('search'))

        data = session.pop('data', None)

        return render_template(
            'search.html',
            listings=db.get_listings_sorted(),
            form=SearchForm(data=data),
        )

    @app.route('/listings')
    @login_required
    def listings():
        """View all listings with filtering options."""
        all_listings = db.get_listings_sorted()

        # Get filter parameters
        neighborhood = request.args.get('neighborhood')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        # Apply filters
        filtered_listings = all_listings
        if neighborhood:
            filtered_listings = [l for l in filtered_listings if l['neighborhood'] == neighborhood]
        if min_price is not None:
            filtered_listings = [l for l in filtered_listings if l['price'] >= min_price]
        if max_price is not None:
            filtered_listings = [l for l in filtered_listings if l['price'] <= max_price]

        # Get unique neighborhoods for filter dropdown
        all_neighborhoods = sorted(set(l['neighborhood'] for l in all_listings if l['neighborhood']))

        return render_template(
            'listings.html',
            listings=filtered_listings,
            all_neighborhoods=all_neighborhoods,
            current_neighborhood=neighborhood,
            current_min_price=min_price,
            current_max_price=max_price
        )
    

    @app.route('/<path:url>', methods=['GET'])
    @login_required
    def url_redirect(url):
        """Redirect to paddaddy or original listing URL."""
        # Validate URL to prevent open redirect
        if not url.startswith('http'):
            url = 'https://' + url

        # Only allow StreetEasy URLs
        if 'streeteasy.com' not in url:
            flash('Invalid URL - only StreetEasy links are allowed', 'danger')
            return redirect(url_for('dashboard'))

        try:
            params = {'q': url}
            r = requests.get(offermate_lookup_api, params=params, timeout=5)
            json = r.json()
            if (
                json.get('matching_listings')
                and json['matching_listings'][0]['similarity_type'] == 'exact_match'
            ):
                paddaddy_id = json['matching_listings'][0]['url']
                redirect_url = paddaddy_base_url + paddaddy_id
            else:
                redirect_url = url
        except Exception as e:
            print(f'Error: {e}')
            redirect_url = url

        return redirect(redirect_url, code=302)

    return app
