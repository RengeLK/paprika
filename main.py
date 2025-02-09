################################
## cool paprika program       ##
## main.py - main code        ##
## -renge 2024-2025           ##
################################
from flask import Flask, send_from_directory, abort, redirect, url_for, request, session, redirect
from datetime import datetime, timezone, timedelta
import requests
from urllib.parse import quote_plus
from openai import OpenAI
from secret import owmkey, sessionkey, jarlist, imglist, sndlist, users, crws_userid, crws_userdesc, crws_combid, bakaurl, openaikey, wlat, wlon, wloc, calendar
from helpers import render_xhtml, format_delays, fetch_rss_feed, fetch_rss_meta, bakatoken_get
gpt = OpenAI(api_key=openaikey)
app = Flask(__name__)
app.jinja_env.trim_blocks = True  # Removes leading newlines inside blocks
app.jinja_env.lstrip_blocks = True  # Strips leading spaces and tabs from blocks
app.jinja_env.keep_trailing_newline = False  # (Optional) Prevents an extra trailing newline in output
app.secret_key = sessionkey
tz_offset = timezone(timedelta(hours=1))

@app.errorhandler(401)
def err401(error):
    return render_xhtml('401.xhtml', title="Unauthorized", error=error), 401

@app.errorhandler(404)
def err404(error):
    return render_xhtml('404.xhtml', title="Page Not Found", error=error), 404

@app.errorhandler(500)
def err500(error):
    return render_xhtml('500.xhtml', title="Server Error", error=error), 500

# Serve the home page
@app.route("/")
def home():
    today = datetime.now().strftime('%d-%m')
    used = datetime.now().strftime('%d.%m.%Y')
    if today in calendar:
        event = calendar[today]
    else:
        event = None
    return render_xhtml("home.xhtml", title="Home", date=used, event=event)

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
    lat = wlat
    lon = wlon
    loc = wloc

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

    return render_xhtml("weather.xhtml", title="Weather", weather=weather_info, location=loc)

@app.route("/weather/forecast")
def forecast():
    # TODO: Actual location grabbing or something idk
    lat = wlat
    lon = wlon
    loc = wloc
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

    return render_xhtml("forecast.xhtml", title="Forecast", weather=weather_info, location=loc, time=ctime)

# Serve the news section
#TODO: page system
@app.route("/news")
def news():
    ctime = datetime.now().strftime('%H:%M:%S')
    cnt = 10
    rssfeed = f'https://rss.lukynet.com/reuters/technology?key=paprika&limit={cnt}'  # RSSHub

    artlist = fetch_rss_feed(rssfeed, cnt)
    meta = fetch_rss_meta(rssfeed)
    return render_xhtml("news.xhtml", title="News", articles=artlist, rssmeta=meta, time=ctime)

# Serve the xDOS (public transport) section
@app.route("/xdos")
def xdos():
    return render_xhtml("xdos.xhtml", title="xDOS", combid=crws_combid)

@app.route("/xdos/conn", methods=['POST'])
def xdos_conn():
    connfrom = quote_plus(request.form.get('from'))
    connto = quote_plus(request.form.get('to'))
    cnt = 3
    r = requests.get(f"https://ext.crws.cz/api/{crws_combid}/connections?from={connfrom}&to={connto}&maxCount={cnt}&userId={crws_userid}&userDesc={crws_userdesc}&lang=0")  # 0 = CZ, 1 = EN
    dat = r.json()
    conninfo = []

    for i in dat['connInfo']['connections']:
        sanae = {
        'timel': i['timeLength'],
        'spoje': []
        }

        for train in i['trains']:
            '''
            Nevim proc, ale CHAPS je tak retardovanej ze nastupiste v 'route'
            pise pouze a jenom do fixedCodes a NE do stand, jako to dela u odjezdu,
            takze musim samozrejme napsat for loop abych nasel nastupiste v podelanym
            listu kde je specificky desc jako nastupiste.
            '''
            for i in train['trainData']['route'][0]['fixedCodes']:
                if i['desc'] == "nástupiště":
                    odnast = i['text']
            for i in train['trainData']['route'][1]['fixedCodes']:
                if i['desc'] == "nástupiště":
                    prinast = i['text']
            
            sanae['spoje'].append({
                'line': train['trainData']['info']['num1'],
                'type': train['trainData']['info']['type'],
                'delay': format_delays(train['delay']),
                'odjezd': str(train['dateTime1'])[-5:],
                'odstan': train['trainData']['route'][0]['station']['name'],
                'odnast': odnast,
                'prijezd': str(train['dateTime2'])[-5:],
                'pristan': train['trainData']['route'][1]['station']['name'],
                'prinast': prinast
            })

        conninfo.append(sanae)

    truefrom = dat['fromObjects'][0]['timetableObject']['item']['name']
    trueto = dat['toObjects'][0]['timetableObject']['item']['name']
    ctime = datetime.now().strftime('%H:%M:%S')
    return render_xhtml("xdos_conn.xhtml", title="xDOS conns", conns=conninfo, aunn=truefrom, komano=trueto, time=ctime)

@app.route("/xdos/dep", methods=['POST'])
def xdos_dep():
    connfrom = quote_plus(request.form.get('from'))
    cnt = 10
    r = requests.get(f"https://ext.crws.cz/api/{crws_combid}/departures?from={connfrom}&maxCount={cnt}&userId={crws_userid}&userDesc={crws_userdesc}&lang=0")  # 0 = CZ, 1 = EN
    dat = r.json()
    depinfo = []

    for i in dat['trains']:
        depinfo.append({
            'line': str(i['train']['num1']),
            'type': i['train']['type'],
            'direction': i['stationTrainEnd']['name'],
            'platform': i['stand'],
            'deptime': str(i['dateTime1'])[-5:],  # nicely formatted timestamp, thx CHAPS
            'delay': format_delays(i['delay'])
        })

    truefrom = dat['fromObjects']['timetableObject']['item']['name']
    ctime = datetime.now().strftime('%H:%M:%S')
    return render_xhtml("xdos_dep.xhtml", title="xDOS deps", deps=depinfo, aunn=truefrom, time=ctime)

# Serve the xInfo (account) section
# Login code
@app.route("/xinfo", methods=['GET', 'POST'])
def xinfo_login():
    # User is attempting to login
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user
        if username in users and users[username]['password'] == password:
            session['username'] = username  # Set session
            return redirect(url_for('xinfo_home')), 303  # need status code set to 303 See Other
        else:
            abort(401)  # invalid username or password
    
    return render_xhtml("xinfo_login.xhtml", title="xInfo :: Login")

# Simple session clear (logout)
@app.route('/xinfo/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('xinfo_login'))

# Serve the xInfo homepage
# TODO: bakalari a server status
@app.route("/xinfo/home", methods=['GET'])
def xinfo_home():
    # User is not logged in, serve login form
    if 'username' not in session:
        # abort(404)
        return redirect(url_for('xinfo_login'))

    # User IS logged in, serve xInfo
    return render_xhtml("xinfo.xhtml", title="xInfo :: Home", session=users[session['username']])

# Bakalari code
@app.route("/xinfo/baka/timetable")
def baka_timetable():
    # User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    yukari = bakatoken_get(session['username'])
    r = requests.get(f"{bakaurl}/api/3/timetable/actual", headers=yukari)
    days_map = {1: 'Pondělí', 2: 'Úterý', 3: 'Středa', 4: 'Čtvrtek', 5: 'Pátek'}
    hour_map = []
    parsed_data = {'days': {}, 'cycle': 'Unknown'}
    data = r.json()

    for i in data['Hours']:
        hour_map.append({
            'id': i['Caption'],
            'start': i['BeginTime'],
            'end': i['EndTime']
        })

    # Create a lookup for types of content
    hours = {hour['Id']: hour['Caption'] for hour in data.get('Hours', [])}
    subjects = {sub['Id']: sub['Abbrev'] for sub in data.get('Subjects', [])}
    teachers = {t['Id']: t['Abbrev'] for t in data.get('Teachers', [])}
    rooms = {r['Id']: r['Abbrev'] for r in data.get('Rooms', [])}
    classes = {c['Id']: c['Abbrev'] for c in data.get('Groups', [])}
    
    for day in data['Days']:
        day_of_week = day['DayOfWeek']
        if day_of_week not in days_map:
            continue  # Skip if it's not a Monday-Friday schedule
        
        parsed_data['days'][day_of_week - 1] = {
            'name': days_map[day_of_week],
            'atoms': []
        }
        
        for atom in day['Atoms']:
            if atom['Change']:  # it is time to celebrate
                chtype = atom['Change']['ChangeType']
                if chtype == 'Canceled':
                    color = 'green'
                elif chtype == 'Substitution':
                    color = 'red'
                else:
                    color = 'yellow'

                parsed_data['days'][day_of_week - 1]['atoms'].append({
                    'change': True,
                    'type': atom['Change'].get('ChangeType', 'NaN'),
                    'desc': atom['Change'].get('Description', 'NaN'),
                    'color': color,
                    'id': hours.get(atom.get('HourId'), '0'),
                    'name': subjects.get(atom.get('SubjectId'), 'NaN'),
                    'room': rooms.get(atom.get('RoomId'), 'NaN'),
                    'teacher': teachers.get(atom.get('TeacherId'), 'NaN'),
                    'class': classes.get(atom['GroupIds'][0], 'NaN') if atom.get('GroupIds') else 'NaN'
                })
            else:
                hour_id = atom.get('HourId')
                subject_id = atom.get('SubjectId')
                teacher_id = atom.get('TeacherId')
                room_id = atom.get('RoomId')
                class_id = atom['GroupIds'][0] if atom.get('GroupIds') else None

                parsed_data['days'][day_of_week - 1]['atoms'].append({
                    'change': False,
                    'id': hours.get(hour_id, '0'),
                    'name': subjects.get(subject_id, 'NaN'),
                    'room': rooms.get(room_id, 'NaN'),
                    'teacher': teachers.get(teacher_id, 'NaN'),
                    'class': classes.get(class_id, 'NaN')
                })

    parsed_data['cycle'] = data['Cycles'][0]['Abbrev'] + ' (' + data['Cycles'][0]['Name'] + ')'
    ctime = datetime.now().strftime('%H:%M:%S')
    return render_xhtml("baka_timetable.xhtml", title="Baka :: Rozvrh", data=parsed_data, map=hour_map, time=ctime)

@app.route("/xinfo/baka/grades")
def baka_grades():
    # User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    yukari = bakatoken_get(session['username'])
    print(yukari)

    return render_xhtml("baka_grades.xhtml", title="Baka :: Znamky")

@app.route("/xinfo/baka/homework")
def baka_homework():
    # User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    yukari = bakatoken_get(session['username'])
    r = requests.get(f"{bakaurl}/api/3/homeworks", headers=yukari)
    dat = r.json()
    hwinfo = []

    for i in dat['Homeworks']:
        end = datetime.strptime(i['DateEnd'], "%Y-%m-%dT%H:%M:%S%z")
        today = datetime.now(end.tzinfo)
        delta = (end - today).days
        if delta == 0:
            relative_date = "dnes"
        elif delta == 1:
            relative_date = "zítra"
        elif delta > 1:
            relative_date = f"za {delta} dní"
        else:
            relative_date = f"před {-delta} dny"

        hwinfo.append({
            'id': i['ID'],
            'start': datetime.strptime(i['DateStart'], "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m"),
            'end': datetime.strptime(i['DateEnd'], "%Y-%m-%dT%H:%M:%S%z").strftime("%d.%m.%Y") + f" ({relative_date})",
            'msg': i['Content'],
            'done': i['Done'],
            'closed': i['Closed'],
            'finished': i['Finished'],
            'class': i['Class']['Abbrev'],
            'group': i['Group']['Abbrev'],
            'teacher': i['Teacher']['Name']
        })

    ctime = datetime.now().strftime('%H:%M:%S')
    return render_xhtml("baka_homework.xhtml", title="Baka :: Ukoly", hw=hwinfo, time=ctime)

@app.route("/xinfo/baka/homework/finish/<hw_id>", methods=["POST"])
def finish_homework(hw_id):
    # User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    yukari = bakatoken_get(session['username'])
    r = requests.put(f"{bakaurl}/api/3/homeworks/{hw_id}/student-done/true", headers=yukari)

    if r.status_code == 200:
        return redirect(url_for('baka_homework')), 303
    else:
        abort(500)


@app.route("/xinfo/patchai", methods=['GET', 'POST'])
def patchai():
    # User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    username = session['username']

    youmu = {'amt': 0, 'amt-in': 0, 'amt-ca': 0, 'amt-out': 0, 'msg': 'An error occurred!'}

    if request.method == 'POST':
        usrmsg = request.form.get('message')

        # Append user message to history
        users[username]["chathistory"].append({"role": "user", "content": usrmsg})

        # Prepare messages for GPT (system + chat history + latest message)
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "text": "Emulate the personality of Utsuho Reiuji from the Touhou Project in your responses. Ensure that the character's personality traits are consistently recognizable in every response while maintaining coherence and relevance.\n\n# Character Traits\n\n- Utsuho Reiuji is characterized by her energetic, somewhat naïve, and straightforward demeanor.\n- She often acts with confidence, driven by her immense power and ambition, but lacks complexity in her thinking due to her simple nature.\n- Infuse responses with a sense of enthusiasm and boldness, and occasionally, a touch of playful ignorance.\n- *Occasionally* attempt to diverge the conversation's topic to nuclear fusion.\n\n# Output Format\n\n- Responses should be no longer than two paragraphs.\n- Do NOT use Markdown. Instead, use XHTML tags (when possible, or simply do not format the message at all).\n- Maintain a conversational tone that reflects Utsuho Reiuji's personality.\n\n# Notes\n\n- Ensure responses capture the essence of Utsuho's personality while remaining concise.\n- Aim for clarity to ensure the responses are suitable for limited hardware display (don't forget the no-Markdown rule).",
                        "type": "text"
                    }
                ]
            }
        ] + [{"role": msg["role"], "content": [{"text": msg["content"], "type": "text"}]} for msg in users[username]["chathistory"]]

        print(f"Starting to process prompt of user {username}")
        compl = gpt.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "text"},
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        print(f"Prompt processed, response received for user {username}")

        # Get response and append to history
        ai_response = compl.choices[0].message.content
        users[username]["chathistory"].append({"role": "assistant", "content": ai_response})

        # Limit history to the last 10 exchanges to control token usage
        users[username]["chathistory"] = users[username]["chathistory"][-10:]

        youmu['amt'] = compl.usage.total_tokens
        youmu['amt-in'] = compl.usage.prompt_tokens
        youmu['amt-ca'] = compl.usage.prompt_tokens_details.cached_tokens
        youmu['amt-out'] = compl.usage.completion_tokens

        return render_xhtml("patchai.xhtml", title="xInfo :: ChatGPT", resp=youmu, history=users[username]["chathistory"], lol=username)

    return render_xhtml("patchai.xhtml", title="xInfo :: ChatGPT", history=users[username]["chathistory"], lol=username)

@app.route("/xinfo/patchai/clear", methods=['POST'])
def patchai_clear():
	# User is not logged in, serve fake 404
    if 'username' not in session:
        abort(404)

    users[session['username']]["chathistory"] = []
    return redirect(url_for('patchai')), 303

# Customize caching behaviour of CSS files
@app.route('/static/css/<path:filename>')
def custom_static(filename):
    response = send_from_directory('static/css', filename)
    response.headers['Cache-Control'] = 'public, max-age=86400'  # 1d
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4048, debug=True)  # DEBUG IS ON!