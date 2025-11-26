"""Simple blog posts REST API using Flask.

Provides endpoints to list, create, update, delete and search posts
stored in an in-memory list.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

# -------------------------
# APP SETUP
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# IN-MEMORY DATABASE
# -------------------------
POSTS = [
    {
        "id": 1,
        "title": "My First Blog Post",
        "content": "This is the content of my first blog post.",
        "author": "Your Name",
        "date": "2023-06-07"
    },
    {
        "id": 2,
        "title": "My Second Blog Post",
        "content": "This is the content of my second blog post.",
        "author": "Your Name",
        "date": "2023-06-08"
    }
]

# -------------------------
# SWAGGER SETUP
# -------------------------

SWAGGER_URL="/api/docs"
API_URL="/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# -------------------------
# ROUTES
# -------------------------
@app.route("/api/posts", methods=["GET"])
def get_posts():
    """Return all posts, optionally sorted by title, content, author or date.

    Query parameters:
        sort: "title", "content", "author" or "date" (optional)
        direction: "asc" or "desc" (optional, defaults to "asc")

    If no sort is provided, posts are returned in their original order.
    """
    sort = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort is None:
        return jsonify(POSTS), 200

    if sort not in ("title", "content", "author", "date"):
        return jsonify({"error": "Invalid sort request."}), 400

    if direction not in ("asc", "desc"):
        return jsonify({"error": "Invalid direction."}), 400

    reverse = (direction == "desc")

    if sort == "date":
        # Parse date string "YYYY-MM-DD" into a real date
        def key_func(post):
            return datetime.strptime(post["date"], "%Y-%m-%d")
    else:
        # For title, content, author → case-insensitive string sort
        def key_func(post):
            return post[sort].lower()

    sorted_posts = sorted(POSTS, key=key_func, reverse=reverse)
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Create a new post.

    Expects JSON body with:
    title, content, author and date.
    """
    new_post = request.get_json()

    if not new_post:
        return jsonify({"error": "JSON body required"}), 400

    title = new_post.get("title", "").strip()
    content = new_post.get("content", "").strip()
    author = new_post.get("author", "").strip()
    date = new_post.get("date", "").strip()

    if not title:
        return jsonify({"error": "Valid title is required"}), 400
    if not content:
        return jsonify({"error": "Valid content is required"}), 400
    if not author:
        return jsonify({"error": "Valid author is required"}), 400
    if not date:
        return jsonify({"error": "Valid date is required"}), 400

    new_id = max(post["id"] for post in POSTS) + 1
    new_post = {
        "id": new_id,
        "title": title,
        "content": content,
        "author": author,
        "date": date
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete a post by its ID."""
    for post in POSTS:
        if post["id"] == post_id:
            POSTS.remove(post)
            return jsonify({"message": f"Post {post_id} has been deleted."}), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update an existing post by ID.

    Expects JSON body with optional fields:
    title, content, author, date.
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
            if "author" in new_data:
                post["author"] = new_data["author"]
            if "date" in new_data:
                post["date"] = new_data["date"]
            return jsonify(post), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title, content, author and/or date.

    Query parameters (all optional, can be combined):
        title: substring to search in the title
        content: substring to search in the content
        author: substring to search in the author
        date: exact date to match (YYYY-MM-DD)

    Returns a list of matching posts. If no query is provided,
    an empty list is returned.
    """
    title = request.args.get("title")
    content = request.args.get("content")
    author = request.args.get("author")
    date = request.args.get("date")

    # If no filters provided, return an empty list
    if not any([title, content, author, date]):
        return jsonify([]), 200

    filtered = []
    for post in POSTS:
        conditions = []

        if title:
            conditions.append(title.lower() in post["title"].lower())
        if content:
            conditions.append(content.lower() in post["content"].lower())
        if author:
            conditions.append(author.lower() in post["author"].lower())
        if date:
            # Exact match for date
            conditions.append(date == post["date"])

        if conditions and all(conditions):
            # All provided filters must match this post
            filtered.append(post)

    return jsonify(filtered), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
