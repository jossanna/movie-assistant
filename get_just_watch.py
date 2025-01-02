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
        "first": 10,
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
        if item["node"]["content"]["externalIds"]["tmdbId"] == tmdb_id:
            return item
    return None


def load_just_watch_data(tmdb_id, movie_title):
    data = get_just_watch_data_for_tmdb_id(tmdb_id, movie_title)

    if not data or "node" not in data:
        return None, None

    try:
        df_movie = pd.DataFrame(
            {
                "title": [data["node"]["content"]["title"]],
                "year": [data["node"]["content"]["originalReleaseYear"]],
                "poster_url": [data["node"]["content"]["posterUrl"]],
                "imdb_id": [data["node"]["content"]["externalIds"]["imdbId"]],
                "tmdb_id": [data["node"]["content"]["externalIds"]["tmdbId"]],
                "imdb_score": [data["node"]["content"]["scoring"]["imdbScore"]],
                "imdb_votes": [data["node"]["content"]["scoring"]["imdbVotes"]],
                "tmdb_popularity": [
                    data["node"]["content"]["scoring"]["tmdbPopularity"]
                ],
                "tmdb_score": [data["node"]["content"]["scoring"]["tmdbScore"]],
            },
            index=[0],
        )

        df_offers = pd.DataFrame(
            {
                "monetization_type": [data["node"]["offers"][0]["monetizationType"]],
                "element_count": [data["node"]["offers"][0]["elementCount"]],
                "retail_price_value": [data["node"]["offers"][0]["retailPriceValue"]],
                "retail_price": [data["node"]["offers"][0]["retailPrice"]],
                "currency": [data["node"]["offers"][0]["currency"]],
                "standard_web_url": [data["node"]["offers"][0]["standardWebURL"]],
                "deeplink_url": [data["node"]["offers"][0]["deeplinkURL"]],
                "presentation_type": [data["node"]["offers"][0]["presentationType"]],
                "package_id": [data["node"]["offers"][0]["package"]["id"]],
                "package_clear_name": [
                    data["node"]["offers"][0]["package"]["clearName"]
                ],
                "package_icon": [data["node"]["offers"][0]["package"]["icon"]],
            }
        )

        return df_movie, df_offers

    except KeyError as e:
        print(f"Error parsing data: {e}")
        return None, None
