import json
import db
from flask import Flask, request
import datetime

app = Flask(__name__)
Db = db.DB()

@app.route('/')
@app.route('/api/users/')
def get_users():
        res = {'success': True, 'data': Db.get_all_users()}
        return json.dumps(res), 200

@app.route('/api/users/', methods =['POST'])
def create_user():
    post_body = json.loads(request.data)
    name = post_body['name']
    username = post_body['username']
    balance = post_body['balance']
    user = {
        'id': Db.insert_user(name, username, balance),
        'name': name,
        'username': username,
        'balance': balance,
        'transactions': []
    }
    return json.dumps({'success': True, 'data': user}), 201

@app.route('/api/user/<int:user_id>/')
def get_user(user_id):
    user = Db.get_user_by_id(user_id)
    if user is not None:
        user['transactions']= Db.get_transactions_of_user(user_id, user_id)
        return json.dumps({'success': True, 'data': user}), 200
    return json.dumps({'success': False, 'error': 'User not found'}), 404

@app.route('/api/user/<int:user_id>/', methods =['DELETE'])
def delete_user(user_id):
    user = Db.get_user_by_id(user_id)
    if user is not None:
        return json.dumps({'success': True, 'data': user}), 200
        Db.delete_user_by_id(user_id)
    return json.dumps({'success': False, 'error': 'User not found'}), 404

@app.route('/api/transactions/', methods =['POST'])
def send_and_request_money():
    post_body = json.loads(request.data)
    timestamp = datetime.datetime.now()
    sender_id = post_body['sender_id']
    receiver_id = post_body['receiver_id']
    amount = post_body['amount']
    message = post_body['message']
    accepted = post_body['accepted']
    sender = Db.get_user_by_id(sender_id)

    if sender is None:
        return json.dumps({'success': False, 'error': 'User not found'}), 404

    if sender['balance'] < amount:
        return json.dumps({'success': False, 'error': 'Not enough money in balance'}), 404

    if accepted == True:
        print(timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
        res = {
            'id': Db.transaction_send_money(timestamp, sender_id, receiver_id, amount, message, accepted),
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'message': message,
            'accepted': accepted
            }
        return json.dumps({'success': True, 'data': res}), 201

    else:
        res = {
            'id': Db.transaction_request_money(timestamp, sender_id, receiver_id, amount, message, accepted),
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'amount': amount,
            'message': message,
            'accepted': accepted
            }
        return json.dumps({'success': True, 'data': res}), 201

@app.route('/api/transaction/<int:transaction_id>/', methods =['POST'])
def accept_or_deny_request(transaction_id):
    transaction = Db.get_transaction_by_id(transaction_id)

    if transaction['accepted'] is not None:
        return json.dumps({'success': False, 'error': 'Transaction already accepted or denied'}), 404

    post_body = json.loads(request.data)
    accepted = post_body['accepted']

    timestamp = datetime.datetime.now()
    string_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

    if accepted == True:
        Db.accept_request(transaction_id, timestamp, accepted, transaction['sender_id'], transaction['receiver_id'], transaction['amount'])
        res = Db.get_transaction_by_id(transaction_id)
        return json.dumps({'success': True, 'data': res}), 201

    if accepted == False:
        Db.deny_request(transaction_id, timestamp, accepted)
        res = Db.get_transaction_by_id(transaction_id)
        return json.dumps({'success': True, 'data': res}), 201



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
