POSTER_URL = 'https://image.tmdb.org/t/p/w600_and_h900_bestv2'
IMDB_ID = 7
ORIGINAL_TITLE_ID = 9
POSTER_PATH_ID = 12


def get_movie_data_from_row(row):
    return {
        'imdb_id': row[IMDB_ID], 'original_title': row[ORIGINAL_TITLE_ID],
        'poster_path': POSTER_URL + row[POSTER_PATH_ID]
    }


def get_movie_id_from_id_map(id_map, movie):
    try:
        movie_id = list(id_map.loc[movie]['movieId'])[0]
    except:
        movie_id = id_map.loc[movie]['movieId']
    return movie_id

