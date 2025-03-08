################################
## cool paprika program       ##
## helpers.py - helper funcs  ##
## -renge 2024-2025           ##
################################
from flask import render_template, make_response
import feedparser
import xmltodict
import requests
from datetime import datetime
from time import mktime, time
from secret import users, bakaurl
bakalogurl = f"{bakaurl}/api/login"

# Format the response correctly
def render_xhtml(template_name, **context):
    resp = make_response(render_template(template_name, **context))
    resp.headers['X-Bara'] = 'pica'
    resp.content_type = 'application/xhtml+xml'
    # resp.headers['Cache-Control'] = 'public, max-age=60'  # 1m
    resp.headers['Cache-Control'] = 'no-cache'  # cache but revalidate
    return resp

# Format delays
def format_delays(delay):
    if delay == -1:
        yuuka = "neznámé"
    elif delay == -2:
        yuuka = "nelze zjistit"
    else:
        yuuka = str(delay) + ' min'
    return yuuka

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

def parse_cap(url, geocode):
    tenshi = []
    r = requests.get(url)
    if r.status_code != 200:
        return None
    
    cap_data = xmltodict.parse(r.content)
    alert = cap_data.get('alert', {})
    info_blocks = alert.get('info', [])
    if isinstance(info_blocks, dict):
        info_blocks = [info_blocks]
    
    for info in info_blocks:
        event = info.get('event', '')
        areas = info.get('area')

        # Only process Czech info blocks
        if info.get('language') != 'cs':
            continue
        # Filter out event-less block (Žádný/Žádná/Žádné)
        if event.startswith('Žádn'):
            continue
        
        # Check if any area in the info block has the requested geocode
        found_geocode = False
        if areas:
            # Normalize to list
            areas = areas if isinstance(areas, list) else [areas]
            for area in areas:
                geocodes = area.get('geocode', [])
                geocodes = geocodes if isinstance(geocodes, list) else [geocodes]
                for gc in geocodes:
                    if gc.get('value') == geocode:
                        found_geocode = True
                        break
                if found_geocode:
                    break
        if not found_geocode:
            continue

        if info.get('onset'):
            onset = datetime.fromisoformat(info.get('onset')).strftime('%d/%m/%Y %H:%M')
        else:
            onset = "an unknown date"
        if info.get('expires'):
            expires = datetime.fromisoformat(info.get('expires')).strftime('%d/%m/%Y %H:%M')
        else:
            expires = "an unknown date"
        
        # Append all the event data
        tenshi.append({
            "event": event,
            "response": info.get('responseType'),
            "urgency": info.get('urgency'),
            "severity": info.get('severity'),
            "certainty": info.get('certainty'),
            "start": onset,
            "end": expires,
            "description": info.get('description'),
            "instruction": info.get('instruction')
        })

    return tenshi

############################
##  Bakalari functions!!  ##
############################

# Function to check if bakatoken is still valid
def bakatoken_validate(user_data):
    return user_data["bakatoken"] and time() < user_data["bakatimeout"]

# Function to refresh bakatoken
def bakatoken_refresh(user_data):
    if not user_data["bakarefresh"]:
        return False  # No refresh token available

    data = {
        "client_id": "ANDR",
        "grant_type": "refresh_token",
        "refresh_token": user_data["bakarefresh"]
    }

    response = requests.post(bakalogurl, data=data)
    if response.status_code == 200:
        token_data = response.json()
        user_data["bakatoken"] = token_data["access_token"]
        user_data["bakarefresh"] = token_data["refresh_token"]
        user_data["bakatimeout"] = time() + token_data.get("expires_in", 3599)
        return True
    return False

# Function to perform full login
def bakalogin(user_data):
    data = {
        "client_id": "ANDR",
        "grant_type": "password",
        "username": user_data["bakauser"],
        "password": user_data["bakapass"]
    }

    response = requests.post(bakalogurl, data=data)
    if response.status_code == 200:
        token_data = response.json()
        user_data["bakatoken"] = token_data["access_token"]
        user_data["bakarefresh"] = token_data["refresh_token"]
        user_data["bakatimeout"] = time() + token_data.get("expires_in", 3599)
        return True
    return False

# Main function to get a valid token
def bakatoken_get(user_id):
    user_data = users.get(user_id)
    if not user_data:
        return None  # User not found

    # Try refresh token first
    if bakatoken_validate(user_data) or bakatoken_refresh(user_data):
        return {"Authorization": f"Bearer {user_data["bakatoken"]}"}
    # If refresh fails, do a full login
    elif bakalogin(user_data):
        return {"Authorization": f"Bearer {user_data["bakatoken"]}"}

    return None  # Login failed