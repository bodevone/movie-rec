from django.shortcuts import render
import os
from django.conf import settings
import csv
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from surprise import Reader, Dataset, SVD, KNNBasic, accuracy

metadata_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv/smd.csv')

# Create your views here.
def main_page(request):
    if request.method == 'POST':
        movie_search = request.POST.get('movie_search')
        search_data = search(movie_search, "like")
        return render(request, 'main.html', {'data': search_data})

    data = {"status":"like"}
    movies = {}
    with open(metadata_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(row)
            if line_count != 0:
                if float(row[11]) < 17:
                    continue
                temp = {"imdb_id":row[7], "original_title":row[9], "poster_path":"https://image.tmdb.org/t/p/w600_and_h900_bestv2" + row[12]}
                movies[line_count] = temp
            if line_count == 20:
                break
            line_count += 1
    data["movies"] = movies

    # print(data)
    return render(request, 'main.html', {'data': data})


def dislike_page(request):
    if request.method == 'POST':
        movie_search = request.POST.get('movie_search')
        search_data = search(movie_search, "dislike")
        return render(request, 'main.html', {'data': search_data})

    data = {"status":"dislike"}
    movies = {}
    with open(metadata_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                if float(row[11]) > 15:
                    continue
                temp = {"imdb_id":row[7], "original_title":row[9], "poster_path":"https://image.tmdb.org/t/p/w600_and_h900_bestv2" + row[12]}
                movies[line_count] = temp
            if line_count == 10:
                break
            line_count += 1
    data["movies"] = movies

    # print(data)
    return render(request, 'main.html', {'data': data})

def result_page(request, m1, m2, m3, dm1, dm2, dm3):
    movies = movie_predict(m1, m2, m3, dm1, dm2, dm3)
    return render(request, 'result.html', {'movies': movies})

def search(movie, status):
    data = {"status": status}
    movies = {}
    with open(metadata_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            print(movie, row[9])
            if movie.lower() in row[9].lower():
                temp = {"imdb_id":row[7], "original_title":row[9], "poster_path":"https://image.tmdb.org/t/p/w600_and_h900_bestv2" + row[12]}
                movies[line_count] = temp
                line_count += 1

            if line_count == 20:
                break
    data["movies"] = movies
    return data


def movie_predict(movie1, movie2, movie3, movie4, movie5, movie6):
    # print("MOVIES YOU LIKE")
    # print(m1, m2, m3)
    # print("MOVIES YOU DONT LIKE")
    # print(dm1, dm2, dm3)
    links_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv/links_small.csv')
    ratings_path = os.path.join(settings.STATICFILES_DIRS[0], 'csv/ratings_small.csv')


    smd = pd.read_csv(metadata_path)


    count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
    count_matrix = count.fit_transform(smd['soup'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    smd = smd.reset_index()
    titles = smd['title']
    indices = pd.Series(smd.index, index=smd['title'])


    def convert_int(x):
        try:
            return int(x)
        except:
            return np.nan

    id_map = pd.read_csv(links_path)[['movieId', 'tmdbId']]
    id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
    id_map.columns = ['movieId', 'id']
    id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')
    indices_map = id_map.set_index('id')

    id_map.to_csv("id_map.csv")

    reader = Reader()
    ratings = pd.read_csv(ratings_path)

    try:
        id1 = list(id_map.loc[movie1]['movieId'])[0]
    except:
        id1 = id_map.loc[movie1]['movieId']
    try:
        id2 = list(id_map.loc[movie2]['movieId'])[0]
    except:
        id2 = id_map.loc[movie2]['movieId']
    try:
        id3 = list(id_map.loc[movie3]['movieId'])[0]
    except:
        id3 = id_map.loc[movie3]['movieId']
    try:
        id4 = list(id_map.loc[movie4]['movieId'])[0]
    except:
        id4 = id_map.loc[movie4]['movieId']
    try:
        id5 = list(id_map.loc[movie5]['movieId'])[0]
    except:
        id5 = id_map.loc[movie5]['movieId']
    try:
        id6 = list(id_map.loc[movie6]['movieId'])[0]
    except:
        id6 = id_map.loc[movie6]['movieId']

    newdata = pd.DataFrame({"userId":[0,0,0,0,0,0],"movieId":[id1,id2,id3,id4,id5,id6],"rating":[5.0,5.0,5.0,1.0,1.0,1.0],"timestamp":[1260759131,1260759131,1260759131,1260759131,1260759131,1260759131]})
    ratings = ratings.append(newdata)

    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    testset = trainset.build_testset()
    predictions = algo.test(testset)

    favs = [movie1,movie2,movie3]
    movie_indices = []

    for title in favs:

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

    movies_dic = {}


    line_count = 0

    for mov in arr:
        with open(metadata_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if mov == row[9]:
                    temp = {"imdb_id":row[7], "original_title":row[9], "poster_path":"https://image.tmdb.org/t/p/w600_and_h900_bestv2" + row[12]}
                    movies_dic[line_count] = temp
                    line_count += 1
                    break
    return movies_dic
