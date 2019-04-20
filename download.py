import requests
import re
import sqlite3

conn = sqlite3.connect('music.sqlite3')

#updateCoverPictures()
def updateCoverPictures():
    cur = conn.cursor()
    # class MyOpener(urllib.FancyURLopener):
    #     version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    # myopener = MyOpener()
    cur.execute('SELECT movie, url, cover from Movies')
    for row in cur:
        movie = row[0]
        url = row[1]
        if row[2] == None:
            print("Working on ", movie)
            content = requests.get(url)
            try:
                cover = re.findall('<img data-retina="" src="(.+?)"',content)[0]
                cur1 = conn.cursor()
                cur1.execute('UPDATE Movies SET cover=? WHERE movie=?',(cover,movie))
                conn.commit()
            except:
                print("Error Fetching Cover photo of ",movie)

# getAllSongsList()
def getAllSongsList():
    cur = conn.cursor()
    # class MyOpener(urllib.FancyURLopener):
    #     version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    # myopener = MyOpener()
    try:
        cur.execute('select * from Songs')
    except:
        print("Creating Songs Table")
        cur.execute('CREATE TABLE Songs (song_id INTEGER PRIMARY KEY AUTOINCREMENT, movie_id INTEGER, song TEXT, url TEXT, UNIQUE(movie_id,song), FOREIGN KEY (movie_id) REFERENCES Movies(movie_id))')
    cur.execute('SELECT * FROM Movies')
    for row in cur:
        movie = row[0]
        movieNm = row[1]
        url = row[2]
        print("Working on ",movieNm,"...")
        cur1 = conn.cursor()
        cur1.execute('SELECT song FROM Songs WHERE movie_id = ?',(movie,))
        if not cur1.fetchone():
            content = requests.get(url)
            links = re.findall('<td class="songs-bitrate-1"><i class="fa fa-music"></i>(.+?)<em>',content.text)
            for link in links:
                try:
                    songURL = re.findall('<a href="(.+?)"',link)[0]
                    songName = re.findall('>(.+?)<',link)[0]
                    print(movie,songName,songURL)
                    cur1.execute('INSERT or IGNORE INTO Songs (movie_id,song,url) VALUES (?,?,?)',(movie,songName,songURL))
                    cover = re.findall('<img data-retina="" src="(.+?)"',content)[0]
                    cur1.execute('UPDATE Movies SET cover=? WHERE movie_id=?',(cover,movie))
                except:
                    pass
            conn.commit()
            
# getAllMoviesList
def getAllMoviesList():
    cur = conn.cursor()
    try:
        cur.execute('select * from Movies')
    except:
        print("Creating Movies Table")
        cur.execute('CREATE TABLE Movies (movie_id INTEGER PRIMARY KEY AUTOINCREMENT, movie TEXT, url TEXT, cover TEXT)')
    movies = list()
    pages = ['0-9', 'A', 'B', 'C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    # class MyOpener(urllib.FancyURLopener):
    #     version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'
    # myopener = MyOpener()
    for page in pages:
        print("Started List for ", page)
        url = 'https://www.songspk.run/indian_movie/'+page+'_List.html'
        content = requests.get(url)
        tags = re.findall('<li class="list">.*?</li>',content.text)
        print("Processing Tags for", page)
        for tag in tags:
            movieName = re.findall('<a href=".*?">(.*?)</a>',tag)[0]
            link = re.findall('<a href="(.*?)">',tag)[0]
            movies.append((movieName,link))

    print("Writing to Database")
    for movie in movies:
        cur.execute('SELECT movie FROM Movies WHERE movie=?',(movie[0],))
        if not (cur.fetchone()):
            cur.execute('INSERT INTO Movies (movie,url) VALUES (?,?)', movie)
    print("Commiting")
    conn.commit()
    return

#Main Program
choice=99
print("\n1. Download/Refresh Movie Data\n2. Download/Refresh Songs Data\n3. Download Cover Pictures\nEnter Choice:")
try:
    choice = int(input())
    if(choice>3):
        print("Wrong Input\nExiting...")
except Exception:
    print("Enter Integer.\nExiting...")

if(choice == 1):
    getAllMoviesList()
if(choice == 2):
    getAllSongsList()
if(choice == 3):
    updateCoverPictures()
