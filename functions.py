from variables import HOME_API, ENV_PATH, SEARCH_API, FETCH_TV_SERIES, DOWNLOAD_API
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


def fetch_series(session: Browser, tv_id: str) -> Response:
    prepared_url: str = f'{FETCH_TV_SERIES}/{tv_id}'
    return session.get(prepared_url)


def extract_links_from_response(response_obj: Response, quality: str) -> dict:
    seasons = response_obj.json()['seasons'][quality.rstrip('p')]
    data = {} # store data extracted from response json
    for season in seasons:
        episodes = seasons[season]["episodes"] #List of episodes[dict] in current season
        data[season] = [f'{DOWNLOAD_API}/{episode["name"]}?id={episode["_id"]}&token=' for episode in episodes]
    return data