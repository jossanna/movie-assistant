import kagglehub
import os
import glob
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up Kaggle credentials from environment variables
kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

if not kaggle_username or not kaggle_key:
    raise ValueError("Kaggle credentials not found in environment variables")

os.environ["KAGGLE_USERNAME"] = kaggle_username
os.environ["KAGGLE_KEY"] = kaggle_key

# Create data directory if it doesn't exist
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# Download latest version
download_path = kagglehub.dataset_download(
    "asaniczka/tmdb-movies-dataset-2023-930k-movies"
)

# Find CSV file in the download directory
csv_files = glob.glob(os.path.join(download_path, "**", "*.csv"), recursive=True)

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {download_path}")

# Use the first CSV file found
source_path = csv_files[0]
print(f"Found CSV file: {source_path}")

# Read CSV and save as pickle
df = pd.read_csv(source_path)
pickle_path = os.path.join(data_dir, "tmdb.pkl")
df.to_pickle(pickle_path, compression="gzip")
