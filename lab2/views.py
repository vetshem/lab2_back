from lab2 import app, db
from flask import Flask, request, jsonify, abort
from datetime import datetime
from lab2.schemas import UserSchema, CategorySchema, RecordSchema, CurrencySchema
from lab2.models import User, Category, Record, Currency
import uuid
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
import os
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, verify_jwt_in_request
from passlib.hash import pbkdf2_sha256

jwt = JWTManager(app)
with app.app_context():
    db.create_all()
    db.session.commit()



@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
   return (
       jsonify({"message": "The token has expired.", "error": "token_expired"}),
       401,
   )

@jwt.invalid_token_loader
def invalid_token_callback(error):
   return (
       jsonify(
           {"message": "Signature verification failed.", "error": "invalid_token"}
       ),
       401,
   )

@jwt.unauthorized_loader
def missing_token_callback(error):
   return (
       jsonify(
           {
               "description": "Request does not contain an access token.",
               "error": "authorization_required",
           }
       ),
       401,
   )




health_status = True


@app.route("/")
def hello_user():
    return f"<p>Hello, user!</p><a href='/healthcheck'>Check Health</a>"

@app.route("/healthcheck")
def healthcheck():
    status_code = 200 if health_status else 500
    response = {
        "date": datetime.now(),
        "status": "OK" if health_status else "FAIL"
    }
    return jsonify(response), status_code


@app.route('/user/<int:user_id>', methods=['GET', 'DELETE'])
@jwt_required()
def manage_user(user_id):
    with app.app_context():
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': f'User with that {user_id} dosnt exist'}), 404

        if request.method == "GET":
            user_data = {
                'id': user.id,
                'username': user.username,
                'currency': user.default_currency_id
            }
            return jsonify(user_data), 200

        elif request.method == "DELETE":
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': f'User {user_id} deleted'}), 200

@app.route('/user/reg', methods=['POST'])
def create_user():
    data = request.get_json()

    user_schema = UserSchema()
    try:
        user_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    default_currency_id = data.get("default_currency_id")
    default_currency = Currency.query.filter_by(id=default_currency_id).first()

    if default_currency_id is None:
        default_currency = Currency.query.filter_by(name="Default Currency").first()
        if not default_currency:
            # Валюта за замовчуванням не існує, тому створіть її
            default_currency = Currency(name="Default Currency", symbol="USD")
            db.session.add(default_currency)
            db.session.commit()
            default_currency = Currency.query.filter_by(name="Default Currency").first()

    new_user = User(
        username=user_data["username"],
        default_currency_id=default_currency.id,
        password=pbkdf2_sha256.hash(user_data["password"])
    )
    with app.app_context():
        db.session.add(new_user)
        db.session.commit()

        user_response = {
            'id': new_user.id,
            'username': new_user.username,
            'currency': new_user.default_currency.symbol if new_user.default_currency else None
        }

        return jsonify(user_response), 200

@app.route('/user/login', methods=['POST'])
def login_user():
    data = request.get_json()

    user_schema = UserSchema()
    try:
        user_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({'error': err.messages}), 400

    username = user_data["username"]
    provided_user_id = user_data["id"]

    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if user:

            if provided_user_id is not None and provided_user_id == user.id:
                # Password verification
                if pbkdf2_sha256.verify(user_data["password"], user.password):
                    # Create an access token with the user's ID
                    access_token = create_access_token(identity=user.id)

                    return jsonify({"message": "success login", "token": access_token, "user_id": user.id}), 200
                else:
                    return jsonify({"message": "unsuccessful login (invalid password)"}), 401
            else:
                return jsonify({"message": "unsuccessful login (invalid user ID)"}), 401
        else:
            return jsonify({"message": "unsuccessful login (user not found)"}), 404


@app.route('/users', methods=['GET'])
def get_all_users():
    jwt_claims = verify_jwt_in_request()
    if jwt_claims is None:
        return jsonify({'error': 'invalid token'}), 400
    else:

        with app.app_context():
            users_data = {
                user.id: {"username": user.username, "currency": user.default_currency_id} for user in User.query.all()
            }
            return jsonify(users_data)

@app.route('/category', methods=['POST', 'GET'])
@jwt_required()
def manage_category():
    if request.method == 'GET':
        with app.app_context():
            categories_data = {
                category.id: {"name": category.name} for category in Category.query.all()
            }
            return jsonify(categories_data)

    elif request.method == 'POST':
        data = request.get_json()
        cat_schema = CategorySchema()
        try:
            cat_data = cat_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_category = Category(name=cat_data["name"])
        with app.app_context():
            db.session.add(new_category)
            db.session.commit()

            category_response = {
                "id": new_category.id,
                "name": new_category.name
            }

            return jsonify(category_response), 200

@app.route('/category/<int:cat_id>', methods=['DELETE'])
@jwt_required()
def delete_category(cat_id):
    with app.app_context():
        category = Category.query.get(cat_id)

        if not category:
            return jsonify({'error': f'Category {cat_id} not found'}), 404

        db.session.delete(category)
        db.session.commit()
        return jsonify({'message': f'Category {cat_id} deleted'}), 200

@app.route('/records', methods=['GET'])
def get_all_records():
    with app.app_context():
        records_data = {
            "records": [
                {
                    "id": record.id,
                    "user_id": record.user_id,
                    "cat_id": record.category_id,
                    "amount": record.amount,
                    "currency_id": record.currency_id,
                    "created_at": record.created_at
                } for record in Record.query.all()
            ]
        }
        return jsonify(records_data)


@app.route('/record', methods=['GET', 'POST'])
def manage_records():
    if request.method == 'GET':
        # Handle GET request
        user_id = request.args.get('user_id')
        category_id = request.args.get('category_id')

        if not user_id and not category_id:
            return jsonify({'error': 'Specify user_id or category_id'}), 400

        query = Record.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        if category_id:
            query = query.filter_by(category_id=category_id)

        need_records = query.all()
        print(need_records)
        records_data = {
            record.id: {
                "user_id": record.user_id,
                "cat_id": record.category_id,
                "amount": record.amount,
                "currency_id": record.currency_id,
                "created_at": record.created_at
            } for record in need_records
        }
        return jsonify(records_data)

    elif request.method == 'POST':
        data = request.get_json()
        record_schema = RecordSchema()
        try:
            record_data = record_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        user_id = record_data['user_id']
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Retrieve the currency_id from the associated user
        currency_id = user.default_currency_id



        new_record = Record(
            user_id=user_id,
            category_id=record_data['category_id'],
            amount=record_data['amount'],
            currency_id=currency_id
        )
        with app.app_context():
            db.session.add(new_record)
            db.session.commit()

            record_response = {
                "id": new_record.id,
                "user_id": new_record.user_id,
                "cat_id": new_record.category_id,
                "amount": new_record.amount,
                "currency_id": new_record.currency_id
            }

            return jsonify(record_response), 200

@app.route('/record/<int:record_id>', methods=['GET', 'DELETE'])
def manage_record(record_id):
    with app.app_context():
        record = Record.query.get(record_id)

        if not record:
            return jsonify({"error": f"Record {record_id} not found"}), 404

        if request.method == "GET":
            record_data = {
                "id": record.id,
                "user_id": record.user_id,
                "cat_id": record.category_id,
                "amount": record.amount,
                "currency_id": record.currency_id,
                "created_at": record.created_at
            }
            return jsonify(record_data), 200

        elif request.method == "DELETE":
            db.session.delete(record)
            db.session.commit()
            return jsonify({'message': f'Record {record_id} deleted'}), 200

@app.route('/currency', methods=['POST', 'GET'])
@jwt_required()
def manage_currency():
    if request.method == 'GET':
        with app.app_context():
            currencies_data = {
                currency.id: {"name": currency.name, "symbol": currency.symbol}
                for currency in Currency.query.all()
            }
            return jsonify(currencies_data)

    elif request.method == 'POST':
        data = request.get_json()
        currency_schema = CurrencySchema()
        try:
            currency_data = currency_schema.load(data)
        except ValidationError as err:
            return jsonify({'error': err.messages}), 400

        new_currency = Currency(name=currency_data["name"], symbol=currency_data["symbol"])
        with app.app_context():
            db.session.add(new_currency)
            db.session.commit()

            currency_response = {
                "id": new_currency.id,
                "name": new_currency.name,
                "symbol": new_currency.symbol
            }

            return jsonify(currency_response), 200

@app.route('/currency/<int:currency_id>', methods=['GET', 'DELETE'])
@jwt_required()
def manage_currency_by_id(currency_id):
    with app.app_context():
        currency = Currency.query.filter_by(id=currency_id).first()

        if request.method == "GET":
            if currency:
                currency_data = {
                    'id': currency.id,
                    'name': currency.name,
                    'symbol': currency.symbol
                }
                return jsonify(currency_data), 200
            else:
                return jsonify({'error': f'Currency {currency_id} not found'}), 404

        elif request.method == "DELETE":
            if currency:
                db.session.delete(currency)
                db.session.commit()
                return jsonify({'message': f'Currency {currency_id} deleted'}), 200
            else:
                return jsonify({'error': f'Currency {currency_id} not found'}), 404
