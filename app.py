from flask import Flask, render_template, request, jsonify, g
import sqlite3

app = Flask(__name__)

# Database configuration
DATABASE = 'db.sqlite3'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                content TEXT,
                reactions INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                username TEXT,
                text TEXT,
                FOREIGN KEY(post_id) REFERENCES posts(id)
            )
        ''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.json
    username = data.get("username", "Anonymous")
    content = data.get("content")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO posts (username, content) VALUES (?, ?)", (username, content))
    db.commit()
    post_id = cursor.lastrowid

    return jsonify({"id": post_id, "username": username, "content": content, "reactions": 0}), 201

@app.route('/view_posts', methods=['GET'])
def view_posts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, username, content, reactions FROM posts")
    posts = cursor.fetchall()
    results = []
    for post in posts:
        post_id, username, content, reactions = post
        cursor.execute("SELECT username, text FROM comments WHERE post_id=?", (post_id,))
        comments = [{"username": c[0], "text": c[1]} for c in cursor.fetchall()]
        results.append({
            "id": post_id,
            "username": username,
            "content": content,
            "reactions": reactions,
            "comments": comments
        })
    return jsonify(results)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json
    post_id = data.get("post_id")
    username = data.get("username", "Anonymous")
    text = data.get("text")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (post_id, username, text) VALUES (?, ?, ?)", (post_id, username, text))
    db.commit()

    return jsonify({"message": "Comment added successfully"}), 200

@app.route('/add_reaction/<int:post_id>', methods=['POST'])
def add_reaction(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE posts SET reactions = reactions + 1 WHERE id=?", (post_id,))
    db.commit()
    return jsonify({"message": "Reaction added successfully"}), 200

@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM posts WHERE id=?", (post_id,))
    cursor.execute("DELETE FROM comments WHERE post_id=?", (post_id,))
    db.commit()
    return jsonify({"message": "Post deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
