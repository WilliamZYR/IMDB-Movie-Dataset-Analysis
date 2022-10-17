import urllib.request
from bs4 import BeautifulSoup
import re

import sqlite3

url = 'https://www.imdb.com/chart/top?ref_=tt_awd'
html = urllib.request.urlopen(url).read()
soup = BeautifulSoup(html, 'html.parser')
tags = soup('a')
ID = []
movies = []
directors = []

for line in tags:
    url = line.get('href', None)
    ID.append(url)
    movie_name = re.findall('\(dir.\), .*">(.*)</a>', str(line))
    movies.extend(movie_name)
    dir_name = re.findall('title="(.*) \(dir.\)', str(line))
    directors.extend(dir_name)
ID = ID[48:548:2]

AllUser = []
Age_under_18 = []
Age_18_29 = []
Age_30_44 = []
Age_45_plus = []

Males = []
male_under_18 = []
male_18_29 = []
male_30_44 = []
male_45_plus = []

Females = []
female_under_18 = []
female_18_29 = []
female_30_44 = []
female_45_plus = []

demographic = [AllUser, Age_under_18, Age_18_29, Age_30_44, Age_45_plus, Males, male_under_18, male_18_29, male_30_44, male_45_plus, Females, female_under_18, female_18_29, female_30_44, female_45_plus]
index = [31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47]

for id in ID:
    url = 'https://www.imdb.com' + id + 'ratings/?ref_=tt_ov_rt'
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    datas = soup('td')
    for i in range(15):
        n = index[i]
        rating = re.findall('<div class="bigcell">(.*)</div>', str(datas[n]))
        demographic[i].extend(rating)

Ratings = []
for lists in demographic:
    Ratings.append([float(i) for i in lists])

for rating in Ratings:
    print(rating)


conn = sqlite3.connect('imdb250.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Movies;
DROP TABLE IF EXISTS Directors;

CREATE TABLE Movies (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name            TEXT UNIQUE,
    director_id     INTEGER,
    AllUser         FLOAT,
    Age_under_18    FLOAT,
    Age_18_29       FLOAT,
    Age_30_44       FLOAT,
    Age_45_plus     FLOAT,
    Males           FLOAT,
    male_under_18   FLOAT,
    male_18_29      FLOAT,
    male_30_44      FLOAT,
    male_45_plus    FLOAT,
    Females         FLOAT,
    female_under_18 FLOAT,
    female_18_29    FLOAT,
    female_30_44    FLOAT,
    female_45_plus  FLOAT
);

CREATE TABLE Directors (
    id     INTEGER NOT NULL PRIMARY KEY UNIQUE,
    name   TEXT UNIQUE
);
''')

for i in range(250):
    movie = movies[i]
    director = directors[i]
    cur.execute('INSERT OR IGNORE INTO Directors (name) VALUES ( ? )', (director,))
    cur.execute('SELECT id FROM Directors WHERE name = ? ', (director,))
    director_id = cur.fetchone()[0]

    cur.execute('''INSERT INTO Movies (name, director_id, AllUser, Age_under_18, Age_18_29, Age_30_44, Age_45_plus, Males, male_under_18, male_18_29, male_30_44, male_45_plus, Females, female_under_18, female_18_29, female_30_44, female_45_plus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (movie, director_id, Ratings[0][i], Ratings[1][i], Ratings[2][i], Ratings[3][i], Ratings[4][i], Ratings[5][i], Ratings[6][i], Ratings[7][i], Ratings[8][i], Ratings[9][i], Ratings[10][i], Ratings[11][i], Ratings[12][i], Ratings[13][i], Ratings[14][i]))
    conn.commit()
