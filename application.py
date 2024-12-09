from flask import Flask, jsonify, request, render_template
import sqlite3
import logging
import boto3
from botocore.config import Config
import os


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CloudWatch Logs client
cw_logs = boto3.client('logs', config=Config(region_name='eu-north-1'))
log_group_name = 'TaskManager-Flask-SQLite-Logs'
log_stream_name = 'flask-app-logs'


app = Flask(__name__)

# Path for the database
DB_PATH = '/home/ec2-user/tasks.db'

# Function to initialize the database
def query_db():
    if not os.path.exists(DB_PATH):
        logger.info("Initializing the database.")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized at %s", DB_PATH)
    else:
        logger.info("Database already exists at %s", DB_PATH)

# Serve the frontend
@app.route('/')
def home():
    logger.info('rendered html page')
    return render_template('index.html')

# Add a new task
@app.route('/tasks', methods=['POST'])
def add_task():
    logger.info('Received request for /tasks POST method - used to add new task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    query_db('INSERT INTO tasks (name, description) VALUES (?, ?)',
             (data['name'], data.get('description', '')))
    logger.info('Completed request for /tasks POST method - used to add new task')
    return jsonify({'message': 'Task added'}), 201

# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method - used to fetch all tasks')
    tasks = query_db('SELECT * FROM tasks')
    logger.info('Completed request for /tasks GET method - used to fetch all tasks')
    return jsonify([dict(task) for task in tasks])

# Update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info('Received request for /tasks PUT method - used to update a task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    result = query_db('UPDATE tasks SET name = ?, description = ? WHERE id = ?',
                      (data['name'], data.get('description', ''), task_id))
    if result:
        logger.info('Completed request for /tasks PUT method - used to update a task')
        return jsonify({'message': 'Task updated'})
    return jsonify({'error': 'Task not found'}), 404

# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method - used to delete a task')
    query_db('DELETE FROM tasks WHERE id = ?', (task_id,))
    logger.info('Completed request for /tasks DELETE method - used to delete a task')
    return jsonify({'message': f'Task with id {task_id} deleted'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)
