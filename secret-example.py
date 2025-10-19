sessionkey = "somerandomlongstringthatlovesbeingchanged"  # used for encrypting session cookies
port = 4048  # port number used by the Flask server
bakaurl = "https://bakalari.tss.cz/"  # api url for bakalari (xInfo)
stravacode = 1234  # Strava.cz place code
rssfeed = "https://rss.example.com/?limit=10"  # RSS feed in use for news section

owmkey = "8634fds683f43dfs468"  # OpenWeatherMap API key
openaikey = "sk-proj-letsgogambling!"  # OpenAI API key
openaimodel = "gpt-4o-mini"  # Name of used OpenAI LLM
openaiprompt = "You are a helpful assistant."  # OpenAI 'developer' prompt incl. in each request
openainame = "Assistant"  # Name of assistant in patchai (display purposes only)

crws_userid = "GHB4534FDG-GFHGB45GH5D4HG"  # needed for xDOS
crws_userdesc = "cz.mafra.jizdnirady"
crws_combid = "PID"  # combination id as defined in CRWS docs

wlat = 0  # GPS latitude for weather
wlon = 0  # GPS longitude for weather
wloc = 'Null Island'  # Displayed name of weather location
woffset = 0  # Timezone offset for weather, used sometimes
capurl = "https://example.com/cap.xml"  # URL for CAP alerts
capgeo = "69420"  # Geocode for CAP alerts

jarlist = [  # manual list of all jars present in /dls/java
    {'name': 'Test game', 'uri': 'test.jad'}
]
imglist = [  # same but img
    {'name': 'Test wallpaper (176x220)', 'uri': 'test.png'}
]
sndlist = [  # same but snd
    {'name': 'Test ringtone (.mid, 0:53)', 'uri': 'test.mid'}
]

users = {  # used by xInfo auth
    "admin9": {
        "password": "cirnoIZdaBEST",
        "gptallow": False,  # Allow access to /xinfo/patchai
        ## Bakalari ##
        "bakauser": "paveln9c",
        "bakapass": "jsemretard69",
        ## Strava ##
        "stravauser": "john.doe",
        "stravapass": "extremelyinsecure",
        ## DO NOT CHANGE ##
        ## THE FOLLOWING ##
        ##    SETTINGS   ##
        "chathistory": [],  # OpenAI chat history
        "bakatoken": None,
        "bakarefresh": None,
        "bakatimeout": 0
    }
}

calendar = {  # used on the home page to display EoTD
    "09-09": {  # dd-mm
        'name': 'Cirno Day',
        'desc': 'The strongest day of the year!'
    }
}