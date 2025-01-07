import streamlit as st

st.set_page_config(page_title="Movie Assistant", page_icon="🎬", layout="wide")

st.title("🎬 Movie Assistant")

st.write("""
Welcome to Movie Assistant! This app helps you discover and track movies to watch.

### Features:
- 📋 View and manage your Letterboxd watchlist
- 🎯 Get personalized movie recommendations
- 🎦 Find where to stream your favorite movies
""")

st.sidebar.success("Select a feature above.")
