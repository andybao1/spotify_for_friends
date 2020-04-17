import base64
import requests
import json
import boto3
import User
import random

class Group:

	def __init__(self, group_name=None, host=None, group_id=None):
		# creation of the initial group
		dynamodb = boto3.resource('dynamodb')
		self.dynamodb = dynamodb
		group_table = dynamodb.Table('group')
		if group_name is not None and host is not None:
			# create a group with the host as the first member
			self.group_name = group_name
			self.group_id = str(random.randrange(10000,1000000000))
			self.host_name = host.get_username()

			# add host as the first member
			self.users = {host.get_username()}

			# create the group playlist and get a group_playlist_id
			self.group_playlist_id = self.create_group_playlist(host, group_name)

			# generate a random password for future members to join the group
			self.access_code = random.randrange(100000, 999999)
			
			# store all the information in the database
			group_table.put_item(Item={
				'group_id': self.group_id,
				'group_name': self.group_name,
				'host_name' : self.host_name,
				'users' : self.users,
				'access_code' : self.access_code,
				'group_playlist_id' : self.group_playlist_id
			})
			
		# getting one single group from the database and instantiating it
		else:
			# get all the data from the database
			try:
				response = group_table.get_item(Key={
					'group_id' : group_id
					})
			except ClientError as e:
				return
			else:
				group_data = response['Item']
				# instantiate the object given the data
				self.group_id = group_id
				self.group_name = group_data['group_name']
				self.host_name = group_data['host_name']
				self.users = group_data['users']
				self.access_code = group_data['access_code']
				self.group_playlist_id = group_data['group_playlist_id']

	def add_member(self, user, input_access_code):
		# add the member to the group object
		# only if the input_access_code matches the access_code
		# return None if input_access_code is incorrect, return the group playlist_id if correct
		if input_access_code != self.access_code:
			return

		self.users.add(user.get_username())
		self.add_group_member(user.get_username())
		return self.group_playlist_id

	def remove_member(self, host_name, member_username):
		# only the host has the ability to remove a member
		# write the value to the database
		if host_name == self.host_name:
			member = User(member_username)
			member.leave_group(self)

	def leave_member(self, member_username):
		self.users.remove(member_username)
		self.remove_member_from_database(member_username)
	
	def remove_member_from_database(self, member_username):
		group_table = self.dynamodb.Table('group')
		group_table.update_item(
			Key= {'group_id': self.group_id},
			UpdateExpression= "DELETE #u :m",
			ExpressionAttributeNames= {"#u": "users"},
			ExpressionAttributeValues= {":m" :{member_username}}
			)

	def create_group_playlist(self, host, group_name):
		# create an empty group playlist, returns the group_playlist_id
		# get access token and create headers
		print("creating playlist")
		access_token = host.get_access_token()
		headers =  {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json', 'Accept': 'application/json'}

		# create the playlist under the host's account
		data = {'name' : group_name}
		creation_result = requests.post('https://api.spotify.com/v1/users/' + host.get_username() + '/playlists', data=json.dumps(data), headers=headers)
		print(creation_result)
		playlist_id = creation_result.json()['id']
		return playlist_id

	def add_group_member(self, member_username):
		group_table = self.dynamodb.Table('group')
		group_table.update_item(
			Key= {"group_id" : self.group_id},
			UpdateExpression="ADD #u :m",
			ExpressionAttributeNames={"#u": "users"},
			ExpressionAttributeValues={
				':m': {member_username},
			}
			)

	#def refresh_group_playlist(self):
		# the weekly update
	
	def get_group_name(self):
		return self.group_name
	
	def get_group_id(self):
		return self.group_id
		
	def get_users(self):
		return self.users
	
	def get_access_code(self):
		return self.access_code
	
	def get_host_name(self):
		return self.host_name
	
	def get_group_playlist_id(self):
		return self.group_playlist_id

	