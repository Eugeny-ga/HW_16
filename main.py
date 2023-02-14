
import json
from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

import raw_data

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False



db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def to_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return result


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(100))
    price = db.Column(db.Numeric)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def to_dict(self):
        result = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return result


class Offer(db.Model):
    __tablename__ = 'offer'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def to_dict(self):
        result = {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
        return result

with app.app_context():
    db.create_all()

    for user_data in raw_data.users:
        new_user = User(**user_data)
        db.session.add(new_user)
        db.session.commit()

    for order in raw_data.orders:
        order['start_date'] = datetime.strptime(order['start_date'], "%m/%d/%Y").date()
        order['end_date'] = datetime.strptime(order['end_date'], "%m/%d/%Y").date()
        new_order = Order(**order)
        db.session.add(new_order)
        db.session.commit()

    for offer in raw_data.offers:
        new_offer = Offer(**offer)
        db.session.add(new_offer)
        db.session.commit()



@app.route('/users', methods=['GET', 'POST'])
def users_page():
    if request.method == 'GET':
        users = User.query.all()
        result = [user.to_dict() for user in users]
        return jsonify(result)
    elif request.method == ["POST"]:
        user_data = json.loads(request.data)
        db.session.add(User(**user_data))
        db.session.commit()
        return "User added"


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def user_page_by_id(id):
    user = User.query.get(id)
    if request.method == 'GET':
        result = user.to_dict()
        return jsonify(result)
    elif request.method == 'PUT':
        new_user_data = json.loads(request.data)
        user.first_name = new_user_data.get('first_name')
        user.last_name = new_user_data.get('last_name')
        user.role = new_user_data.get('role')
        user.phone = new_user_data.get('phone')
        user.email = new_user_data.get('email')
        user.age = new_user_data.get('age')
        db.session.add(user)
        db.session.commit()
        result = User.query.get(id)
        return jsonify(result)

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()


@app.route('/orders', methods=['GET', 'POST'])
def orders_page():
    if request.method == 'GET':
        orders = Order.query.all()
        result = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict["start_date"] = str(order_dict['start_date'])
            order_dict["end_date"] = str(order_dict['end_date'])
            result.append(order_dict)
        return jsonify(result)
    elif request.method == ["POST"]:
        order_data = json.loads(request.data)
        db.session.add(Order(**order_data))
        db.session.commit()
        return "Order added"


@app.route('/orders/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def order_page_by_id(id):
    order = Order.query.get(id)
    if request.method == 'GET':
        order_dict = order.to_dict()
        order_dict["start_date"] = str(order_dict['start_date'])
        order_dict["end_date"] = str(order_dict['end_date'])
        return jsonify(order_dict)
    elif request.method == 'PUT':
        new_order_data = json.loads(request.data)
        order.name = new_order_data.get('name')
        order.description = new_order_data.get('description')
        order.start_date = datetime.strptime((new_order_data["start_date"]), "%Y-%m-%d").date()
        order.end_date = datetime.strptime((new_order_data["end_date"]), "%Y-%m-%d").date()
        order.address = new_order_data.get('address')
        order.price = new_order_data.get('price')
        order.customer_id = new_order_data.get('customer_id')
        order.executor_id = new_order_data.get('executor_id')
        db.session.add(order)
        db.session.commit()

        update_order = Order.query.get(id)
        update_order_dict = update_order.to_dict()
        update_order_dict["start_date"] = str(update_order_dict['start_date'])
        update_order_dict["end_date"] = str(update_order_dict['end_date'])
        return jsonify(update_order_dict)

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()


@app.route('/offers', methods=['GET', 'POST'])
def offers_page():
    if request.method == 'GET':
        offers = Offer.query.all()
        result = [offer.to_dict() for offer in offers]
        return jsonify(result)
    elif request.method == ["POST"]:
        offer_data = json.loads(request.data)
        db.session.add(Offer(**offer_data))
        db.session.commit()
        return "Offer added"


@app.route('/offers/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def offers_page_by_id(id):
    offer = Offer.query.get(id)
    if request.method == 'GET':
        result = offer.to_dict()
        return jsonify(result)
    elif request.method == 'PUT':
        new_offer_data = json.loads(request.data)
        offer.executor_id = new_offer_data.get('executor_id')
        offer.order_id = new_offer_data.get('order_id')
        db.session.add(offer)
        db.session.commit()
        return 'Offer update'

    elif request.method == 'DELETE':
        db.session.delete(offer)
        db.session.commit()
        return 'Offer delete'

if __name__ == '__main__':
    app.run()






