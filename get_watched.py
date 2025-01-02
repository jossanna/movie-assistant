from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_page_count(username):
    url = f"https://letterboxd.com/{username}/films/by/date"
    r = requests.get(url)

    soup = BeautifulSoup(r.text, "lxml")

    body = soup.find("body")

    try:
        if "error" in body["class"]:
            return -1, None
    except KeyError:
        print(body)
        return -1, None

    try:
        page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
        num_pages = int(page_link.find("a").text.replace(",", ""))
        display_name = (
            body.find("section", attrs={"class": "profile-header"})
            .find("h1", attrs={"class": "title-3"})
            .text.strip()
        )
    except IndexError:
        num_pages = 1
        display_name = None

    return num_pages, display_name


def parse_ratings_page(page):
    soup = BeautifulSoup(page, "lxml")
    films = soup.find_all("li", attrs={"class": "poster-container"})
    film_data = []
    for film in films:
        film_data.append(film.find("div").get("data-target-link"))
    return film_data


def get_watched_films(username, num_pages=None):
    url = f"https://letterboxd.com/{username}/films/by/date/page/{{}}"

    if not num_pages:
        num_pages = get_page_count(username)

    all_films = []
    for i in range(num_pages):
        page_url = url.format(i + 1)
        response = requests.get(page_url)
        if response.ok:
            films = parse_ratings_page(response.text)
            all_films.extend(films)

    return all_films


def get_user_data(username):
    num_pages, display_name = get_page_count(username)

    if num_pages == -1:
        return []

    user_films = get_watched_films(username, num_pages=num_pages)

    return user_films


if __name__ == "__main__":
    username = os.getenv("LETTERBOXD_USERNAME")
    watched_films = get_user_data(username)
