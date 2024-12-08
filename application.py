from flask import Flask, jsonify, request, render_template
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLiteCloud API endpoint and API key
endpoint = "sqlitecloud://culptoevhk.sqlite.cloud:8860/chinook.sqlite?apikey=bahtndRsnM5Lgl6PbGJ1KuThwT7YIipGxh65uDApnlU"
api_key = "bahtndRsnM5Lgl6PbGJ1KuThwT7YIipGxh65uDApnlU"

# Headers for API requests
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

app = Flask(__name__)

# Helper function to interact with SQLiteCloud API
def query_db(query, args=(), one=False):
    # Preparing the query payload
    query_payload = {'query': query}
    
    # Sending POST request to SQLiteCloud endpoint
    response = requests.post(endpoint, json=query_payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None if one else data
    else:
        logger.error(f"Error querying SQLiteCloud: {response.status_code} - {response.text}")
        return []

# Serve the frontend
@app.route('/')
def home():
    logger.info('Rendered HTML page')
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
    logger.info('Completed request for /tasks POST method - added new task')
    return jsonify({'message': 'Task added'}), 201

# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    logger.info('Received request for /tasks GET method - fetching all tasks')
    tasks = query_db('SELECT * FROM tasks')
    logger.info('Completed request for /tasks GET method - fetched all tasks')
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
        logger.info('Completed request for /tasks PUT method - updated task')
        return jsonify({'message': 'Task updated'})
    return jsonify({'error': 'Task not found'}), 404

# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    logger.info('Received request for /tasks DELETE method - deleting a task')
    query_db('DELETE FROM tasks WHERE id = ?', (task_id,))
    logger.info('Completed request for /tasks DELETE method - deleted task')
    return jsonify({'message': f'Task with id {task_id} deleted'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8055)
