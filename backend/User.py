import base64
import requests
import json
import boto3
from Group import Group
from datetime import datetime

class User:
	
	# to create a new instance just call this in the main class that you create: user_object = User(username, usertoken)
	def __init__(self, username, refreshToken = None):
		dynamodb = boto3.resource('dynamodb')
		user_table = dynamodb.Table('user')
		response = user_table.get_item(Key={
			'username' : username
		})
		self.dynamodb = dynamodb
		
		if 'Item' not in response:
			self.username = username
			self.groupIds = {"None"}
			self.refreshToken = refreshToken
		
			#get an access code for the initialization process and create the headers field 
			access_token = self.get_access_token()
			headers =  {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
		
			# create a new weekly favourites playlist
			self.weeklyFavId = self.initialize_weekly_fav(headers)
				
			#get the top 50 tracks from the past month to store for history and for the next update
			self.topFifty = self.top_tracks(headers, 50)
	
			# store everything that we need in their respective databases
			self.store_user()
			self.store_history(self.topFifty)
		else:
			user_data = response['Item']
			# instantiate the object given the data
			self.username = username
			self.groupIds = user_data['groupIds']
			self.refreshToken = user_data['refreshToken']
			self.weeklyFavId = user_data['weeklyFavId']
			self.topFifty = user_data['topFifty']
			
			

	
	#using the refresh token that is stored, get an access token
	def get_access_token(self):
		post_data = {'grant_type' : 'refresh_token', 'refresh_token' : self.refreshToken}
		#you need to supply the clientid:clientsecret encoded in base64 which are given to us when we register our app with spotify
		post_headers = {'Authorization' : 'Basic MTAzZGY4ZjNhNDQ4NGI1MTkzYjcwMjljMTU1OGY5NGI6ZDUzN2Y4NDA1MDk2NDU2MGI5MWRjZWY2YTJiZDE0YmI='}
		result = requests.post('https://accounts.spotify.com/api/token', data=post_data, headers=post_headers)
		access_token = result.json()['access_token']
		return access_token
	
	def get_headers(self):
		access_token = self.get_access_token()
		headers =  {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
		return headers
		
	def top_tracks(self, headers, limit):
		result = requests.get("https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=" + str(limit), headers=headers)
		list_r = []
		for item in result.json()['items']:
			list_r += [item['id']]
		return list_r

	def create_playlist(self, headers):
		data = {'name' : 'my current top 20'}
		result = requests.post('https://api.spotify.com/v1/users/' + self.username + '/playlists', data=json.dumps(data), headers=headers )
		return result.json()['id']
		
	def initialize_weekly_fav(self, headers):
		top_tracks = self.top_tracks(headers, 20)
		playlist_id = self.create_playlist(headers)
		track_ids = ["spotify:track:" + x for x in top_tracks]
		data = {'uris' : track_ids}
		result = requests.post('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', data=json.dumps(data), headers=headers)
		
		return playlist_id
		
	def update_weekly_fav(self, headers):
		top_tracks = self.top_tracks(headers, 20)
		playlist_id = self.weeklyFavId
		track_ids = ["spotify:track:" + x for x in top_tracks]
		data = {'uris' : track_ids}
		result = requests.put('https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks', data=json.dumps(data), headers=headers)

	
	def store_history(self, topFifty):
		history_table = self.dynamodb.Table('history')
		history_table.put_item(Item={
			'username,date' : self.username + str(datetime.now()),
			'songs' : topFifty
		})
		
	def store_user(self):
		user_table = self.dynamodb.Table('user')
		user_table.put_item(Item={
			'username': self.username,
			'groupIds': self.groupIds,
			'refreshToken': self.refreshToken,
			'weeklyFavId' : self.weeklyFavId,
			'topFifty' : self.topFifty
		})
	
	#####
	
	def create_group(self, groupname):
		# create the group with the host as the first member
		group = Group(group_name = groupname, host = self, group_id = None)
		self.groupIds.add(group.group_id)
		self.store_user()

	def join_group(self, groupid, access_code):
		group = Group(group_name = None, host = None, group_id = groupid)
		# group.add_member returns a boolean of whether the access_code is correct or not
		group_playlist_id = group.add_member(self, access_code)
		if group_playlist_id is not None:
			self.groupIds.add(group.get_group_id())
			# now make this user follow the host's group playlist
			headers = self.get_headers()
			result = requests.put('https://api.spotify.com/v1/playlists/{playlist_id}/followers' + group_playlist_id, headers=headers)
			self.store_user()
			


	def leave_group(self, groupid):
		group = Group(group_id = groupid)
		group.leave_member(self.username)
		self.groupIds.remove(groupid)
		self.remove_groupId_from_database(groupid)
	
	def remove_groupId_from_database(self, groupid):
		user_table = self.dynamodb.Table('user')
		user_table.update_item(
			Key = {"username": self.username},
			UpdateExpression= "DELETE groupIds :g",
			ExpressionAttributeValues= {":g" :{groupid}}
			)

	def remove_member(self, group, member_username):
		group.remove_member(self.username, member_username)
	
	def get_username(self):
		return self.username