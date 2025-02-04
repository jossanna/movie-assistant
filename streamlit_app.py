import pandas as pd
import streamlit as st
from get_just_watch import load_just_watch_data
from get_user_watchlist import get_watchlist_data
from get_letterboxd_data import scrape_letterboxd_data

st.title("Movie Assistant")

st.write("## What movie should I watch?")

username = "ossanna"


@st.cache_data
def load_tmdb_data():
    tmdb_data = pd.read_pickle("data/tmdb.pkl", compression="gzip")
    tmdb_data["poster_path"] = (
        "https://www.themoviedb.org/t/p/w1280" + tmdb_data["poster_path"]
    )
    return tmdb_data


watchlist_data = get_watchlist_data(username)

tmdb_data = load_tmdb_data()

watchlist_letterboxd_data = []

for item in watchlist_data:
    watchlist_letterboxd_data.append(scrape_letterboxd_data(item))


watchlist_letterboxd_data_df = pd.DataFrame(watchlist_letterboxd_data)
watchlist_letterboxd_data_df["tmdb_id"] = watchlist_letterboxd_data_df[
    "tmdb_id"
].astype(int)

watchlist_letterboxd_data_df = pd.merge(
    watchlist_letterboxd_data_df,
    tmdb_data,
    left_on="tmdb_id",
    right_on="id",
    how="left",
)

offers_data = []
for tmdb_id, title in zip(
    watchlist_letterboxd_data_df["tmdb_id"], watchlist_letterboxd_data_df["title"]
):
    data = load_just_watch_data(str(tmdb_id), title)
    if data:
        offers_data.extend(data)


offers_data_df = pd.DataFrame(offers_data)

offers_data_df = offers_data_df.loc[
    offers_data_df["monetization_type"] == "FLATRATE"
].drop_duplicates(subset=["deeplink_url"])

offer_dict = (
    offers_data_df.groupby("tmdb_id_just_watch")["package_clear_name"]
    .agg(list)
    .to_dict()
)

watchlist_letterboxd_data_df["offers"] = (
    watchlist_letterboxd_data_df["tmdb_id"].astype(str).map(offer_dict)
)

st.write("## Watchlist")


st.dataframe(
    watchlist_letterboxd_data_df.loc[:, ["title", "poster_path", "offers"]],
    column_config={
        "title": "Movie Title",
        "poster_path": st.column_config.ImageColumn("Poster", width="large"),
        "offers": st.column_config.ListColumn("Offers"),
        "rating": st.column_config.NumberColumn("Rating", format="%d%%"),
    },
    hide_index=True,
    width="large",
)
