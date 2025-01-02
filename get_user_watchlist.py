from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import requests

load_dotenv()


def parse_watchlist_page(html):
    soup = BeautifulSoup(html, "lxml")
    watchlist_movies = soup.findAll("li", attrs={"class": "poster-container"})

    movie_ids = []
    for movie in watchlist_movies:
        movie_id = movie.find("div", attrs={"class": "film-poster"})[
            "data-target-link"
        ].split("/")[-2]
        movie_ids.append(movie_id)
    return movie_ids


def get_user_watchlist(username, num_pages):
    url = f"https://letterboxd.com/{username}/watchlist/page/{{}}/"

    all_movie_ids = []
    for i in range(num_pages):
        response = requests.get(url.format(i + 1))
        if response.ok:
            page_ids = parse_watchlist_page(response.text)
            all_movie_ids.extend(page_ids)

    return all_movie_ids


def get_page_count(username):
    url = f"https://letterboxd.com/{username}/watchlist"
    soup = BeautifulSoup(requests.get(url).text, "lxml")

    if "error" in soup.find("body").get("class", []):
        return -1

    try:
        return int(
            soup.findAll("li", attrs={"class": "paginate-page"})[-1]
            .find("a")
            .text.replace(",", "")
        )
    except IndexError:
        return 1


def get_watchlist_data(username):
    num_pages = get_page_count(username)
    if num_pages == -1:
        return []

    result = get_user_watchlist(username, num_pages)
    return result


if __name__ == "__main__":
    username = os.getenv("LETTERBOXD_USERNAME")
    if not username:
        raise ValueError("LETTERBOXD_USERNAME not found in environment variables")
    get_watchlist_data(username)
