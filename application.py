from flask import Flask, jsonify, request, render_template
import logging
import os
import json
import boto3
from botocore.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CloudWatch Logs client
cw_logs = boto3.client('logs', config=Config(region_name='eu-north-1'))
log_group_name = 'TaskManager-Flask-SQLite-Logs'
log_stream_name = 'flask-app-logs'

# Path to the JSON file for task storage
TASKS_FILE = '/home/ec2-user/TaskManager-Flask-SQLite/tasks.json'

app = Flask(__name__)

# Helper function to load tasks from the file
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

# Helper function to save tasks to the file
def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

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
    
    tasks = load_tasks()
    new_task = {
        'id': len(tasks) + 1,  # Simple ID generation
        'name': data['name'],
        'description': data.get('description', '')
    }
    tasks.append(new_task)
    save_tasks(tasks)

    logger.info('Completed request for /tasks POST method - used to add new task')
    return jsonify({'message': 'Task added'}), 201

# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method - used to fetch all tasks')
    tasks = load_tasks()
    logger.info('Completed request for /tasks GET method - used to fetch all tasks')
    return jsonify(tasks)

# Update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info('Received request for /tasks PUT method - used to update a task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    
    tasks = load_tasks()
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task:
        task['name'] = data['name']
        task['description'] = data.get('description', '')
        save_tasks(tasks)

        logger.info('Completed request for /tasks PUT method - used to update a task')
        return jsonify({'message': 'Task updated'})
    
    return jsonify({'error': 'Task not found'}), 404

# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method - used to delete a task')
    tasks = load_tasks()
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    if task:
        tasks.remove(task)
        save_tasks(tasks)
        logger.info('Completed request for /tasks DELETE method - used to delete a task')
        return jsonify({'message': f'Task with id {task_id} deleted'})
    
    return jsonify({'error': 'Task not found'}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)
