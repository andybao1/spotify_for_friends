import requests
import time
import boto3
import json

def getRefreshToken ():
    code = 'AQA9N1TQZDWLBtwcn-KB2zJ2Zjlhxs7f67Gpp3Drmos6_AAdcfQSeg0-CGbjdEI4-Ti6PrFkkc2CW1rLK5uPeyej9BI3Zh_24XZbwTYSSOebr0EJzsYucBYEcrQ-bWr0-vAF9emNXp7w0gYmD9Ed-Rht40Ii0iKzEvP-Bd0wl2hLnpse5FV79Gm8nV4TBhE4hv03MpgYG7xO_dXR8he_nehzi98djTLxFwzWn1a67aLi28vvKbsFFZaX'
    data = {
	    'grant_type' : 'authorization_code',
	    'code' : code,
	    'redirect_uri' : 'http://www.apple2spotify.com/',
	    'client_id' : '103df8f3a4484b5193b7029c1558f94b',
	    'client_secret' : 'd537f84050964560b91dcef6a2bd14bb'
    }

    results = requests.post('https://accounts.spotify.com/api/token', data=data)

    return results.content.json()['refresh_token']