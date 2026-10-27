from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'change-this-to-a-long-random-string-please'
DB_NAME = 'ghost_protocol.db'

AVATAR_DIR = os.path.join('static', 'uploads', 'avatars')
AWARDS_UPLOAD_DIR = os.path.join('static', 'icons') # NEW
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(AWARDS_UPLOAD_DIR, exist_ok=True) # NEW
os.makedirs(os.path.join('static', 'img'), exist_ok=True)


# ---------- DB HELPERS ----------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------- AUTH DECORATORS ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper


# ---------- AUTH ROUTES ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('hall_of_fame'))

        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- CATEGORY RENDERER ----------
def render_category(category):
    db = get_db()
    users = db.execute(
        "SELECT * FROM users WHERE category = ? ORDER BY username COLLATE NOCASE",
        (category,)
    ).fetchall()

    users_with_awards = []
    for user in users:
        awards = db.execute('''
            SELECT a.id, a.name, a.description, a.icon_url, a.color, ua.count
            FROM user_awards ua
            JOIN awards a ON a.id = ua.award_id
            WHERE ua.user_id = ?
            ORDER BY a.id
        ''', (user['id'],)).fetchall()

        u = dict(user)
        u['awards'] = [dict(a) for a in awards]
        users_with_awards.append(u)

    db.close()

    template_map = {
        'fame':   'hall_of_fame.html',
        'shame':  'hall_of_shame.html',
        'friend': 'friends.html',
    }
    return render_template(template_map[category], users=users_with_awards)


# ---------- PUBLIC PAGES ----------
@app.route('/')
@login_required
def hall_of_fame():
    return render_category('fame')


@app.route('/shame')
@login_required
def hall_of_shame():
    return render_category('shame')


@app.route('/friends')
@login_required
def friends_page():
    return render_category('friend')


@app.route('/awards')
@login_required
def awards_library():
    db = get_db()
    awards = db.execute("SELECT * FROM awards ORDER BY id").fetchall()
    db.close()
    return render_template('awards.html', awards=[dict(a) for a in awards])


# ---------- ADMIN PANEL ----------
@app.route('/admin')
@login_required
def admin_panel():
    if session.get('role') != 'admin':
        return redirect(url_for('hall_of_fame'))
    return render_template('admin.html')


# ---------- API: USERS CRUD ----------
@app.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    db = get_db()
    users = db.execute('''
        SELECT id, username, role, user_role, torn_id, status,
               category, description, profile_pic, quote
        FROM users ORDER BY id
    ''').fetchall()
    db.close()
    return jsonify([dict(u) for u in users])


@app.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    data = request.json
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    role = data.get('role', 'member')

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 chars"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 chars"}), 400

    db = get_db()
    try:
        db.execute('''
            INSERT INTO users (username, password_hash, role, user_role,
                               torn_id, status, category, description,
                               profile_pic, quote)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            generate_password_hash(password),
            role,
            data.get('user_role', 'Member'),
            data.get('torn_id', 0),
            data.get('status', 'Active'),
            data.get('category', 'fame'),
            data.get('description', ''),
            data.get('profile_pic', '/static/img/default_avatar.png'),
            data.get('quote', 'Silent moves. Loud results.')
        ))
        db.commit()
        new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()
        return jsonify({"status": "success", "id": new_id})
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({"error": "Username already exists"}), 400


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    data = request.json
    db = get_db()

    fields, values = [], []
    for field in ['username', 'role', 'user_role', 'torn_id', 'status',
                  'category', 'description', 'profile_pic', 'quote']:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if data.get('password'):
        fields.append("password_hash = ?")
        values.append(generate_password_hash(data['password']))

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    values.append(user_id)
    db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
    db.commit()
    db.close()
    return jsonify({"status": "success"})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    if user_id == session['user_id']:
        return jsonify({"error": "You cannot delete yourself"}), 400

    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    db.close()
    return jsonify({"status": "success"})


# ---------- API: SELF-EDIT ----------
@app.route('/api/me', methods=['GET'])
@login_required
def api_get_me():
    db = get_db()
    me = db.execute('''
        SELECT id, username, role, user_role, torn_id, status,
               category, description, profile_pic, quote
        FROM users WHERE id = ?
    ''', (session['user_id'],)).fetchone()
    db.close()
    return jsonify(dict(me))


@app.route('/api/me', methods=['PUT'])
@login_required
def api_update_me():
    data = request.json
    db = get_db()

    fields, values = [], []
    if 'quote' in data:
        fields.append("quote = ?")
        values.append(data['quote'])
    if 'profile_pic' in data:
        fields.append("profile_pic = ?")
        values.append(data['profile_pic'])

    if not fields:
        return jsonify({"error": "Nothing to update"}), 400

    values.append(session['user_id'])
    db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
    db.commit()
    db.close()
    return jsonify({"status": "success"})


# ---------- API: AVATAR UPLOAD ----------
def _save_avatar(file):
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXT:
        return None, "Invalid file type"
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(AVATAR_DIR, fname)
    file.save(path)
    return f"/static/uploads/avatars/{fname}", None


@app.route('/api/me/avatar', methods=['POST'])
@login_required
def api_upload_my_avatar():
    if 'avatar' not in request.files:
        return jsonify({"error": "No file"}), 400
    url, err = _save_avatar(request.files['avatar'])
    if err:
        return jsonify({"error": err}), 400

    db = get_db()
    db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (url, session['user_id']))
    db.commit()
    db.close()
    return jsonify({"status": "success", "profile_pic": url})


@app.route('/api/users/<int:user_id>/avatar', methods=['POST'])
@admin_required
def api_upload_user_avatar(user_id):
    if 'avatar' not in request.files:
        return jsonify({"error": "No file"}), 400
    url, err = _save_avatar(request.files['avatar'])
    if err:
        return jsonify({"error": err}), 400

    db = get_db()
    db.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (url, user_id))
    db.commit()
    db.close()
    return jsonify({"status": "success", "profile_pic": url})


# ---------- API: AWARDS CRUD ----------
@app.route('/api/awards', methods=['GET'])
@admin_required
def api_get_awards():
    db = get_db()
    awards = db.execute("SELECT * FROM awards ORDER BY id").fetchall()
    db.close()
    return jsonify([dict(a) for a in awards])


@app.route('/api/awards', methods=['POST'])
@admin_required
def api_create_award():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "Award name required"}), 400

    db = get_db()
    try:
        db.execute('''
            INSERT INTO awards (name, description, how_to_earn, icon_url, icon_filename, color)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            name,
            data.get('description', ''),
            data.get('how_to_earn', ''),
            data.get('icon_url', '/static/icons/default.png'),
            data.get('icon_filename', ''),
            data.get('color', '#00ffcc')
        ))
        db.commit()
        new_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.close()
        return jsonify({"status": "success", "id": new_id})
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({"error": "Award name already exists"}), 400


@app.route('/api/awards/<int:award_id>', methods=['PUT'])
@admin_required
def api_update_award(award_id):
    data = request.json
    db = get_db()
    fields, values = [], []
    for field in ['name', 'description', 'how_to_earn', 'icon_url', 'icon_filename', 'color']:
        if field in data:
            fields.append(f"{field} = ?")
            values.append(data[field])

    if not fields:
        return jsonify({"error": "No fields"}), 400

    values.append(award_id)
    db.execute(f"UPDATE awards SET {', '.join(fields)} WHERE id = ?", values)
    db.commit()
    db.close()
    return jsonify({"status": "success"})


@app.route('/api/awards/<int:award_id>', methods=['DELETE'])
@admin_required
def api_delete_award(award_id):
    db = get_db()
    db.execute("DELETE FROM awards WHERE id = ?", (award_id,))
    db.commit()
    db.close()
    return jsonify({"status": "success"})


# ---------- API: AWARD ICON UPLOAD (NEW) ----------
def _save_award_icon(file):
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXT:
        return None, "Invalid file type"
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(AWARDS_UPLOAD_DIR, fname)
    file.save(path)
    return f"/static/icons/{fname}", fname, None


@app.route('/api/awards/<int:award_id>/icon', methods=['POST'])
@admin_required
def api_upload_award_icon(award_id):
    if 'icon' not in request.files:
        return jsonify({"error": "No file"}), 400
    url, fname, err = _save_award_icon(request.files['icon'])
    if err:
        return jsonify({"error": err}), 400

    db = get_db()
    db.execute(
        "UPDATE awards SET icon_url = ?, icon_filename = ? WHERE id = ?",
        (url, fname, award_id)
    )
    db.commit()
    db.close()
    return jsonify({"status": "success", "icon_url": url, "icon_filename": fname})


# ---------- API: ASSIGN AWARDS (STACKING) ----------
@app.route('/api/users/<int:user_id>/awards', methods=['GET'])
@admin_required
def api_user_awards(user_id):
    db = get_db()
    rows = db.execute('''
        SELECT a.id, a.name, a.icon_url, a.color, ua.count, ua.last_earned
        FROM user_awards ua
        JOIN awards a ON a.id = ua.award_id
        WHERE ua.user_id = ?
    ''', (user_id,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/add_award', methods=['POST'])
@admin_required
def api_add_award():
    data = request.json
    user_id = data.get('user_id')
    award_id = data.get('award_id')
    amount = int(data.get('amount', 1))

    if not user_id or not award_id:
        return jsonify({"error": "user_id and award_id required"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT id, count FROM user_awards WHERE user_id = ? AND award_id = ?",
        (user_id, award_id)
    ).fetchone()

    if existing:
        new_count = existing['count'] + amount
        db.execute('''
            UPDATE user_awards
            SET count = ?, last_earned = CURRENT_DATE
            WHERE id = ?
        ''', (new_count, existing['id']))
    else:
        db.execute('''
            INSERT INTO user_awards (user_id, award_id, count)
            VALUES (?, ?, ?)
        ''', (user_id, award_id, amount))

    db.commit()
    db.close()
    return jsonify({"status": "success"})


@app.route('/api/remove_award', methods=['POST'])
@admin_required
def api_remove_award():
    data = request.json
    user_id = data.get('user_id')
    award_id = data.get('award_id')

    db = get_db()
    existing = db.execute(
        "SELECT id, count FROM user_awards WHERE user_id = ? AND award_id = ?",
        (user_id, award_id)
    ).fetchone()

    if not existing:
        db.close()
        return jsonify({"error": "Award not assigned"}), 404

    if existing['count'] > 1:
        db.execute("UPDATE user_awards SET count = count - 1 WHERE id = ?", (existing['id'],))
    else:
        db.execute("DELETE FROM user_awards WHERE id = ?", (existing['id'],))

    db.commit()
    db.close()
    return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=41321, debug=False)