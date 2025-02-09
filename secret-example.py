sessionkey = "somerandomlongstringthatlovesbeingchanged"  # used for encrypting session cookies
bakaurl = "https://bakalari.spse4.cz/"  # api url for bakalari (xInfo)

owmkey = "8634fds683f43dfs468"  # OpenWeatherMap API key
openaikey = "sk-proj-letsgogambling!"  # OpenAI API key
astroid = "bla-bla-bla"  # AstronomyAPI app ID
astrokey = "TRHRHIONONBDGFO"  # AstronomyAPI app key

crws_userid = "GHB4534FDG-GFHGB45GH5D4HG"  # needed for xDOS
crws_userdesc = "cz.mafra.jizdnirady"
crws_combid = "PID"  # combination id as defined in CRWS docs

wlat = 0  # GPS latitude for weather
wlon = 0  # GPS longitude for weather
wele = 0  # Elevation for weather in meters
wloc = 'Null Island'  # Displayed name of weather location

jarlist = [  # manual list of all jars present in /dls/java
    {'name': 'Test game', 'uri': 'test.jar'}
]
imglist = [  # same but img
    {'name': 'Test wallpaper (176x220)', 'uri': 'test.png'}
]
sndlist = [  # same but snd
    {'name': 'Test ringtone (.mid, 0:53)', 'uri': 'test.mid'}
]

users = {  # used by xInfo auth
    "admin9": {
        "username": "admin9",  # This NEEDS to be identical to the previous line
        "password": "cirnoIZdaBEST",
        "gptallow": False,  # Allow access to /xinfo/patchai
        "gamallow": False,  # Allow gambling
        ## Bakalari ##
        "bakauser": "paveln9c",
        "bakapass": "jsemretard69",
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