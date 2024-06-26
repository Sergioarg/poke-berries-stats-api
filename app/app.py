""" Main API of Berries Stats"""
from os import getenv, path
from flask import Flask, jsonify, render_template, Blueprint
from flask_caching import Cache

from .berries.berry_data_fetcher import BerryDataFetcher
from .berries.berry_statistics import BerryStatistics
from .berries.histogram_generator import HistogramGenerator

# Confurations constans
ALL_BERRY_STATS_PATH = 'allBerryStats'
API_HOST = getenv("API_HOST", "127.0.0.1")
API_PORT = getenv("API_PORT", "5000")

# Initilization of flask and blueprints
app = Flask(__name__, static_folder='static')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
berries_bp = Blueprint(name=ALL_BERRY_STATS_PATH, import_name=__name__)


@app.route('/', methods=['GET'])
def base_endpoint():
    """ Base endpoint of the API """
    api_path = f"{API_HOST}:{API_PORT}/api/v1/{ALL_BERRY_STATS_PATH}/"

    response = {
        "message": "Poke-berries statistics API",
        "version": "1.0",
        "endpoints": {
            "berries": api_path,
            "histogram": f"{api_path}/histogram"
        }
    }
    return jsonify(response)


@berries_bp.route('/', methods=['GET'])
@cache.cached(timeout=50)
def get_all_berries_stats():
    """ Endpoint to get all berries statistics """

    berry_statistics = BerryStatistics(BerryDataFetcher())
    response = berry_statistics.get_stats()

    return jsonify(response)


@berries_bp.route('/histogram')
def histogram_view():
    """ Endpoint to get the histogram of berries """

    if not path.exists(path="/app/static/imgs/histogram.png"):
        berry_statistics = BerryStatistics(BerryDataFetcher())
        histogram_generator = HistogramGenerator(berry_statistics)
        histogram_generator.generate_histogram()

    return render_template(template_name_or_list='histogram.html')

# Register Blueprint in app
app.register_blueprint(blueprint=berries_bp, url_prefix=f'/api/v1/{ALL_BERRY_STATS_PATH}')

if __name__ == '__main__':
    app.run(host=API_HOST, port=API_PORT)
