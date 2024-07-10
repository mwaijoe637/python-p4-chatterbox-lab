from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    serialized_messages = [message.to_dict() for message in messages]
    return jsonify(serialized_messages)

@app.route('/messages', methods=['POST'])
def create_message():
    body = request.json.get('body')
    username = request.json.get('username')
    if not body or not username:
        return make_response(jsonify({'error': 'Missing body or username'}), 400)

    new_message = Message(body=body, username=username)
    db.session.add(new_message)
    db.session.commit()
    return jsonify(new_message.to_dict())

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    new_body = request.json.get('body')
    if new_body:
        message.body = new_body
        message.updated_at = datetime.utcnow()
        db.session.commit()
    
    return jsonify(message.to_dict())

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({'error': 'Message not found'}), 404)

    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted'})

if __name__ == '__main__':
    app.run(port=5555)
