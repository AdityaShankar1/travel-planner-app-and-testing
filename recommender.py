import polars as pl
import pandas as pd

# Load datasets
spotify_path = "/Users/adityashankar/Downloads/spotify.csv"
tourism_path = "/Users/adityashankar/Downloads/IndiaTourism.csv"

spotify_df = pl.read_csv(spotify_path)
tourism_df = pd.read_csv(tourism_path)

# Simple mapping: genre → place type
GENRE_TO_PLACE = {
    "acoustic": "Nature",
    "pop": "City",
    "rock": "Adventure",
    "classical": "Heritage",
    "jazz": "Relaxation",
    "hip hop": "Urban"
}

def recommend_places(genre: str, n: int = 5):
    """Recommend Indian destinations based on selected music genre."""
    place_type = GENRE_TO_PLACE.get(genre.lower(), "Nature")
    subset = tourism_df[tourism_df["Type"].str.contains(place_type, case=False, na=False)]
    if subset.empty:
        subset = tourism_df.sample(n)
    return subset.sample(min(n, len(subset)))
