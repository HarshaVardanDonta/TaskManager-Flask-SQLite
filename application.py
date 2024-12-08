from flask import Flask, jsonify, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory task list (simulating a database)
tasks = []

app = Flask(__name__)

# Helper function to simulate CRUD operations on in-memory data
def load_tasks():
    return tasks

def save_tasks():
    # In this case, no need to persist, as data is in memory
    pass

# Serve the frontend
@app.route('/')
def home():
    logger.info('rendered html page')
    return 'Task Manager - Use the API to manage tasks'

# Add a new task
@app.route('/tasks', methods=['POST'])
def add_task():
    logger.info('Received request for /tasks POST method - used to add new task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    task = {
        'id': len(tasks) + 1,  # Assigning a new ID based on the list length
        'name': data['name'],
        'description': data.get('description', '')
    }
    tasks.append(task)  # Adding the task to the in-memory list
    logger.info('Completed request for /tasks POST method - used to add new task')
    return jsonify({'message': 'Task added', 'task': task}), 201

# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method - used to fetch all tasks')
    tasks_list = load_tasks()  # Get tasks from the in-memory list
    logger.info('Completed request for /tasks GET method - used to fetch all tasks')
    return jsonify(tasks_list)

# Update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    logger.info('Received request for /tasks PUT method - used to update a task')
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task:
        task['name'] = data['name']
        task['description'] = data.get('description', '')
        logger.info('Completed request for /tasks PUT method - used to update a task')
        return jsonify({'message': 'Task updated', 'task': task})
    return jsonify({'error': 'Task not found'}), 404

# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method - used to delete a task')
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]  # Removing the task from the list
    logger.info('Completed request for /tasks DELETE method - used to delete a task')
    return jsonify({'message': f'Task with id {task_id} deleted'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)
