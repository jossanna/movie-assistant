import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_letterboxd_data(movie_url_id):
    url_base = f"https://letterboxd.com/film/{movie_url_id}/"
    url_stats = f"https://letterboxd.com/csi/film/{movie_url_id}/stats/"
    url_rating = f"https://letterboxd.com/csi/film/{movie_url_id}/rating-histogram/"

    response_base = requests.get(url_base, headers=header)
    soup_base = BeautifulSoup(response_base.content, "lxml")

    response_stats = requests.get(url_stats, headers=header)
    soup_stats = BeautifulSoup(response_stats.content, "lxml")

    response_rating = requests.get(url_rating, headers=header)
    soup_rating = BeautifulSoup(response_rating.content, "lxml")

    data_base = {
        "movie title": soup_base.find("meta", {"property": "og:title"})["content"],
        "rating": soup_base.find("meta", {"name": "twitter:data2"})["content"][:3]
        if soup_base.find("meta", {"name": "twitter:data2"})
        else "",
        "tmdb_id": soup_base.find("a", {"data-track-action": "TMDb"})["href"].split(
            "/"
        )[-2],
        "imdb_id": soup_base.find("a", {"data-track-action": "IMDb"})["href"].split(
            "/"
        )[-2],
    }

    data_stats = {
        "watch_count": int(
            re.search(
                r"Watched by ([\d,]+)",
                soup_stats.find("li", {"class": "filmstat-watches"}).find("a")["title"],
            )
            .group(1)
            .replace(",", "")
        ),
        "list_count": int(
            re.search(
                r"Appears in ([\d,]+)",
                soup_stats.find("li", {"class": "filmstat-lists"}).find("a")["title"],
            )
            .group(1)
            .replace(",", "")
        ),
        "like_count": int(
            re.search(
                r"Liked by ([\d,]+)",
                soup_stats.find("li", {"class": "filmstat-likes"}).find("a")["title"],
            )
            .group(1)
            .replace(",", "")
        ),
    }

    data_rating = {
        "0.5 stars ratings": soup_rating.find_all("li")[0]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "1.0 stars ratings": soup_rating.find_all("li")[1]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "1.5 stars ratings": soup_rating.find_all("li")[2]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "2.0 stars ratings": soup_rating.find_all("li")[3]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "2.5 stars ratings": soup_rating.find_all("li")[4]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "3.0 stars ratings": soup_rating.find_all("li")[5]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "3.5 stars ratings": soup_rating.find_all("li")[6]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "4.0 stars ratings": soup_rating.find_all("li")[7]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "4.5 stars ratings": soup_rating.find_all("li")[8]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
        "5.0 stars ratings": soup_rating.find_all("li")[9]
        .find("a")["title"]
        .split()[0]
        .replace(",", ""),
    }

    return pd.DataFrame([data_base | data_stats | data_rating])
