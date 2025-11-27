"""Simple blog posts REST API using Flask.

Provides endpoints to list, create, update, delete and search posts
stored in a JSON file on disk.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime
import json

DATA_FILE = "storage.json"

# -------------------------
# APP SETUP
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# HELPERS
# -------------------------
def get_data():
    """Return all saved blog posts from the JSON storage file.

    If the file does not exist, return an empty list.
    If the file content is invalid, return an empty list as well.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if not isinstance(data, list):
                return []
            return data
    except FileNotFoundError:
        # First run: file doesn't exist yet
        return []
    except json.JSONDecodeError:
        # File exists but is not valid JSON
        return []


def save_data(data):
    """Write updated blog posts to the JSON storage file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=4)
    except OSError:
        # Writing failed (disk permission, full disk, etc.)
        raise RuntimeError("Failed to save data to JSON file.")

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
    posts = get_data()
    sort = request.args.get("sort")
    direction = request.args.get("direction", "asc")

    if sort is None:
        return jsonify(posts), 200

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

    sorted_posts = sorted(posts, key=key_func, reverse=reverse)
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Create a new post.

    Expects JSON body with:
    title, content, author and date.
    """
    posts = get_data()
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

        # ✅ Validate date format "YYYY-MM-DD"
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Date must be YYYY-MM-DD"}), 400

    new_id = max((post["id"] for post in posts), default=0) + 1
    new_post = {
        "id": new_id,
        "title": title,
        "content": content,
        "author": author,
        "date": date
    }
    posts.append(new_post)
    try:
        save_data(posts)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete a post by its ID."""
    posts = get_data()
    for post in posts:
        if post["id"] == post_id:
            posts.remove(post)
            try:
                save_data(posts)
            except RuntimeError as exc:
                return jsonify({"error": str(exc)}), 500
            return jsonify({"message": f"Post {post_id} has been deleted."}), 200

    return jsonify({"error": "Post Not Found"}), 404


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update an existing post by ID.

    Expects JSON body with optional fields:
    title, content, author, date.
    """
    posts = get_data()
    new_data = request.get_json()
    if new_data is None:
        new_data = {}

    for post in posts:
        if post["id"] == post_id:
            if "title" in new_data:
                post["title"] = new_data["title"]
            if "content" in new_data:
                post["content"] = new_data["content"]
            if "author" in new_data:
                post["author"] = new_data["author"]
            if "date" in new_data:
                new_date = new_data["date"].strip()
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                except ValueError:
                    return jsonify({"error": "Date must be YYYY-MM-DD"}), 400
                post["date"] = new_date
            try:
                save_data(posts)
            except RuntimeError as exc:
                return jsonify({"error": str(exc)}), 500
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
    posts = get_data()
    title = request.args.get("title")
    content = request.args.get("content")
    author = request.args.get("author")
    date = request.args.get("date")

    # If no filters provided, return an empty list
    if not any([title, content, author, date]):
        return jsonify([]), 200

    filtered = []
    for post in posts:
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
