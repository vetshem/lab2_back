from lab2 import app
from flask import Flask, request, jsonify
from faker import Faker
from datetime import datetime
from lab2.models import User, Category, Record
import uuid




users = {}
categories = {}
records = {}

@app.route("/")
def hello_user():
    return f"<p>Hello, user!</p><a href='/healthcheck'>Check Health</a>"

health_status = True
@app.route("/healthcheck")
def healthcheck():
    if health_status:
        resp = jsonify(date=datetime.now(), status="OK")
        resp.status_code = 200
    else:
        resp = jsonify(date=datetime.now(), status="FAIL")
        resp.status_code = 500
    return resp

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = users.pop(user_id, None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route('/user', methods=['POST'])
def create_user():
    user_data = request.get_json()

    # Перевірка обов'язкових полів
    if "username" not in user_data:
        return jsonify({"error": "username are required"}), 400

    # Генерація випадкового ідентифікатора
    user_id = uuid.uuid4().hex
    user = {"id": user_id, **user_data}
    users[user_id] = user
    return jsonify(user)



@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(list(users.values()))


@app.route('/category', methods=['GET'])
def get_categories():
    return jsonify(list(categories.values()))


@app.route('/category', methods=['POST'])
def create_category():
    category_data = request.get_json()
    if "name" not in category_data:
        return jsonify({"error": "name are required"}), 400
    category_id = uuid.uuid4().hex
    category = {"id": category_id, **category_data}
    categories[category_id] = category
    return jsonify(category)


@app.route('/category', methods=['DELETE'])
def delete_category():
    category_id = request.args.get('id')

    if category_id:
        # Видалення конкретної категорії за ідентифікатором
        category = categories.pop(category_id, None)
        if not category:
            return jsonify({"error": f"Category with id {category_id} not found"}), 404
        return jsonify(category)
    else:
        # Видалення всіх категорій
        categories.clear()
        return jsonify({"message": "All categories deleted"})


@app.route('/record/<record_id>', methods=['GET'])
def get_record(record_id):
    record = records.get(record_id)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(record)


@app.route('/record/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = records.pop(record_id, None)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    return jsonify(record)


@app.route('/record', methods=['POST'])
def create_record():
    record_data = request.get_json()

    user_id = record_data.get('user_id')
    category_id = record_data.get('category_id')

    if not user_id or not category_id:
        return jsonify({"error": "Both user_id and category_id are required"}), 400

    # Перевірка чи існує користувач з вказаним user_id
    if user_id not in users:
        return jsonify({"error": f"User with id {user_id} not found"}), 404

    # Перевірка чи існує категорія з вказаним category_id
    if category_id not in categories:
        return jsonify({"error": f"Category with id {category_id} not found"}), 404

    record_id = uuid.uuid4().hex
    record = {"id": record_id, **record_data}
    records[record_id] = record
    return jsonify(record)


@app.route('/record', methods=['GET'])
def get_records():
    user_id = request.args.get('user_id')
    category_id = request.args.get('category_id')

    if not user_id and not category_id:
        return jsonify({"error": "Specify user_id or category_id"}), 400

    filtered_records = [
        r for r in records.values() if (not user_id or r['user_id'] == user_id) or (not category_id or r['category_id'] == category_id)
    ]
    return jsonify(filtered_records)

