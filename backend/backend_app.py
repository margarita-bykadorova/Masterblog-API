from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)


@app.route('/api/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()
    if "title" not in new_post:
        return jsonify({"error": "Title is missing"}), 400
    elif "content" not in new_post:
        return jsonify({"error": "Content is missing"}), 400
    else:
        new_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_id
        POSTS.append(new_post)
        return jsonify(new_post), 201


@app.route('/api/posts/<id>', methods=['DELETE'])
def delete_post(id):
    post_id = int(id)
    for post in POSTS:
        if post["id"] == post_id:
            POSTS.remove(post)
            return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route('/api/posts/<id>', methods=['PUT'])
def update_post(id):
    post_id = int(id)
    for post in POSTS:
        if post["id"] == post_id:
            new_data = request.get_json()
            post.update(new_data)
            return jsonify(post)

    return jsonify({"error": "Post Not Found"}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title = request.args.get('title')
    content = request.args.get('content')

    # Return empty list if no query provided
    if not title and not content:
        return jsonify([]), 200

    filtered = []
    for post in POSTS:
        post_title = post["title"].lower()
        post_content = post["content"].lower()

        conditions = []
        if title:
            conditions.append(title.lower() in post_title)
        if content:
            conditions.append(content.lower() in post_content)
        if any(conditions):
            filtered.append(post)

    return jsonify(filtered), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
