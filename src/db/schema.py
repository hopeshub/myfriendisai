"""SQLite schema creation for the AI companion tracker."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "tracker.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS subreddit_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    snapshot_date DATE NOT NULL,
    data_source TEXT NOT NULL DEFAULT 'json_endpoint',
    subscribers INTEGER,
    active_users INTEGER,
    visitors_7d INTEGER,
    contributions_7d INTEGER,
    posts_today INTEGER,
    avg_comments_per_post REAL,
    avg_score_per_post REAL,
    unique_authors INTEGER,
    unique_post_authors_7d INTEGER,
    unique_comment_authors_7d INTEGER,
    unique_contributors_7d INTEGER,
    raw_about_json TEXT,
    raw_listing_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subreddit, snapshot_date)
);

CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT NOT NULL,
    title TEXT,
    author TEXT,
    created_utc INTEGER,
    score INTEGER,
    num_comments INTEGER,
    upvote_ratio REAL,
    is_self BOOLEAN,
    selftext TEXT,
    url TEXT,
    collected_date DATE NOT NULL,
    data_source TEXT NOT NULL DEFAULT 'json_endpoint',
    raw_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keyword_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    keyword_category TEXT NOT NULL,
    keyword TEXT NOT NULL,
    search_date DATE NOT NULL,
    hit_count INTEGER,
    sample_post_ids TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subreddit, keyword, search_date)
);

CREATE TABLE IF NOT EXISTS keyword_counts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subreddit TEXT NOT NULL,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'post_title',
    count INTEGER DEFAULT 0,
    matched_terms TEXT,
    post_sample_ids TEXT,
    UNIQUE(subreddit, date, category, source)
);

CREATE TABLE IF NOT EXISTS scanned_posts (
    post_id TEXT NOT NULL,
    scan_date TEXT NOT NULL,
    PRIMARY KEY(post_id, scan_date)
);

CREATE TABLE IF NOT EXISTS subreddit_config (
    subreddit TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    tier INTEGER,
    display_name TEXT,
    description TEXT,
    added_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS post_keyword_tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     TEXT    NOT NULL,
    subreddit   TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    matched_term TEXT   NOT NULL,
    post_date   DATE    NOT NULL,
    source      TEXT    NOT NULL DEFAULT 'post',
    UNIQUE(post_id, category, matched_term, source)
);

CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    post_id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    author TEXT,
    body TEXT,
    score INTEGER,
    depth INTEGER NOT NULL DEFAULT 0,
    parent_id TEXT,
    created_utc INTEGER,
    permalink TEXT,
    collected_at TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE INDEX IF NOT EXISTS idx_comments_post_id
    ON comments(post_id);

CREATE INDEX IF NOT EXISTS idx_comments_subreddit_created
    ON comments(subreddit, created_utc);

CREATE TABLE IF NOT EXISTS comment_keyword_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL,
    post_id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    category TEXT NOT NULL,
    matched_term TEXT NOT NULL,
    post_date DATE NOT NULL,
    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE INDEX IF NOT EXISTS idx_comment_hits_post_id
    ON comment_keyword_hits(post_id);

CREATE INDEX IF NOT EXISTS idx_comment_hits_keyword
    ON comment_keyword_hits(category, matched_term);

CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_hits_unique
    ON comment_keyword_hits(comment_id, category, matched_term);

CREATE TABLE IF NOT EXISTS comment_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    comments_collected INTEGER NOT NULL DEFAULT 0,
    collected_at TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_log_post
    ON comment_collection_log(post_id);

CREATE INDEX IF NOT EXISTS idx_pkt_subreddit_date
    ON post_keyword_tags(subreddit, post_date);

CREATE INDEX IF NOT EXISTS idx_pkt_category_date
    ON post_keyword_tags(category, post_date);

CREATE INDEX IF NOT EXISTS idx_posts_subreddit_created
    ON posts(subreddit, created_utc);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Run any needed schema migrations on an existing database."""
    # Check if keyword_counts has source column
    cols = [row[1] for row in conn.execute("PRAGMA table_info(keyword_counts)").fetchall()]
    if "source" not in cols:
        # Drop old table and recreate — keyword_counts data is regenerated daily
        conn.execute("DROP TABLE IF EXISTS keyword_counts")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS keyword_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subreddit TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'post_title',
                count INTEGER DEFAULT 0,
                matched_terms TEXT,
                post_sample_ids TEXT,
                UNIQUE(subreddit, date, category, source)
            )
        """)
        conn.commit()

    # Create scanned_posts if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scanned_posts (
            post_id TEXT NOT NULL,
            scan_date TEXT NOT NULL,
            PRIMARY KEY(post_id, scan_date)
        )
    """)

    # Add rolling-7d contributor columns if missing (migration 002)
    snap_cols = {row[1] for row in conn.execute("PRAGMA table_info(subreddit_snapshots)").fetchall()}
    for col in ("unique_post_authors_7d", "unique_comment_authors_7d", "unique_contributors_7d"):
        if col not in snap_cols:
            conn.execute(f"ALTER TABLE subreddit_snapshots ADD COLUMN {col} INTEGER")
    conn.commit()


def initialize(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create the database and all tables if they don't exist."""
    conn = get_connection(db_path)
    conn.executescript(SCHEMA)
    _migrate(conn)
    conn.commit()
    return conn
