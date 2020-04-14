import requests
import boto3
import json
import authorization
import generate_playlist
from User import User

def lambda_handler(event, context):
    
    #refreshToken = authorization.getRefreshToken()
    test_user = User("misho2211", "AQCiW_MnJ0YA46k1bK_ZokDO31kApl9Pa7or0ANH-fU24PXoMl1yuI9Z-kG9aQJKB_Z2JUR5gt4yFq0U_ViijJbeL55g3L0KXsv4UFEQoXSE4Tcz74vAmui30zgw9-7Y4bk")
    
    
    # print(event)
    # #save that code for later when we use API gateway
    # #content = json.loads(event['body'], strict = False)
    # accessToken = event['accessToken']
    
    # #Create headers for requests
    # headers = {'Authorization': 'Bearer ' + accessToken, 'Content-Type': 'application/json', 'Accept': 'application/json'}

    # #Get top 5 tracks in the past week for this user
    # track_results = generate_playlist.top_tracks(headers)
    # playlist_creation_results = generate_playlist.create_playlist(headers)
    # playlist_id = playlist_creation_results.json()['uri'].split(":")[-1]
    # track_ids = ["spotify:track:" + x for x in track_results]
    # data = {'uris' : track_ids}
    # result = requests.post('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', data=json.dumps(data), headers=headers)
    
    # print(track_results)
    
    



