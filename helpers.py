################################
## cool paprika program       ##
## helpers.py - helper funcs  ##
## -renge 2024-2025           ##
################################
from flask import render_template, make_response
import feedparser
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