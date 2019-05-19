from flask import Flask, render_template, request
from flask_mail import Mail, Message
import sqlite3
import praw
import datetime
import re

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'thefrontpagestore@gmail.com'
app.config['MAIL_PASSWORD'] = 'Alfismo249_'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

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
		self.cost = 10

users = []
cart = []
totalCost = 0

@app.route('/', methods=['GET', 'POST'])
def load():
	global totalCost

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

	if request.method == 'POST':
		if request.form.get('Add') == 'Add':
			for user in users:
				if user.name == request.form.get('Username'):
					for cartUser in cart:
						if user.name == cartUser.name:
							return render_template('index.html', users=users, cart=cart, total=totalCost)
					cart.append(user)
					totalCost += user.cost
		elif request.form.get('Remove') == 'Remove':
			for user in cart:
				if user.name == request.form.get('Username'):
					cart.remove(user)
					totalCost -= user.cost
		elif request.form.get('Send') == 'Send':
			return 'Email sent!'

		return render_template('index.html', users=users, cart=cart,total=totalCost)
	else:
		return render_template('index.html', users=users, cart=cart,total=totalCost)

@app.route('/contact', methods=['POST'])
def contact():
	if request.form.get('Send') == 'Submit':
		isValidEmail = re.match('[^@]+@[^@]+\.[^@]+', request.form.get('EmailAddress'))
		if not isValidEmail:
			return "Email is invalid"

		msg = Message(request.form.get('EmailAddress'),
			body=request.form.get('EmailMessage'),
			sender="thefrontpagestore@gmail.com", 
			recipients=["thefrontpagestore@gmail.com"])

		mail.send(msg)

		return render_template('contact.html')
	else:
		return 'An error has occurred sending your email.'

if __name__ == "__main__":
	app.run(host='0.0.0.0')
