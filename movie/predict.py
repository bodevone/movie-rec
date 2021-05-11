import csv

import numpy
import pandas
from django.conf import settings
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset, SVD

from .helpers import get_movie_data_from_row, get_movie_id_from_id_map


def movie_predict(movie_1, movie_2, movie_3):
    smd = pandas.read_csv(settings.METADATA_PATH)

    count = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
    count_matrix = count.fit_transform(smd['soup'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    smd = smd.reset_index()
    indices = pandas.Series(smd.index, index=smd['title'])

    def convert_int(x):
        try:
            return int(x)
        except:
            return numpy.nan

    id_map = pandas.read_csv(settings.LINKS_PATH)[['movieId', 'tmdbId']]
    id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
    id_map.columns = ['movieId', 'id']
    id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')
    indices_map = id_map.set_index('id')

    reader = Reader()
    ratings = pandas.read_csv(settings.RATINGS_PATH)

    id_1 = get_movie_id_from_id_map(id_map, movie_1)
    id_2 = get_movie_id_from_id_map(id_map, movie_2)
    id_3 = get_movie_id_from_id_map(id_map, movie_3)

    new_ratings = pandas.DataFrame({
        'userId': [0, 0, 0], 'movieId': [id_1, id_2, id_3],
        'rating': [5.0, 5.0, 5.0],
    })
    ratings = ratings.append(new_ratings)

    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    liked_movies = [movie_1, movie_2, movie_3]
    movie_indices = []

    for title in liked_movies:
        try:
            idx = list(indices[title])[0]
        except:
            idx = indices[title]

        sim_scores = list(enumerate(cosine_sim[int(idx)]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:26]
        movie_indices += [i[0] for i in sim_scores if i[0] not in movie_indices]

    movies = smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]
    movies['est'] = movies['id'].apply(lambda x: algo.predict(0, indices_map.loc[x]['movieId']).est)
    movies = movies.sort_values('est', ascending=False)
    arr = movies['title'][:11]

    predicted_movies = {}
    line_count = 0
    for mov in arr:
        with open(settings.METADATA_PATH) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if mov == row[9]:
                    movie_data = get_movie_data_from_row(row)
                    predicted_movies[line_count] = movie_data
                    line_count += 1
                    break
    return predicted_movies
