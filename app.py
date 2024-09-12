from flask import Flask, send_from_directory
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
import openai

import os
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
import openai

load_dotenv()


app = Flask(__name__, static_folder='build')
CORS(app)

# Use PostgreSQL in production (Railway), SQLite in development
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

# ... rest of your code ...


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class SalesData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    additional_info = db.Column(db.JSON)


with app.app_context():
    db.create_all()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created!'})


@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic realm="Login required!"'}), 401
    user = User.query.filter_by(username=auth.username).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 401
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'username': user.username, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Could not verify!'}), 401


@app.route('/add_sales_data', methods=['POST'])
@token_required
def add_sales_data():
    data = request.get_json()
    new_sales_data = SalesData(
        date=datetime.datetime.strptime(data['date'], '%Y-%m-%d').date(),
        product_name=data['product_name'],
        quantity=data['quantity'],
        price=data['price'],
        additional_info=data.get('additional_info', {})
    )
    db.session.add(new_sales_data)
    db.session.commit()
    return jsonify({'message': 'Sales data added successfully!'})


@app.route('/ask', methods=['POST'])
@token_required
def ask_question():
    data = request.get_json()
    question = data['question']

    # Fetch all sales data
    sales_data = SalesData.query.all()
    context = "\n".join(
        [f"Date: {sale.date}, Product: {sale.product_name}, Quantity: {sale.quantity}, Price: {sale.price}, Additional Info: {sale.additional_info}" for sale in sales_data])

    # Use OpenAI to generate a response
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions about sales data. Here's the context:"},
            {"role": "user", "content": context},
            {"role": "user", "content": question}
        ]
    )

    return jsonify({'answer': response.choices[0].message['content']})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
