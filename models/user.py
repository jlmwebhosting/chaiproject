from lib.py import model

reset_email_message = """
Hello %(fullname)s,

To reset your password <a href="%(url)s">click here</a>.

Or copy-paste this url to your address bar:

%(url)s

If you did not request to reset your password, ingore this mail.

Nice Day!

(System Generated Message)
"""

class User(model.Model):
	_name = 'user'
	_create_table = """
	create table `user` (
		name varchar(180) primary key,
		fullname varchar(240),
		email varchar(180),
		password varchar(100),
		reset_password_id varchar(100),
		_updated timestamp
	) engine=InnoDB
	"""	
	
	def __init__(self, obj):
		super(User, self).__init__(obj)
		
	def before_insert(self):
		"""save password as sha256 hash"""		
		import hashlib
		if 'password' in self.obj and len(self.obj['password'])!=64:
			self.obj['password'] = hashlib.sha256(self.obj['password']).hexdigest()
		
		# clear re-entered password
		if 'password_again' in self.obj:
			del self.obj['password_again']
	
	def before_update(self):
		self.before_insert()
	
	def before_get(self):
		"""hide password"""
		if 'password' in self.obj:
			del self.obj['password']
	
	def request_reset_password(self):
		"""generate a reset password id and mail the password to the user"""
		import hashlib, time
		from lib.py import database, emailer
		import conf
		
		db = database.get()
		resetid = hashlib.sha224(str(time.time())).hexdigest()
		db.setvalue('user', self.obj['name'], 'reset_password_id', resetid)
		
		d = {
			'fullname': self.obj['fullname'] or self.obj['name'],
			'url': conf.app_url + '#reset_password/' + resetid
		}
		
		emailer.sendtext(recipients=[self.obj['email']], subject="Password Reset",
		 	message=reset_email_message % d)
		
		
