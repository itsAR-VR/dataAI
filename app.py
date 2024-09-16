# app.py

import os
import datetime
from functools import wraps
from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import openai

load_dotenv()

app = Flask(__name__, static_folder='build')

CORS(app, resources={
     r"/*": {"origins": "https://data-ai-p5ei.vercel.app/"}})


# Database configuration
if os.getenv('RAILWAY_ENVIRONMENT'):
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace(
            'postgres://', 'postgresql://')
    else:
        raise ValueError(
            "DATABASE_URL is not set in the environment variables.")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales_data.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# Models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    sales_data = db.relationship('SalesData', backref='user', lazy=True)


class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    additional_info = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


with app.app_context():
    db.create_all()

# Helper functions


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if parts[0] == 'Bearer' and len(parts) == 2:
                token = parts[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Routes


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'New user created!'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 401

    if check_password_hash(user.password, password):
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({'token': token}), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401


@app.route('/add_sales_data', methods=['POST'])
@token_required
def add_sales_data(current_user):
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No input data provided'}), 400

    date_str = data.get('date')
    product_name = data.get('product_name')
    quantity = data.get('quantity')
    price = data.get('price')
    additional_info = data.get('additional_info', {})

    if not date_str or not product_name or quantity is None or price is None:
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    new_sales_data = SalesData(
        date=date,
        product_name=product_name,
        quantity=quantity,
        price=price,
        additional_info=additional_info,
        user_id=current_user.id
    )
    db.session.add(new_sales_data)
    db.session.commit()
    return jsonify({'message': 'Sales data added successfully!'}), 201


@app.route('/ask', methods=['POST'])
@token_required
def ask_question(current_user):
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'message': 'Question is required'}), 400

    # Fetch sales data for the current user
    sales_data = SalesData.query.filter_by(user_id=current_user.id).all()
    context = "\n".join(
        [f"Date: {sale.date}, Product: {sale.product_name}, Quantity: {sale.quantity}, Price: {sale.price}, Additional Info: {sale.additional_info}" for sale in sales_data]
    )

    # Use OpenAI to generate a response
    openai.api_key = os.getenv('OPENAI_API_KEY')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about sales data. Here's the context:"},
                {"role": "user", "content": context},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message['content']
    except openai.error.OpenAIError as e:
        return jsonify({'message': 'Failed to get response from AI service'}), 500

    return jsonify({'answer': answer}), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Serve React build files
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
