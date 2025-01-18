from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Example data store (in-memory database for simplicity)
data_store = {
    "users": []
}

# Route to get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({"users": data_store["users"]}), 200

# Route to create a new user
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        user = request.json
        if not user or not user.get("name") or not user.get("email"):
            return jsonify({"error": "Invalid input"}), 400

        user_id = len(data_store["users"]) + 1
        user["id"] = user_id
        data_store["users"].append(user)
        return jsonify(user), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to get a specific user by ID
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in data_store["users"] if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

# Route to update a user's information
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = next((u for u in data_store["users"] if u["id"] == user_id), None)
        if not user:
            return jsonify({"error": "User not found"}), 404

        updated_data = request.json
        if not updated_data:
            return jsonify({"error": "Invalid input"}), 400

        user.update(updated_data)
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to delete a user
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global data_store
    user = next((u for u in data_store["users"] if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data_store["users"] = [u for u in data_store["users"] if u["id"] != user_id]
    return jsonify({"message": "User deleted"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
