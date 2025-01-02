import requests
import pandas as pd

url = "https://apis.justwatch.com/graphql"

# GraphQL query as a string


def get_just_watch_data(search_term):
    query = """
        query GetSuggestedTitles(
        $country: Country!
        $language: Language!
        $first: Int!
        $filter: TitleFilter
        ) {
        popularTitles(country: $country, first: $first, filter: $filter) {
            edges {
            node {
                ...SuggestedTitle
                ... on MovieOrShowOrSeason {
                objectType
                objectId
                offerCount(country: $country, platform: WEB)
                offers(country: $country, platform: WEB) {
                    monetizationType
                    elementCount
                    retailPriceValue
                    retailPrice(language: $language)
                    currency
                    standardWebURL
                    deeplinkURL(platform: WEB)
                    presentationType
                    package {
                    id
                    packageId
                    clearName
                    icon
                    }
                }
                }
            }
            }
        }
        }

        fragment SuggestedTitle on MovieOrShow {
        id
        objectType
        objectId
        content(country: $country, language: $language) {
            fullPath
            title
            originalReleaseYear
            posterUrl
            externalIds {
            imdbId
            tmdbId
            }
            scoring {
            imdbScore
            imdbVotes
            tmdbPopularity
            tmdbScore
            }
        }
        }
    """

    variables = {
        "country": "DE",
        "language": "de",
        "first": 12,
        "filter": {"searchQuery": search_term},
    }

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://www.justwatch.com",
        "Referer": "https://www.justwatch.com/",
    }

    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"]["popularTitles"]["edges"]

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Response content: {response.text}")
        return None


def get_just_watch_data_for_tmdb_id(tmdb_id, movie_title):
    """
    Get JustWatch data for a specific movie by TMDB ID.

    Args:
        tmdb_id: TMDB ID of the movie
        movie_title: Title of the movie to search for

    Returns:
        Dictionary containing movie data if found, None otherwise
    """
    data = get_just_watch_data(movie_title)
    if not data:
        return None

    for item in data:
        try:
            if str(item["node"]["content"]["externalIds"]["tmdbId"]) == str(tmdb_id):
                return item
        except (KeyError, TypeError):
            continue

    return None


def load_just_watch_data(tmdb_id, movie_title):
    data = get_just_watch_data_for_tmdb_id(tmdb_id, movie_title)

    if not data or "node" not in data:
        return None

    try:
        # movie_data = {
        #     "title_just_watch": data["node"]["content"] ["title"],
        #     "year_just_watch": data["node"]["content"]["originalReleaseYear"],
        #     "poster_url_just_watch": data["node"]["content"]["posterUrl"],
        #     "imdb_id_just_watch": data["node"]["content"]["externalIds"]["imdbId"],
        #     "tmdb_id_just_watch": data["node"]["content"]["externalIds"]["tmdbId"],
        #     "imdb_score_just_watch": data["node"]["content"]["scoring"]["imdbScore"],
        #     "imdb_votes_just_watch": data["node"]["content"]["scoring"]["imdbVotes"],
        #     "tmdb_popularity_just_watch": data["node"]["content"]["scoring"][
        #         "tmdbPopularity"
        #     ],
        #     "tmdb_score_just_watch": data["node"]["content"]["scoring"]["tmdbScore"],
        # }

        offers_data = []
        for offer in data["node"]["offers"]:
            offers_data.append(
                {
                    "tmdb_id_just_watch": data["node"]["content"]["externalIds"][
                        "tmdbId"
                    ],
                    "monetization_type": offer["monetizationType"],
                    "element_count": offer["elementCount"],
                    "retail_price_value": offer["retailPriceValue"],
                    "retail_price": offer["retailPrice"],
                    "currency": offer["currency"],
                    "standard_web_url": offer["standardWebURL"],
                    "deeplink_url": offer["deeplinkURL"],
                    "presentation_type": offer["presentationType"],
                    "package_id": offer["package"]["id"],
                    "package_clear_name": offer["package"]["clearName"],
                    "package_icon": "https://images.justwatch.com"
                    + offer["package"]["icon"]
                    .replace("{profile}", "s100")
                    .replace("{format}", "png"),
                }
            )
        return offers_data

    except KeyError as e:
        print(f"Error parsing data: {e}")
        return None
