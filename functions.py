from variables import HOME_API, ENV_PATH, SEARCH_API, FETCH_TV_SERIES_API, DOWNLOAD_API, FETCH_MOVIE_API
from browser import Browser, Response
from requests.utils import requote_uri

from logging_module import logger

smily_emoji = "\U0001f642"
shushing_emoji = "\U0001F92B"


def get_token_links(tokenless_links: list, session: Browser) -> list:
    return [link+session.headers['Authorization'].replace('Bearer ', '') for link in tokenless_links]


def is_valid_token(session: Browser) -> Response:
    return session.get(HOME_API) # Check the status of cached token


def update_token(session: Browser) -> bool:
    response = session.get_new_token()
    if response.ok:
        return True
    logger.info(response.json())
    return False

    
def search_in_plex(session: Browser, keyword: str) -> Response:
    prepared_url: str = f'{SEARCH_API}/{requote_uri(keyword)}'
    return session.get(prepared_url)


def fetch_series(session: Browser, tv_id: int) -> Response:
    prepared_url: str = f'{FETCH_TV_SERIES_API}/{tv_id}'
    return session.get(prepared_url)


def fetch_movie(session: Browser, movie_id: int) -> Response:
    prepared_url: str = f'{FETCH_MOVIE_API}/{movie_id}'
    return session.get(prepared_url)


def extract_links_from_response(response_obj: Response, quality: str) -> dict:
    seasons = response_obj.json()['seasons'][quality.rstrip('p')]
    data = {} # store data extracted from response json
    for season in seasons:
        episodes = seasons[season]["episodes"] #List of episodes[dict] in current season
        data[season] = [f'{DOWNLOAD_API}/{episode["name"]}?id={episode["_id"]}&token=' for episode in episodes]
    return data

def get_movie(response_obj: Response) -> dict:
    response: dict = response_obj.json()
    file_data = []
    for file in response['files']:
        size = round(int(file.get('size')) / 1073741824, 2) # to convert it into GB
        movie_url = f'{DOWNLOAD_API}/{file["name"]}?id={file["_id"]}&token=' # Add token later
        movie_links_data = {
            'quality': file.get('quality'),
            'size': size,
            'language': file.get('language'),
            'link': movie_url
        }
        file_data.append(movie_links_data)
    movie_data = {
        'poster_path': response.get('poster_path'),
        'overview': response.get('overview'),
        'title': response.get('title'),
        'release_date': response.get('release_date'),
        'link_data': file_data
    }
    return movie_data