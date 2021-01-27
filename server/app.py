#flask

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash


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



if __name__ == '__main__':
	app.run(debug=True)

