import csv

from django.shortcuts import render
from django.conf import settings

from .helpers import get_movie_data_from_row
from .predict import movie_predict


def main_page(request):
    if request.method == 'POST':
        movie_text = request.POST.get('movie_text')
        search_data = search_movie(movie_text)
        return render(request, 'main.html', {'data': search_data})

    movies = {}
    with open(settings.METADATA_PATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                if float(row[11]) < 17:
                    continue
                movie_data = get_movie_data_from_row(row)
                movies[line_count] = movie_data
            if line_count == 20:
                break
            line_count += 1
    return render(request, 'main.html', {'movies': movies})


def result_page(request, movie_1, movie_2, movie_3):
    movies = movie_predict(movie_1, movie_2, movie_3)
    return render(request, 'result.html', {'movies': movies})


def search_movie(movie_text):
    movies = {}
    with open(settings.METADATA_PATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            if movie_text.lower() in row[9].lower():
                movie_data = get_movie_data_from_row(row)
                movies[line_count] = movie_data
                line_count += 1
            if line_count == 20:
                break
    return movies
