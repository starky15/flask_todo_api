#flask

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '*2__cbuuXjhy52##@344abc!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask_user:Password@12@localhost/myapp'

# engine = create_engine('mysql+mysqldb://scott:tiger@localhost/foo')


#creating class for sqlalchemy
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	public_id = db.Column(db.String(50), unique = True)	
	name = db.Column(db.String(50))
	password = db.Column(db.String(80))
	admin = db.Column(db.Boolean)	

class Todo(db.Model):
	id = db.Column(db.Integer, primary_key =True)
	text = db.Column(db.String(50))
	complete = db.Column(db.Boolean)
	user_id = db.Column(db.String(50))

@app.route('/')
def index():
	return jsonify({'status':'success'})


@app.route('/user', methods=['POST'])
def create_user():

	data = request.get_json()
	hashed_pwd = generate_password_hash(data['password'], method = 'sha256')
	new_user = User(public_id=str(uuid.uuid4()), name = data['name'], password = hashed_pwd, admin = False)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'status':'success'})


@app.route('/user',methods=['GET'])
def get_all_users():
	users = User.query.all()
	user_list = []
	for user in users:
		opt = {}
		opt['name'] = user.name
		opt['password'] = user.password
		opt['admin'] = user.admin
		opt['public_id'] = user.public_id
		user_list.append(opt)

	# print(user_list)
	return jsonify({'users':user_list})


@app.route('/user/<public_id>', methods=['PUT'])
def promote_user(public_id):
	user = User.query.filter_by(public_id = public_id).first()
	if not user:
		return jsonify({'status':'User does not exist!'})
	else:
		user.admin = True
		db.session.commit()
		return jsonify({'status': 'User was promoted successfully!'})


@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
	user = User.query.filter_by(public_id = public_id).first()
	if not user:
		return jsonify({'status':'User does not exist!'})
	else:
		user.admin = True
		db.session.delete(user)
		db.session.commit()
		return jsonify({'status': 'User was deleted successfully!'})


@app.route('/login',methods=['POST'])
def login():
	auth = request.authorization
	if not auth or not auth.username or not auth.password:
		make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'})

	user = User.query.filter_by(name=auth.username).first()

	if not user:
		make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login Required!"'})

	if check_password_hash(user.password, auth.password):
		token = jwt.encode({'public_id':user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
		# return jsonify({'token': token.decode('UTF-8')})
		return make_response(jsonify({'token' : token.decode('UTF-8')}), 201) 


if __name__ == '__main__':
	app.run(debug=True)

