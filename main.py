##########################
## cool paprika program ##
## main.py - req parts  ##
## -renge 2024          ##
##########################
from flask import Flask, render_template, send_from_directory, abort, redirect, make_response, url_for, request, session, redirect
from datetime import datetime
from time import mktime
import requests
import feedparser
from secret import owmkey, sessionkey, jarlist, imglist, sndlist, users
app = Flask(__name__)
app.secret_key = sessionkey

############## Helper functions ##############

# Format data from RSS feeds for display
def fetch_rss_feed(url, cnt):
    feed = feedparser.parse(url)
    articles = []
    marisa = cnt

    for entry in feed.entries:
        if marisa == 0:
            break
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary if "summary" in entry else "",
            "published": datetime.fromtimestamp(int(mktime(entry.published_parsed))).strftime('%d/%m/%Y %H:%M:%S') if "published_parsed" in entry else "an unknown date"  # I am sorry for creating this monstrosity
        })
        marisa -= 1
    return articles

def fetch_rss_meta(url):
    d = feedparser.parse(url)
    meta = {
        'title': d.feed.title,
        'date': datetime.fromtimestamp(int(mktime(d.feed.updated_parsed))).strftime('%d/%m/%Y %H:%M:%S')
    }
    return meta

# Format the response correctly
def render_xhtml(template_name, **context):
    resp = make_response(render_template(template_name, **context))
    resp.headers['X-Bara'] = 'pica'
    resp.content_type = 'application/xhtml+xml'
    return resp

############## Content ##############

@app.errorhandler(404)
def err404(error):
    return render_template('404.xhtml'), 404

@app.errorhandler(500)
def err500(error):
    return render_template('500.xhtml'), 500

# Serve the home page
@app.route("/")
def home():
    return render_xhtml("home.xhtml", title="Home")

# Serve the downloads section
@app.route("/downloads")
def downloads():
    return render_xhtml("dlindex.xhtml", title="Downloads")

@app.route("/dls/java")
def dljars():
    return render_xhtml("dljars.xhtml", title="Java ME DLs", list=jarlist)

@app.route("/dls/img")
def dlimg():
    return render_xhtml("dlimg.xhtml", title="Wallpaper DLs", list=imglist)

@app.route("/dls/snd")
def dlsnd():
    return render_xhtml("dlsnd.xhtml", title="Sound DLs", list=sndlist)

# Serve the weather section
@app.route("/weather")
def weather():
    # TODO: Actual location grabbing or something idk
    lat = str(50.0874654)
    lon = str(14.4212535)
    loc = 'Gensokyo'

    get = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={owmkey}&units=metric")
    air = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={owmkey}")
    dat = get.json()

    weather_info = {
        'main': dat['weather'][0]['main'],
        'condition': dat['weather'][0]['description'],
        'icon': dat['weather'][0]['icon'],
        'temp': str(dat['main']['temp']) + '°C',
        'feels': str(dat['main']['feels_like']) + '°C',
        'pressure': str(dat['main']['pressure']) + ' hPa',
        'humidity': str(dat['main']['humidity']) + '%',
        'visibility': str(dat['visibility']) + 'm',
        'wind': str(dat['wind']['speed']) + ' m/s',
        'direct': str(dat['wind']['deg']) + '°',
        'clouds': str(dat['clouds']['all']) + '%',
        'aqi': air.json()['list'][0]['main']['aqi'],
        'reqdate': datetime.fromtimestamp(dat['dt']).strftime('%H:%M:%S'),  # unix timestamp of data calculation
        'sunrise': datetime.fromtimestamp(dat['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.fromtimestamp(dat['sys']['sunset']).strftime('%H:%M')
    }

    return render_template("weather.xhtml", title="Weather", weather=weather_info, location=loc)

@app.route("/forecast")
def forecast():
    # TODO: Actual location grabbing or something idk
    lat = str(50.0874654)
    lon = str(14.4212535)
    loc = 'Gensokyo'
    ctime = datetime.now().strftime('%H:%M:%S')
    cnt = 8  # amount of forecast data in timestamps (3-hour difference, 8 equals 24hrs of data)

    get = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={owmkey}&units=metric&cnt={cnt}")
    dat = get.json()
    
    weather_info = []
    for i in dat['list']:
        weather_info.append({
            'main': i['weather'][0]['main'],
            'condition': i['weather'][0]['description'],
            'icon': i['weather'][0]['icon'],
            'temp': str(i['main']['temp']) + '°C',
            'feels': str(i['main']['feels_like']) + '°C',
            'pressure': str(i['main']['pressure']) + ' hPa',
            'humidity': str(i['main']['humidity']) + '%',
            'wind': str(i['wind']['speed']) + ' m/s',
            'direct': str(i['wind']['deg']) + '°',
            'clouds': str(i['clouds']['all']) + '%',
            'prop': str(int(i['pop'] * 100)) + '%',
            'foretime': datetime.fromtimestamp(i['dt']).strftime('%H:%M')  # forecast data time
        })

    return render_template("forecast.xhtml", title="Forecast", weather=weather_info, location=loc, time=ctime)

# Serve the news section
@app.route("/news")
def news():
    ctime = datetime.now().strftime('%H:%M:%S')
    cnt = 10
    respecttheaya = 'https://bunbunmaru.news/rss'
    rssfeed = f'https://rss.lukynet.com/reuters/technology?key=paprika&limit={cnt}'

    artlist = fetch_rss_feed(rssfeed, cnt)
    meta = fetch_rss_meta(rssfeed)
    return render_template("news.xhtml", title="News", articles=artlist, rssmeta=meta, time=ctime)

# Serve the xDOS (public transport) section (NOT IMPLEMENTED)
@app.route("/xdos")
def xdos():
    return 'not implemented yet'

# Serve the xInfo (account) section (NOT IMPLEMENTED)
# TODO: bakalari a server status idk
@app.route("/xinfo", methods=['GET', 'POST'])
def xinfo():
    # User is attempting to login
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user
        if username in users and users[username]['password'] == password:
            session['username'] = username  # Set session
            return redirect(url_for('xinfo'))
        else:
            abort(401)  # invalid username or password

        session['username'] = request.form['username']
        return redirect(url_for('index'))
    
    # User is not logged in, serve login form
    if 'username' not in session:
        return render_template("login.xhtml", title="xInfo login")

    # User IS logged in, serve xInfo
    return render_template("xinfo.xhtml", title="xInfo", session=session)
    
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('xinfo'))


# Customize caching behaviour of CSS files
@app.route('/static/css/<path:filename>')
def custom_static(filename):
    response = send_from_directory('static/css', filename)
    response.headers['Cache-Control'] = 'public, max-age=86400'  # 1d
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4040, debug=True)  # DEBUG IS ON!