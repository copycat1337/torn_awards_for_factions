# 👻 Ghost Protocol Awards

A simple awards and recognition website for your Torn faction. Track faction achievements with custom award icons and manage awards through the web app.

---

## ✨ Features

- 🏆 Awards for faction achievements
- 🖼️ Custom PNG icons for each award
- 🗄️ SQLite database
- 🔐 Admin login
- 🐳 Run locally with Python or using Docker Compose
- ♻️ Supports use with an existing database

## 🚀 Getting Started

Choose **one** of the installation methods below.

### Option 1: Run locally with Python

#### 1. Install dependencies

Run this command from the project directory:

```bash
pip install -r requirements.txt
```

#### 2. Initialize the database and admin account

```bash
python init_db.py
```

Follow the prompts to create your admin account:

- **Username:** at least 3 characters
- **Password:** at least 6 characters; enter it twice to confirm

This creates `ghost_protocol.db`, sets up the required tables, and adds the default awards.

> **Using an existing database?** Back it up before running initialization. Only run `init_db.py` against an existing database if you have confirmed that the script is safe to use with it.

#### 3. Start the application

```bash
python app.py
```

Open the local address shown in the terminal, if one is displayed.

---

### Option 2: Run with Docker Compose

#### 1. Initialize the database and admin account

From the project directory, run:

```bash
python init_db.py
```

Follow the prompts to create your admin username and password.

#### 2. Build and start the app

```bash
docker compose up -d --build
```

#### 3. Open the app

Visit:

**http://localhost:41321**

#### Useful Docker commands

View application logs:

```bash
docker compose logs -f
```

Stop the app:

```bash
docker compose down
```

Start it again:

```bash
docker compose up -d
```

> **Database note:** Make sure `ghost_protocol.db` is stored in a persistent location used by your Docker setup. Back up the database before rebuilding, migrating, or replacing files.

## 🖼️ Custom Award Icons

You can replace the award icons with your own images.

| Setting | Requirement |
| --- | --- |
| Format | PNG |
| Recommended size | 256 × 256 pixels |
| Directory | `static/icons/` |

Keep the filenames exactly as shown:

```text
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
```

To customize an award, replace its corresponding PNG file while keeping the same filename. Using 256 × 256 pixel images is recommended for consistency.

## 🔑 Default Login

If your existing database or setup uses the default credentials, the login may be:

- **Username:** `admin`
- **Password:** `password`

> ⚠️ **Security warning:** These default credentials are public and unsafe for an internet-accessible deployment. Change the password immediately if the application supports it. If it does not, configure a secure admin password using the project's supported account-management method before exposing the app to the internet. Never reuse the default password.

When setting up a new database, use the `init_db.py` prompts to create a unique admin password.

## 🗃️ Using an Existing Database

The application can also be used with an existing database. Before changing application files or initializing the database:

1. Stop the application.
2. Make a backup copy of `ghost_protocol.db`.
3. Keep the database in the location expected by the app or Docker configuration.
4. Start the application and verify that your existing awards and data are still present.

Do not delete or replace your database unless you have a verified backup.

## 🛠️ Troubleshooting

- **The page will not open:** Confirm the app is running and check the terminal output or `docker compose logs -f`.
- **Docker is running but the page is unavailable:** Check that port `41321` is published in your Compose configuration and is not already in use.
- **Icons are missing:** Confirm the PNG files are in `static/icons/` and that their filenames match the list above.
- **Database or login issues:** Check the application logs and verify that the app is using the expected database file.

## 📄 License

Add a license section here if you intend to publish or distribute the repository. If you already have a `LICENSE` file, link to or name that license here.
