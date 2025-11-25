"""Simple blog posts REST API using Flask.

Provides endpoints to list, create, update, delete and search posts
stored in an in-memory list.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Return all posts, optionally sorted by title or content.

    Query parameters:
        sort: "title" or "content" (optional)
        direction: "asc" or "desc" (optional, defaults to "asc")

    If no sort is provided, posts are returned in their original order.
    """
    sort = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort is None:
        return jsonify(POSTS), 200

    if sort not in ("title", "content"):
        return jsonify({"error": "Invalid sort. Use 'title' or 'content'."}), 400

    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

    reverse = (direction == "desc")
    sorted_posts = sorted(
        POSTS,
        key=lambda post: post[sort].lower(),
        reverse=reverse,
    )
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Create a new post.

    Expects JSON body with:
        title: non-empty string
        content: non-empty string
    """
    new_post = request.get_json()

    if not new_post:
        return jsonify({"error": "JSON body required"}), 400

    title = new_post.get("title", "").strip()
    content = new_post.get("content", "").strip()

    if not title:
        return jsonify({"error": "Valid title is required"}), 400
    if not content:
        return jsonify({"error": "Valid content is required"}), 400

    new_id = max(post["id"] for post in POSTS) + 1
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete a post by its ID."""
    for post in POSTS:
        if post["id"] == post_id:
            POSTS.remove(post)
            return jsonify({"message": (f"Post {post_id} has been deleted.")}), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update an existing post by ID.

    Expects JSON body with optional fields:
        title: string
        content: string
    """
    new_data = request.get_json()
    if new_data is None:
        new_data = {}

    for post in POSTS:
        if post["id"] == post_id:
            if "title" in new_data:
                post["title"] = new_data["title"]
            if "content" in new_data:
                post["content"] = new_data["content"]
            return jsonify(post), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title and/or content.

    Query parameters:
        title: substring to search in the title (optional)
        content: substring to search in the content (optional)

    Returns a list of matching posts. If no query is provided,
    an empty list is returned.
    """
    title = request.args.get("title")
    content = request.args.get("content")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)