import os

NUMBA_CACHE_DIR = '/tmp/numba_cache'

BASE_DIR = "/app/amphitrite"
BASE_URL = "http://127.0.0.1:8000"
DATABASE_URL = "sqlite:///wave_data.sqlite" 

# Base URL for the iframe and image sources
BASE_URL_GHPLOTS = "http://wa-vw-er.bom.gov.au/webapps/vwave/plots/"
BASE_URL_IMAGES = os.path.join(BASE_URL, "plots/spectral/")  
BASE_URL_TABLES = os.path.join(BASE_URL, "transformer/tables/")  

# model data directories
MODEL_DATA_DIR = os.path.join(BASE_DIR, "model_data")
PLOT_DIR = os.path.join(BASE_DIR, "plots")