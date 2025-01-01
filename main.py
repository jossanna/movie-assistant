import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment variable
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("TMDB_API_KEY not found in environment variables")


# Load TMDB data from API
def load_tmdb_data():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data["results"])


tmdb_data = load_tmdb_data()

print(tmdb_data.head())
