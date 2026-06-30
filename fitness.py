import os
import sqlite3
import hashlib
import streamlit as st
import google.generativeai as genai
import pycountry
from datetime import datetime, timedelta

# ======================================================================
# 1. ENFORCED FOREIGN-KEY DATABASE ARCHITECTURE LAYER (ALL 14 TABLES)
# ======================================================================
def initialize_database():
    with sqlite3.connect("fitness_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Identity Vault Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY, password_hash TEXT, country TEXT, tier TEXT
            )
        """)
        
        # User AI Intelligence Profile Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_ai_profile (
                username TEXT PRIMARY KEY,
                preferred_training_time TEXT DEFAULT 'Morning',
                favorite_muscle_group TEXT DEFAULT 'Chest',
                motivation_style TEXT DEFAULT 'Discipline',
                consistency_score REAL DEFAULT 100.0,
                risk_of_quitting TEXT DEFAULT 'Low',
                best_training_day TEXT DEFAULT 'Monday',
                injuries TEXT DEFAULT 'None',
                equipment TEXT DEFAULT 'Full Gym',
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                username TEXT, date_stamp TEXT, m1 INTEGER, m2 INTEGER, m3 INTEGER, m4 INTEGER, m5 INTEGER, 
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workout_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date_logged TEXT, 
                workout_title TEXT, duration_mins INTEGER, calories_burned INTEGER, status_tag TEXT, notes TEXT,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_logs (
                username TEXT, date_stamp TEXT, breakfast_notes TEXT, lunch_notes TEXT, 
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress_logs (
                username TEXT, date_stamp TEXT, body_fat REAL, heart_rate INTEGER, 
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                username TEXT PRIMARY KEY, current_trophies INTEGER, rank_title TEXT,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sleep_logs (
                username TEXT, date_stamp TEXT, hours_slept REAL, recovery_score INTEGER, 
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prayer_logs (
                username TEXT, date_stamp TEXT, scripture_streak INTEGER, verses_read TEXT, repairs_used INTEGER, coach_persona TEXT,
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, date_logged TEXT, distance_km REAL, pace_min_km REAL,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS step_history (
                username TEXT, date_stamp TEXT, step_count INTEGER, 
                PRIMARY KEY (username, date_stamp),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                username TEXT PRIMARY KEY, capital_received REAL, asset_currency TEXT,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, category TEXT, user_msg TEXT, timestamp TEXT,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friends_network (
                username TEXT, friend_username TEXT, connection_status TEXT, 
                PRIMARY KEY (username, friend_username),
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS push_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, alert_text TEXT, timestamp TEXT, read_flag INTEGER,
                FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
            )
        """)
        conn.commit()

def calculate_secure_hash(password):
    static_salt = b"STRIKE_FIT_CORE_OS_PREMIUM_SALT_VECTOR_2026_PRODUCTION_VAULT"
    return hashlib.scrypt(password.encode(), salt=static_salt, n=16384, r=8, p=1, dklen=64).hex()

def register_user(username, password, country, preferred_time, fav_muscle, motivation):
    try:
        with sqlite3.connect("fitness_data.db") as conn:
            cursor = conn.cursor()
            p_hash = calculate_secure_hash(password)
            dt_now = datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("INSERT INTO accounts VALUES (?, ?, ?, 'Basic Plan (Free Core)')", (username, p_hash, country))
            cursor.execute("INSERT INTO user_ai_profile VALUES (?, ?, ?, ?, 100.0, 'Low', 'Monday', 'None', 'Full Gym')", (username, preferred_time, fav_muscle, motivation))
            cursor.execute("INSERT INTO daily_metrics VALUES (?, ?, 0, 0, 0, 0, 0)", (username, dt_now))
            cursor.execute("INSERT INTO progress_logs VALUES (?, ?, NULL, NULL)", (username, dt_now))
            cursor.execute("INSERT INTO achievements VALUES (?, 0, 'ROOKIE STRIKER')", (username,))
            cursor.execute("INSERT INTO sleep_logs VALUES (?, ?, NULL, NULL)", (username, dt_now))
            cursor.execute("INSERT INTO prayer_logs VALUES (?, ?, 0, 'None Logged', 0, 'Drill Sergeant 🪖')", (username, dt_now))
            cursor.execute("INSERT INTO step_history VALUES (?, ?, 0)", (username, dt_now))
            cursor.execute("INSERT INTO payments VALUES (?, 0.0, 'Euros €')", (username,))
            cursor.execute("INSERT INTO nutrition_logs VALUES (?, ?, '', '')", (username, dt_now))
            cursor.execute("INSERT INTO friends_network VALUES (?, 'investor_peer', 'VERIFIED')", (username,))
            cursor.execute("INSERT INTO push_alerts (username, alert_text, timestamp, read_flag) VALUES (?, 'Secure production environment initialized cleanly.', ?, 0)", (username, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def verify_user_credentials(username, password):
    with sqlite3.connect("fitness_data.db") as conn:
        cursor = conn.cursor()
        p_hash = calculate_secure_hash(password)
        cursor.execute("SELECT username, tier, country FROM accounts WHERE username=? AND password_hash=?", (username, p_hash))
        return cursor.fetchone()

def fetch_user_data(username, date_stamp):
    with sqlite3.connect("fitness_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tier, country FROM accounts WHERE username=?", (username,))
        acc = cursor.fetchone()
        cursor.execute("SELECT preferred_training_time, favorite_muscle_group, motivation_style, consistency_score, risk_of_quitting, best_training_day, injuries, equipment FROM user_ai_profile WHERE username=?", (username,))
        ai_prof = cursor.fetchone() or ('Morning', 'Chest', 'Discipline', 100.0, 'Low', 'Monday', 'None', 'Full Gym')
        cursor.execute("SELECT m1, m2, m3, m4, m5 FROM daily_metrics WHERE username=? AND date_stamp=?", (username, date_stamp))
        dm = cursor.fetchone() or (0,0,0,0,0)
        cursor.execute("SELECT body_fat, heart_rate FROM progress_logs WHERE username=? AND date_stamp=?", (username, date_stamp))
        pl = cursor.fetchone() or (0.0, 0)
        cursor.execute("SELECT current_trophies, rank_title FROM achievements WHERE username=?", (username,))
        ach = cursor.fetchone() or (0, 'ROOKIE STRIKER')
        cursor.execute("SELECT hours_slept, recovery_score FROM sleep_logs WHERE username=? AND date_stamp=?", (username, date_stamp))
        sl = cursor.fetchone() or (0.0, 0)
        cursor.execute("SELECT scripture_streak, verses_read, repairs_used, coach_persona FROM prayer_logs WHERE username=? AND date_stamp=?", (username, date_stamp))
        pr = cursor.fetchone() or (0, 'None Logged', 0, 'Drill Sergeant 🪖')
        cursor.execute("SELECT step_count FROM step_history WHERE username=? AND date_stamp=?", (username, date_stamp))
        sh = cursor.fetchone() or (0,)
