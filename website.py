from flask import Flask, render_template, request, url_for, redirect
from flask_mail import Mail, Message
import sqlite3
import praw
import datetime
import re
import stripe

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'thefrontpagestore@gmail.com'
app.config['MAIL_PASSWORD'] = 'Alfismo249_'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

months = [ 'January', 'February', 'March', 'April', 'May',
 'June', 'July', 'August', 'September', 'October', 'November', 'December']
#Authenticate PRAW
r = praw.Reddit(client_id='QGNYNC0_WKmCPQ',
				client_secret='7hhoPaR9dNg9hQZIx4GqXFTsaH0',
				password='flannecessary',
				user_agent='Language processing script by NecessaryFlan',
				username='NecessaryFlan')

class User:
	def __init__(self, username, password, client_id, client_secret, user_agent, cost):
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
		self.cost = cost

users = []
cart = []
totalCost = 0

@app.route('/', methods=['GET'])
def home():
	return render_template('index.html')

@app.route('/', methods=['POST'])
def home():
	return redirect(url_for('index.html'))

@app.route('/accounts', methods=['GET', 'POST'])
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
		cost = row[4]
		user_agent = row[5]

		users.append(User(username,password=password,client_id=client_id,client_secret=client_secret,user_agent=user_agent,cost=cost))

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
					totalCost += (int)(user.cost)
		elif request.form.get('Remove') == 'Remove':
			for user in cart:
				if user.name == request.form.get('Username'):
					cart.remove(user)
					totalCost -= (int)(user.cost)
		elif request.form.get('Checkout') == 'Checkout':
			charge();

		return render_template('accounts.html', users=users, cart=cart,total=totalCost)
	else:
		return render_template('accounts.html', users=users, cart=cart,total=totalCost)

@app.route('/charge', methods=['POST'])
def charge():
	stripe.api_key = 'sk_live_ArRWnSubtTtdTcXyCpEhFcu2002YbfhXh9'

	# Token is created using Checkout or Elements!
	# Get the payment token ID submitted by the form:
	token = request.form['stripeToken'] # Using Flask
	
	messageBody = "Your accounts are here!\n"
	userString = ''
	for user in cart:
		userString += user.name + '\n'
		messageBody += "Username: " + user.name + '\n'
		messageBody += "Password: " + user.password + '\n'

	charge = stripe.Charge.create(
	    amount=totalCost*100,
	    currency='usd',
	    description='Accounts purchased: ' + userString,
	    source=token,
	)

	msg = Message("Your purchased account(s)",
		body=messageBody,
		sender="thefrontpagestore@gmail.com", 
		recipients=[request.form.get('EmailAddress'),"thefrontpagestore@gmail.com"])

	isValidEmail = re.match('[^@]+@[^@]+\.[^@]+', request.form.get('EmailAddress'))
	if not isValidEmail:
		render_template('error.html', error="Email is invalid")

	mail.send(msg)

	accountString = ""

	for user in cart:
		accountString += user.name + '\n'

	#connect to the database
	conn = sqlite3.connect('accounts.db')
	c = conn.cursor()

	for user in cart:
		c.execute('SELECT * FROM Accounts')
		all_rows = c.fetchall()
		for row in all_rows:
			if row[0] == user.name:
				c.execute("DELETE FROM Accounts WHERE Username='"+row[0]+"';") 

		conn.commit()
		conn.close()

	return render_template('payment.html', accounts=accountString)

@app.route('/faq', methods=['GET'])
def faq():
	return render_template('faq.html')

@app.route('/contact', methods=['GET'])
def contact_view():
	return render_template('contact.html')

@app.route('/cart', methods=['GET'])
def cartView():
	global totalCost
	global cart
	return render_template('cart.html', total=totalCost, cart=cart)

@app.route('/accounts', methods=['GET'])
def accounts():
	return render_template('accounts.html', users=users)

@app.route('/contact', methods=['POST'])
def contact():
	if request.form.get('Send') == 'Submit':
		isValidEmail = re.match('[^@]+@[^@]+\.[^@]+', request.form.get('EmailAddress'))
		if not isValidEmail:
			render_template('error.html', error="Email is invalid")

		msg = Message(request.form.get('EmailAddress'),
			sender='thefrontpagestore@gmail.com',
			recipients=['thefrontpagestore@gmail.com'],
			body=request.form.get('EmailMessage'))

		mail.send(msg)

		return render_template('contact.html')
	else:
		render_template('error.html', error="'An error has occurred sending your email.'") 

if __name__ == "__main__":
	app.run(host='0.0.0.0')
