import os
import json
import sqlite3

# From: https://goo.gl/YzypO
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


class DB(object):
    """
    DB driver for the To-Do app - deals with writing entities
    to the DB and reading entities from the DB
    """

    def __init__(self):
        self.conn = sqlite3.connect('todo.db', check_same_thread=False)
        self.create_user_table()
        self.create_transaction_table()

    def create_user_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE user (
                    ID INTEGER PRIMARY KEY,
                    NAME NOT NULL,
                    USERNAME NOT NULL,
                    BALANCE NOT NULL
                );
            """)
        except Exception as e:
            print(e)

    def create_transaction_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE transactions (
                    ID INTEGER PRIMARY KEY,
                    TIMESTAMP TEXT NOT NULL,
                    SENDER_ID INTEGER NOT NULL,
                    RECEIVER_ID INTEGER NOT NULL,
                    AMOUNT DOUBLE NOT NULL,
                    MESSAGE TEXT NOT NULL,
                    ACCEPTED BOOLEAN
                );
            """)
        except Exception as e:
            print(e)

    def get_all_users(self):
        cursor = self.conn.execute('SELECT * FROM user;')
        users =  []
        for row in cursor:
            users.append({'id': row[0], 'name': row[1], 'username': row[2]})
        return users

    def insert_user(self, name, username, balance):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO user (NAME, USERNAME, BALANCE) VALUES (?, ?, ?);', (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    def get_user_by_id(self, id):
        cursor = self.conn.execute('SELECT * FROM user WHERE ID == ?;', (id, ))
        for row in cursor:
            return {'id': row[0], 'name': row[1], 'username': row[2], 'balance': row[3]}

    def delete_user_by_id(self, id):
        cursor = self.conn.execute('DELETE FROM user WHERE ID == ?;', (id, ))
        for row in cursor:
            return {'id': row[0], 'name': row[1], 'username': row[2], 'balance': row[3]}

    def transaction_send_money(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE user SET BALANCE = BALANCE - ? WHERE ID= ?;', (amount, sender_id))
        cursor.execute('UPDATE user SET BALANCE = BALANCE + ? WHERE ID= ?;', (amount, receiver_id))
        cursor.execute('INSERT INTO transactions (TIMESTAMP, SENDER_ID, RECEIVER_ID, AMOUNT, MESSAGE, ACCEPTED) VALUES (?, ?, ?, ?, ?, ?);', (timestamp, sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def transaction_request_money(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO transactions (TIMESTAMP, SENDER_ID, RECEIVER_ID, AMOUNT, MESSAGE, ACCEPTED) VALUES (?, ?, ?, ?, ?, ?);', (timestamp, sender_id, receiver_id, amount, message, accepted))
        self.conn.commit()
        return cursor.lastrowid

    def accept_request(self, id, timestamp, accepted, sender_id, receiver_id, amount):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE transactions SET ACCEPTED = ? WHERE ID = ?;', (accepted, id))
        cursor.execute('UPDATE transactions SET TIMESTAMP = ? WHERE ID = ?;', (timestamp, id))
        cursor.execute('UPDATE user SET BALANCE = BALANCE - ? WHERE ID= ?;', (amount, sender_id))
        cursor.execute('UPDATE user SET BALANCE = BALANCE + ? WHERE ID= ?;', (amount, receiver_id))
        self.conn.commit()

    def deny_request(self, id, timestamp, accepted):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE transactions SET ACCEPTED = ? WHERE ID = ?;', (accepted, id))
        cursor.execute('UPDATE transactions SET TIMESTAMP = ? WHERE ID = ?;', (timestamp, id))
        self.conn.commit()


    def get_transaction_by_id(self, id):
        cursor = self.conn.execute('SELECT * FROM transactions WHERE ID == ?;', (id, ))
        for row in cursor:
            return {'id': row[0], 'timestamp': row[1], 'sender_id': row[2], 'receiver_id': row[3], 'amount': row[4], 'message': row[5], 'accepted': row[6]}

    def get_transactions_of_user(self, sender_id, receiver_id):
        cursor = self.conn.execute('SELECT * FROM transactions WHERE SENDER_ID = ? OR RECEIVER_ID = ?;', (sender_id, receiver_id))
        transactions = []
        for row in cursor:
            transactions.append({'id': row[0], 'timestamp': row[1], 'sender_id': row[2], 'receiver_id': row[3], 'amount': row[4], 'message': row[5], 'accepted': row[6]})
        return transactions


DB = singleton(DB)
