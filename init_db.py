import os
import sys
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

DB_NAME = 'ghost_protocol.db'
DB_PATH = os.path.abspath(DB_NAME)
UPLOAD_DIR = os.path.join('static', 'uploads', 'avatars')
AWARDS_UPLOAD_DIR = os.path.join('static', 'icons')


def create_tables(cursor):
    print("📦 Creating tables...")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            user_role TEXT DEFAULT 'Member',
            torn_id INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Active',
            category TEXT DEFAULT 'fame',
            description TEXT DEFAULT '',
            profile_pic TEXT DEFAULT '/static/img/default_avatar.png',
            quote TEXT DEFAULT 'Silent moves. Loud results.'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            how_to_earn TEXT DEFAULT '',
            icon_url TEXT,
            icon_filename TEXT,
            color TEXT DEFAULT '#00ffcc'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            award_id INTEGER NOT NULL,
            count INTEGER DEFAULT 1,
            last_earned DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(award_id) REFERENCES awards(id) ON DELETE CASCADE,
            UNIQUE(user_id, award_id)
        )
    ''')

    print("✅ Tables created successfully.")


def migrate_db(cursor):
    print("🔄 Running migrations...")
    cursor.execute("PRAGMA table_info(awards)")
    award_cols = {row[1] for row in cursor.fetchall()}
    if 'icon_filename' not in award_cols:
        cursor.execute("ALTER TABLE awards ADD COLUMN icon_filename TEXT")
        print("  ✅ Added 'icon_filename' column to awards table")
    else:
        print("  ℹ️  'icon_filename' already exists on awards table")
    print("✅ Migrations complete.")


def seed_default_awards(cursor):
    print("🏆 Seeding default awards...")
    default_awards = [
        ("First Hit", "First to land a hit in the war.",
         "Land the very first hit on any enemy in a faction war.",
         "/static/icons/first_hit.png", "first_hit.png", "#ff4d4d"),
        ("Most Hits", "Most hits in the war.",
         "Land more hits than anyone else during the war.",
         "/static/icons/most_hits.png", "most_hits.png", "#ffcc00"),
        ("Last Hit", "Final hit of the war.",
         "Land the very last hit that ends the war.",
         "/static/icons/last_hit.png", "last_hit.png", "#cccccc"),
        ("Biggest Bleeder", "Lost the most health.",
         "Lose the most health across the entire war.",
         "/static/icons/bleeder.png", "bleeder.png", "#b8860b"),
        ("Most Heals", "Healed the most in the war.",
         "Use the most healing items on faction members during war.",
         "/static/icons/heals.png", "heals.png", "#00cc44"),
        ("Most Active", "Most attacks / activity.",
         "Highest total number of attacks and actions during war.",
         "/static/icons/active.png", "active.png", "#00aaff"),
        ("Biggest Hit", "Highest single hit damage.",
         "Land the single highest-damage hit of the war.",
         "/static/icons/biggest_hit.png", "biggest_hit.png", "#a020f0"),
        ("Top Respect", "Highest respect gain.",
         "Earn the most respect for the faction during the war.",
         "/static/icons/respect.png", "respect.png", "#ffaa00"),
    ]
    for name, desc, how, icon, filename, color in default_awards:
        try:
            cursor.execute(
                "INSERT INTO awards (name, description, how_to_earn, icon_url, icon_filename, color) VALUES (?, ?, ?, ?, ?, ?)",
                (name, desc, how, icon, filename, color)
            )
        except sqlite3.IntegrityError:
            pass
    print("✅ Default awards ready.")


def create_admin(cursor):
    print("\n👤 Admin Account Setup")
    print("-" * 30)

    while True:
        username = input("Enter admin username: ").strip()
        if len(username) < 3:
            print("❌ Username must be at least 3 characters.")
            continue
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"❌ Username '{username}' is already taken.")
            continue
        break

    while True:
        password = getpass("Enter admin password: ")
        if len(password) < 6:
            print("❌ Password must be at least 6 characters.")
            continue
        if password != getpass("Confirm admin password: "):
            print("❌ Passwords do not match. Try again.")
            continue
        break

    cursor.execute(
        """INSERT INTO users (username, password_hash, role, user_role, torn_id, status, category, description, quote)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (username, generate_password_hash(password), 'admin', 'Leader', 0, 'Active',
         'fame', '', 'Silent moves. Loud results.')
    )
    print(f"\n✅ Admin '{username}' created successfully!")


def db_is_missing_or_empty():
    """True if the DB doesn't exist, or exists but is 0 bytes (Docker bind mount race)."""
    if not os.path.exists(DB_PATH):
        return True
    try:
        return os.path.getsize(DB_PATH) == 0
    except OSError:
        return True


def main():
    force_admin = '--force-admin' in sys.argv

    print(f"📂 Working directory: {os.getcwd()}")
    print(f"📂 Database path:     {DB_PATH}")
    print()

    overwrite = False
    fresh = db_is_missing_or_empty()

    if fresh:
        print("📂 No database (or empty file) found — starting fresh.")
        # Remove the 0-byte placeholder Docker may have created
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    else:
        if force_admin:
            print("📂 Existing DB found. --force-admin → will prompt for admin credentials.")
        else:
            print(f"📂 Database '{DB_NAME}' found ({os.path.getsize(DB_PATH)} bytes).")
            ans = input("⚠️  Overwrite with a fresh DB? (y/N): ").strip().lower()
            if ans == 'y':
                overwrite = True
                os.remove(DB_PATH)
                print("🗑️  Old database removed.")
                fresh = True
            else:
                print("ℹ️  Keeping existing database. Running migrations only.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(AWARDS_UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join('static', 'img'), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    migrate_db(cursor)

    if fresh or overwrite:
        seed_default_awards(cursor)
        create_admin(cursor)
    elif force_admin:
        create_admin(cursor)
    else:
        print("ℹ️  Skipping seed/admin creation (existing DB kept).")
        print("   Tip: run with --force-admin to add/update an admin anyway.")

    conn.commit()
    conn.close()

    print("\n🎉 Database ready! You can now run 'python app.py'.")


if __name__ == '__main__':
    main()