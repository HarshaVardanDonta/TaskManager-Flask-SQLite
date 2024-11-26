from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

# Helper function to interact with the database
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# Add a new task
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    query_db('INSERT INTO tasks (name, description) VALUES (?, ?)',
             (data['name'], data.get('description', '')))
    return jsonify({'message': 'Task added'}), 201

# View all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = query_db('SELECT * FROM tasks')
    return jsonify([dict(task) for task in tasks])

# Update an existing task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    if not data or 'name' not in data:
        return jsonify({'error': 'Task name is required'}), 400
    result = query_db('UPDATE tasks SET name = ?, description = ? WHERE id = ?',
                      (data['name'], data.get('description', ''), task_id))
    if result:
        return jsonify({'message': 'Task updated'})
    return jsonify({'error': 'Task not found'}), 404

# Delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    query_db('DELETE FROM tasks WHERE id = ?', (task_id,))
    return jsonify({'message': f'Task with id {task_id} deleted'})

if __name__ == '__main__':
    app.run(debug=True)
