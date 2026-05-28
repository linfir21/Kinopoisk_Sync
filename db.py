import sqlite3
from datetime import datetime
from config import DB_PATH

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            kp_id INTEGER PRIMARY KEY,
            title_ru TEXT NOT NULL,
            title_en TEXT,
            year INTEGER,
            description TEXT,
            short_description TEXT,
            poster_url TEXT,
            rating_kp REAL,
            rating_imdb REAL,
            genres TEXT,
            duration INTEGER,
            actors TEXT,
            director TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            kp_id INTEGER NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('watched', 'watchlist')),
            user_rating INTEGER,
            watched_date TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, kp_id, status)
        )
    """)
    
    conn.commit()
    conn.close()

def save_movie(conn, data: dict):
    c = conn.cursor()
    c.execute("""
        INSERT INTO movies
        (kp_id, title_ru, title_en, year, poster_url, rating_kp, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(kp_id) DO UPDATE SET
            title_ru = COALESCE(excluded.title_ru, movies.title_ru),
            title_en = COALESCE(excluded.title_en, movies.title_en),
            year = COALESCE(excluded.year, movies.year),
            poster_url = COALESCE(excluded.poster_url, movies.poster_url),
            rating_kp = COALESCE(excluded.rating_kp, movies.rating_kp),
            last_updated = excluded.last_updated
    """, (
        data["kp_id"],
        data.get("title_ru", data.get("title", "")),
        data.get("title_en"),
        data.get("year"),
        data.get("poster_url"),
        data.get("rating_kp"),
        datetime.now().isoformat()
    ))
    conn.commit()

def save_user_movie(conn, user_id: str, data: dict):
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_movies
        (user_id, kp_id, status, user_rating, watched_date)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, kp_id, status) DO UPDATE SET
            user_rating = COALESCE(excluded.user_rating, user_movies.user_rating),
            watched_date = COALESCE(excluded.watched_date, user_movies.watched_date),
            synced_at = CURRENT_TIMESTAMP
    """, (
        user_id,
        data["kp_id"],
        data["status"],
        data.get("user_rating"),
        data.get("watched_date")
    ))
    conn.commit()

def get_user_movies(conn, user_id: str, status: str = None):
    c = conn.cursor()
    if status:
        c.execute("""
            SELECT m.*, um.user_rating, um.status, um.watched_date
            FROM movies m
            JOIN user_movies um ON m.kp_id = um.kp_id
            WHERE um.user_id = ? AND um.status = ?
            ORDER BY um.watched_date DESC NULLS LAST, m.year DESC
        """, (user_id, status))
    else:
        c.execute("""
            SELECT m.*, um.user_rating, um.status, um.watched_date
            FROM movies m
            JOIN user_movies um ON m.kp_id = um.kp_id
            WHERE um.user_id = ?
            ORDER BY um.status, m.year DESC
        """, (user_id,))
    return c.fetchall()

def get_common_movies(conn, status: str):
    c = conn.cursor()
    c.execute("""
        SELECT m.*, 
               u1.user_rating as user1_rating, 
               u2.user_rating as user2_rating
        FROM movies m
        JOIN user_movies u1 ON m.kp_id = u1.kp_id AND u1.user_id = 'user1' AND u1.status = ?
        JOIN user_movies u2 ON m.kp_id = u2.kp_id AND u2.user_id = 'user2' AND u2.status = ?
        ORDER BY m.year DESC
    """, (status, status))
    return c.fetchall()

def get_movie(conn, kp_id: int):
    c = conn.cursor()
    c.execute("SELECT * FROM movies WHERE kp_id = ?", (kp_id,))
    return c.fetchone()

def get_all_movies(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM movies ORDER BY title_ru")
    return c.fetchall()