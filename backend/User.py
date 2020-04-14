import base64
import requests
import json
import boto3

class User:
	
	# to create a new instance just call this in the main class that you create: user_object = User(username, usertoken)
	def __init__(self, username, refreshToken):
		# change the parameters if you need
		self.username = username
		self.groupIds = []
		self.refreshToken = refreshToken

		# create a new weekly favourites playlist
		self.weeklyFavId = self.initialize_weekly_fav()

		# store everything that we need in their respective databases
		dynamodb = boto3.resource('dynamodb')
		table = dynamodb.Table('user')
		table.put_item(Item={
			'username': self.username,
			'groupIds': self.groupIds,
			'refreshToken': self.refreshToken,
			'weeklyFavId' : self.weeklyFavId
								
		})
		
	
	#using the refresh token that is stored, get an access token
	def get_access_token(self):
		post_data = {'grant_type' : 'refresh_token', 'refresh_token' : self.refreshToken}
		print(post_data)
		#you need to supply the clientid:clientsecret encoded in base64 which are given to us when we register our app with spotify
		post_headers = {'Authorization' : 'Basic MTAzZGY4ZjNhNDQ4NGI1MTkzYjcwMjljMTU1OGY5NGI6ZDUzN2Y4NDA1MDk2NDU2MGI5MWRjZWY2YTJiZDE0YmI='}
		result = requests.post('https://accounts.spotify.com/api/token', data=post_data, headers=post_headers)
		access_token = result.json()['access_token']
		return access_token
		
	def top_tracks(self, headers):
		result = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term", headers=headers)
		list_r = []
		for item in result.json()['items']:
			list_r += [item['id']]
		return list_r

	def create_playlist(self, headers):
		data = {'name' : 'weekly favorites'}
		result = requests.post('https://api.spotify.com/v1/users/' + 'misho2211' + '/playlists', data=json.dumps(data), headers=headers )
		return result.json()['id']
		

	def initialize_weekly_fav(self):
		access_token = self.get_access_token()	
		print(access_token)
		headers =  {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
		
		top_tracks = self.top_tracks(headers)
		print("top_tracks")
		print(top_tracks)
		playlist_id = self.create_playlist(headers)
		print("playlist_id")
		print(playlist_id)
		
		track_ids = ["spotify:track:" + x for x in top_tracks]
		data = {'uris' : track_ids}
		result = requests.post('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', data=json.dumps(data), headers=headers)
		return playlist_id
		


		



#
