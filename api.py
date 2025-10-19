################################
## cool paprika program       ##
## api.py - API backend       ##
## -renge 2025                ##
################################
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import feedparser
from time import mktime
from flask import request, abort
from secret import owmkey, users, wlat, wlon, calendar, rssfeed, bakaurl
from __main__ import app, astro, xdos_conn, xdos_dep
from helpers import render_api, dict_to_element, fetch_rss_feed, bakatoken_get

@app.route('/api')
def api_home():
    today = datetime.now().strftime('%d-%m')
    used = datetime.now().strftime('%d.%m.%Y')
    if today in calendar:
        event = calendar[today]
    else:
        event = None

    # Create root
    home = ET.Element("home")
    ET.SubElement(home, "date").text = used

    # Add event
    eve = ET.SubElement(home, "event")
    if event: dict_to_element(eve, event)

    # Convert to string
    xml_str = ET.tostring(home, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)


@app.route('/api/wtr')
def api_weather():
    get = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={wlat}&lon={wlon}&appid={owmkey}&units=metric")
    air = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={wlat}&lon={wlon}&appid={owmkey}")
    ctime = datetime.now().strftime('%H:%M:%S')
    frr = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={wlat}&lon={wlon}&appid={owmkey}&units=metric&cnt=8")

    dat = get.json()
    current = {
        'main': dat['weather'][0]['main'],
        'sec': dat['weather'][0]['description'],
        'icon': dat['weather'][0]['icon'],
        'temp': str(dat['main']['temp']),
        'feels': str(dat['main']['feels_like']),
        'pressure': str(dat['main']['pressure']),
        'wind': str(dat['wind']['speed']),
        'windir': str(dat['wind']['deg']),
        'clouds': str(dat['clouds']['all']),
        'aqi': str(air.json()['list'][0]['main']['aqi']),
        'sunrise': datetime.fromtimestamp(dat['sys']['sunrise']).strftime('%H:%M'),
        'sunset': datetime.fromtimestamp(dat['sys']['sunset']).strftime('%H:%M')
    }

    dat = frr.json()
    forecast = []
    for i in dat['list']:
        forecast.append({
            'icon': i['weather'][0]['icon'],
            'temp': str(i['main']['temp']),
            'feels': str(i['main']['feels_like']),
            'clouds': str(i['clouds']['all']),
            'foretime': datetime.fromtimestamp(i['dt']).strftime('%H:%M')  # forecast data time
        })

    nitori: dict = astro(True)
    for i, j in nitori.items():
        nitori[i] = str(j)

    # Create root
    wtr = ET.Element("weather")
    ET.SubElement(wtr, "time").text = ctime

    # Add info
    cur = ET.SubElement(wtr, "current")
    dict_to_element(cur, current)
    base = ET.SubElement(wtr, "forecast")
    for i in forecast:
        new = ET.SubElement(base, "iter")
        dict_to_element(new, i)
    ast = ET.SubElement(wtr, "moon")
    dict_to_element(ast, nitori)

    # Convert to string
    xml_str = ET.tostring(wtr, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)


@app.route('/api/news')
def api_news():
    artlist = fetch_rss_feed(rssfeed, 10, True)
    d = feedparser.parse(rssfeed)

    nws = ET.Element("news")
    ET.SubElement(nws, "title").text = d.feed.title
    ET.SubElement(nws, "date").text = datetime.fromtimestamp(int(mktime(d.feed.updated_parsed))).strftime('%H:%M')
    lol = ET.SubElement(nws, "articles")
    for i in artlist:
        new = ET.SubElement(lol, "iter")
        dict_to_element(new, i)

    xml_str = ET.tostring(nws, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)

@app.route('/api/xdos/conn')
def api_conn():
    frm = request.args.get('from')
    to = request.args.get('to')
    snae = xdos_conn(True, frm, to)

    con = ET.Element("conns")
    for i in snae:
        new = ET.SubElement(con, "conn")
        dict_to_element(new, i)

    xml_str = ET.tostring(con, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)

@app.route('/api/xdos/deps')
def api_deps():
    frm = request.args.get('from')
    snae = xdos_dep(True, frm)

    con = ET.Element("deps")
    ET.SubElement(con, "time").text = datetime.now().strftime("%H:%M")
    for i in snae:
        new = ET.SubElement(con, "iter")
        dict_to_element(new, i)

    xml_str = ET.tostring(con, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)


@app.route('/api/baka/grades')
def api_grades():
    token = request.args.get('token')
    user = None
    for i, j in users.items():
        if token == j["apitoken"]:
            user = i
    if not user:
        abort("401")

    yukari = bakatoken_get(user)
    r = requests.get(f"{bakaurl}/api/3/marks", headers=yukari)
    dat = r.json()
    chimata = []

    for s in dat['Subjects']:
        for i in s['Marks']:
            if i['IsNew']:  # only append new marks
                chimata.append({
                    'date': datetime.strptime(i['MarkDate'], "%Y-%m-%dT%H:%M:%S%z").strftime("%d/%m"),
                    'caption': i['Caption'],
                    'mark': i['MarkText'],
                    'weight': str(i['Weight']),
                    'class': s['Subject']['Abbrev']
                })

    grd = ET.Element("grades")
    for i in chimata:
        new = ET.SubElement(grd, "grade")
        dict_to_element(new, i)

    xml_str = ET.tostring(grd, encoding="utf-8").decode("utf-8")
    return render_api(xml_str)


# TODO: baka timetable