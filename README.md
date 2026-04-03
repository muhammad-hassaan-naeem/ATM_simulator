# ATM Simulator

A desktop ATM simulation built with Python and Tkinter.

## Features

- **Sign Up** — 3-step registration with personal details, demographics, and account type
- **Login** — Card number + PIN authentication with lockout after 3 failed attempts
- **Dashboard** — Deposit, withdraw, transaction history, and PIN change
- **Audio feedback** — Sound cues for each action
- **Dual database backend** — SQLite (default, zero setup) or MySQL

---

## Requirements

- Python 3.10 or later
- Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Quick Start (SQLite — recommended)

SQLite requires no server. Just run:

```bash
python main.py
```

The database file `atm.db` is created automatically on first run.

---

## MySQL Setup (optional)

1. Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

2. Edit `.env` and set:

```
DB_BACKEND=mysql
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=atm
```

3. Create the `atm` database in MySQL:

```sql
CREATE DATABASE atm CHARACTER SET utf8mb4;
```

4. Install the MySQL driver:

```bash
pip install mysql-connector-python
```

5. Run the app — tables are created automatically:

```bash
python main.py
```

---

## Security notes

- PINs are hashed with **bcrypt** — they are never stored in plain text.
- Database credentials are stored in `.env`, which is excluded from version control via `.gitignore`.
- Cards are **permanently blocked** in the database after 3 failed PIN attempts.

---

## Project structure

```
ATM_simulator/
├── main.py          # Entry point and home screen
├── login.py         # Login window
├── signup.py        # 3-step registration flow
├── dashboard.py     # Post-login ATM operations
├── database.py      # All DB CRUD operations
├── db_config.py     # Connection factory (SQLite / MySQL)
├── sound.py         # Audio playback (pygame.mixer)
├── icons/           # UI images
├── sounds/          # WAV audio files
├── requirements.txt # Python dependencies
├── .env.example     # Environment variable template
└── .gitignore
```

---

## Dependencies

| Package         | Purpose                        |
|----------------|-------------------------------|
| Pillow          | Image loading and resizing     |
| pygame          | Cross-platform audio playback  |
| bcrypt          | Secure PIN hashing             |
| python-dotenv   | Load credentials from .env     |
| mysql-connector-python | MySQL backend (optional) |
