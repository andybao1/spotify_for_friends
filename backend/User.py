class User:

	def __init__(self, username, usertoken):
		# change the parameters if you need
		self.username = username

		# just some ideas of what you can do in the init
		self.userId = None # do we need this?
		self.groupIds = []
		self.refreshToken = None # idk how to do this

		# create a new weekly favourites playlist
		self.weeklyFavId = self.initialize_weekly_fav()

		# store everything that we need in their respective databases




	def initialize_weekly_fav(self):
		# create the initial playlist for the user



	def create_group(groupname):
		# initialize an instance of the Group class
		


	def refresh_weekly_fav(self):
		# maybe store this info somewhere so that we only need to do this for each user once (even if they are in multiple groups)



