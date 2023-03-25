from os.path import dirname, realpath, join

CURR_PATH = dirname(realpath(__file__))

LOGIN_API = 'https://apis.googolplex.live/api/auth/signin'
DOWNLOAD_API = "https://apis.googolplex.live/api/drive/download"
SEARCH_API = 'https://apis.googolplex.live/api/movies/search' # add keyword at the end e.g. search/the%20vampire
HOME_API = "https://apis.googolplex.live/api/tvSeries/fetchSeriesDetails/home"

FETCH_TV_SERIES_API = "https://apis.googolplex.live/api/tvSeries/fetchSeriesDetails"
FETCH_MOVIE_API = "https://apis.googolplex.live/api/movies/getAll"

log_file_name = "bot_logs.log"
ENV_PATH = join(CURR_PATH, '.env')

DEVELOPER_CHAT_ID = 757002673
DATA_FILE_NAME = 'data.json'
INFO_FILE_NAME = 'info.json'