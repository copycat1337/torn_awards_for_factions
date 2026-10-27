# Option 1 — Run Locally (app.py)
pip install -r requirements.txt

# 2. Initialize the database and admin user
python init_db.py

# You'll be prompted for:
# Admin username (min 3 chars)
# Admin password (min 6 chars, typed twice)
# This creates ghost_protocol.db with all tables and default awards.

# 3. Start the app
python app.py



# Option 2 — Run via Docker

# 1. Initialize the database and admin user
python init_db.py

# 2. Build and start
docker compose up -d --build


# 3. Open the app
http://localhost:41321


# Picture size

256×256 px PNG

static/
└── icons/
    ├── first_hit.png
    ├── most_hits.png
    ├── last_hit.png
    ├── bleeder.png
    ├── heals.png
    ├── active.png
    ├── biggest_hit.png
    └── respect.png

can also be used with the existing database 
defualt username and password are

admin 
password 