from flask import Flask, render_template
from flask_mail import Mail
import sqlite3
import praw
import datetime

app = Flask(__name__)

months = [ 'January', 'February', 'March', 'April', 'May',
 'June', 'July', 'August', 'September', 'November', 'December']
#Authenticate PRAW
r = praw.Reddit(client_id='QGNYNC0_WKmCPQ',
				client_secret='7hhoPaR9dNg9hQZIx4GqXFTsaH0',
				password='flannecessary',
				user_agent='Language processing script by NecessaryFlan',
				username='NecessaryFlan')


class User:
	def __init__(self, username, password, client_id, client_secret, user_agent):
		self.name = username
		self.password = password
		self.client_id = client_id
		self.client_secret = client_secret
		self.user_agent = user_agent
		self.profile = r.redditor(username)
		self.commentKarma = self.profile.comment_karma
		self.linkKarma = self.profile.link_karma
		self.dateUnformatted = datetime.datetime.utcfromtimestamp(self.profile.created_utc)
		self.dateCreated = months[self.dateUnformatted.month - 1] + " " + (str)(self.dateUnformatted.day) + ", " + (str)(self.dateUnformatted.year) 

users = []

@app.route('/')
def load():
	del users[:]

	#connect to the database
	conn = sqlite3.connect('accounts.db')
	c = conn.cursor()

	c.execute('SELECT * FROM Accounts')
	all_rows = c.fetchall()

	conn.close()

	for row in all_rows:
		username = row[0]
		password = row[1]
		client_id = row[2]
		client_secret = row[3]
		user_agent = row[4]

		users.append(User(username,password=password,client_id=client_id,client_secret=client_secret,user_agent=user_agent))

	for user in users:
		user.commentKarma = user.profile.comment_karma
		user.linkKarma = user.profile.link_karma

	return render_template('index.html', users=users)

if __name__ == "__main__":
	app.run(host='0.0.0.0')
