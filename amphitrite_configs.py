import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = BASE_DIR.replace("/cws/op", "http://wa-vw-er")
DATABASE_URL = "sqlite:///wave_data.sqlite" 