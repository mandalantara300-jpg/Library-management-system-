"""
CampusShelf - Modern Campus Library Management System
======================================================
A complete, enterprise-grade library management application built with
Python 3 standard-library modules: `http.server`, `sqlite3`, `urllib.request`, and `json`.

Features & Updates:
1. FIXED: Received book workflow in Issued Books part (fixed URL parameter parsing).
2. Typing live search in "Give Book" box: search by Name, Phone, Email, or Unique Member ID (#M-X).
3. Member ID (#M-X) added wherever members appear (Issued table, Give modal, Receive modal, Holds, Members).
4. Strictly Admin / Librarian Mode (student login removed).
5. Interactive KPI summary cards:
   - Total Inventory: switches to Catalog & resets filters.
   - Available Copies: switches to Available part with highlight.
   - Issued Copies: switches to Issued part with highlight.
   - Overdue Loans: opens Overdue Loans details modal with 1-click receive.
   - Pending Fines: opens Fines Breakdown modal with fine details and settlement.
   - Active Holds: switches to Holds (Waitlist) tab.
6. Independent Catalog Scroll: Header, KPI cards, and filters stay locked; only the catalog scrolls.
7. Two distinct parts: 🟢 Available Books vs 🔴 Issued Books.
8. 500 Curated Popular Books with genre, shelf location, ISBN, and cover art.
9. Dark Mode / Light Mode Theme Toggle.
"""

import csv
import io
import json
import os
import sqlite3
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")
PORT = 8000


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT,
                genre TEXT DEFAULT 'General',
                shelf_location TEXT DEFAULT 'Shelf A-01',
                cover_url TEXT,
                status TEXT NOT NULL DEFAULT 'Available',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                member_type TEXT DEFAULT 'Student',
                max_books INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                fine_amount REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'Active',
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                reserve_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Waiting',
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                notice_type TEXT DEFAULT 'Reminder',
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (member_id) REFERENCES members (id)
            )
            """
        )
        conn.commit()

        # Seed 500 books if empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] < 500:
            seed_script = os.path.join(BASE_DIR, "seed_500_books.py")
            if os.path.exists(seed_script):
                import seed_500_books
                seed_500_books.seed_database()


def update_overdue_fines():
    """Calculates $0.50/day overdue fines for all unreturned loans."""
    today = datetime.now()
    with get_db() as conn:
        loans = conn.execute(
            "SELECT id, due_date, status FROM loans WHERE status IN ('Active', 'Overdue')"
        ).fetchall()

        for l in loans:
            due = datetime.strptime(l["due_date"], "%Y-%m-%d")
            if today > due:
                overdue_days = (today - due).days
                fine = round(overdue_days * 0.50, 2)
                conn.execute(
                    "UPDATE loans SET status = 'Overdue', fine_amount = ? WHERE id = ?",
                    (fine, l["id"]),
                )
            else:
                conn.execute(
                    "UPDATE loans SET status = 'Active', fine_amount = 0.0 WHERE id = ?",
                    (l["id"],),
                )
        conn.commit()


# ----------------------------------------------------------------------
# Web Application Frontend
# ----------------------------------------------------------------------
FULL_WEB_APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CampusShelf — Smart Campus Library System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-hover: #f1f5f9;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --success: #16a34a;
      --success-hover: #15803d;
      --success-bg: #dcfce7;
      --danger: #dc2626;
      --danger-hover: #b91c1c;
      --danger-bg: #fee2e2;
      --warning: #d97706;
      --warning-bg: #fef3c7;
      --radius: 10px;
      --shadow: 0 4px 6px -1px rgba(0,0,0,0.06), 0 2px 4px -2px rgba(0,0,0,0.04);
    }

    [data-theme="dark"] {
      --bg: #0b0f19;
      --surface: #151d2f;
      --surface-hover: #1e293b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --border: #243049;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-light: #1e293b;
      --success: #22c55e;
      --success-hover: #16a34a;
      --success-bg: #064e3b;
      --danger: #ef4444;
      --danger-hover: #dc2626;
      --danger-bg: #7f1d1d;
      --warning: #f59e0b;
      --warning-bg: #78350f;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    /* Lock viewport so ONLY catalog scrolls */
    html, body {
      height: 100vh;
      overflow: hidden;
      background: var(--bg);
      color: var(--text);
      display: flex;
      flex-direction: column;
      transition: background 0.2s, color 0.2s;
    }

    header {
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
      z-index: 50;
    }
    .nav-container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text);
      transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    .logo:hover {
      transform: translateY(-1px);
    }
    .logo-mark {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.14) 0%, rgba(139, 92, 246, 0.2) 100%);
      border: 1.5px solid rgba(59, 130, 246, 0.35);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
      position: relative;
      overflow: hidden;
    }
    .logo-mark::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 48%;
      background: linear-gradient(180deg, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 100%);
      border-radius: 10px 10px 0 0;
      pointer-events: none;
    }
    .logo:hover .logo-mark {
      transform: scale(1.08) rotate(-4deg);
      border-color: var(--primary);
      box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
    }
    .logo-text-group {
      display: flex;
      flex-direction: column;
      line-height: 1.1;
    }
    .logo-title {
      font-size: 21px;
      font-weight: 900;
      letter-spacing: -0.6px;
      display: flex;
      align-items: center;
    }
    .logo-campus {
      color: var(--text);
      font-weight: 800;
      letter-spacing: -0.5px;
    }
    .logo-shelf {
      background: linear-gradient(135deg, #2563eb 0%, #7c3aed 55%, #db2777 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-weight: 900;
      letter-spacing: -0.5px;
      margin-right: 7px;
    }
    [data-theme="dark"] .logo-shelf {
      background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 55%, #f472b6 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .logo-badge {
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: white;
      padding: 2.5px 7px;
      border-radius: 999px;
      font-size: 9px;
      text-transform: uppercase;
      font-weight: 800;
      letter-spacing: 0.6px;
      box-shadow: 0 2px 6px rgba(37, 99, 235, 0.3);
    }
    .logo-tagline {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 1.2px;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .nav-tabs { display: flex; gap: 4px; flex-wrap: wrap; }
    .tab-btn {
      padding: 7px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      background: transparent;
      color: var(--text-muted);
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .tab-btn:hover { background: var(--surface-hover); color: var(--primary); }
    .tab-btn.active { background: var(--primary); color: white; }

    .nav-actions { display: flex; align-items: center; gap: 10px; }
    .admin-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      font-weight: 700;
      background: var(--primary-light);
      color: var(--primary);
      padding: 6px 14px;
      border-radius: 20px;
      border: 1px solid var(--primary);
    }

    .theme-toggle {
      background: var(--surface-hover);
      border: 1px solid var(--border);
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-size: 15px;
    }

    main {
      max-width: 1400px;
      margin: 0 auto;
      padding: 14px 24px;
      width: 100%;
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* KPI Summary Cards (Interactive & Clickable) */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 12px;
      flex-shrink: 0;
    }
    .kpi-card {
      background: var(--surface);
      padding: 12px 16px;
      border-radius: var(--radius);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
    }
    .kpi-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 14px -3px rgba(0,0,0,0.12);
      border-color: var(--primary);
    }
    .kpi-card::before {
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
      background: var(--primary);
    }
    .kpi-card.avail::before { background: var(--success); }
    .kpi-card.issued::before { background: var(--danger); }
    .kpi-card.overdue::before { background: var(--warning); }
    .kpi-label { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; }
    .kpi-value { font-size: 22px; font-weight: 800; margin-top: 2px; }
    .kpi-hint { font-size: 10px; font-weight: 600; opacity: 0.8; margin-top: 2px; }

    @keyframes pulseBorder {
      0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.7); }
      70% { box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
      100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
    }
    .pulse-highlight {
      animation: pulseBorder 1.2s ease-out;
    }

    /* Tab Panes */
    .tab-content { display: none; height: 100%; flex-direction: column; overflow: hidden; }
    .tab-content.active { display: flex; flex: 1; }

    .panel {
      background: var(--surface);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      padding: 16px 20px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
    }
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      flex-wrap: wrap;
      gap: 10px;
      flex-shrink: 0;
    }
    .panel-title { font-size: 17px; font-weight: 800; color: var(--text); display: flex; align-items: center; gap: 8px; }

    /* TWO PARTS SWITCHER (AVAILABLE vs ISSUED) */
    .catalog-parts-bar {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      flex-shrink: 0;
      background: var(--surface-hover);
      padding: 4px;
      border-radius: 8px;
      border: 1px solid var(--border);
    }
    .part-tab-btn {
      flex: 1;
      padding: 9px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 700;
      border: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      background: transparent;
      color: var(--text-muted);
      transition: all 0.2s;
    }
    .part-tab-btn:hover { color: var(--text); }
    .part-tab-btn.active.part-available {
      background: var(--success);
      color: white;
      box-shadow: 0 2px 4px rgba(22, 163, 74, 0.25);
    }
    .part-tab-btn.active.part-issued {
      background: var(--danger);
      color: white;
      box-shadow: 0 2px 4px rgba(220, 38, 38, 0.25);
    }
    .part-count-badge {
      background: rgba(255,255,255,0.25);
      color: inherit;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 800;
    }
    .part-tab-btn:not(.active) .part-count-badge {
      background: var(--border);
      color: var(--text);
    }

    /* Filter Controls */
    .filter-bar {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      margin-bottom: 12px;
      flex-shrink: 0;
    }
    .search-input {
      flex: 1;
      min-width: 200px;
      padding: 8px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 13px;
      outline: none;
      background: var(--surface);
      color: var(--text);
    }
    .search-input:focus { border-color: var(--primary); }
    .select-filter {
      padding: 8px 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 13px;
      background: var(--surface);
      color: var(--text);
      outline: none;
    }

    /* INDEPENDENT CATALOG SCROLL AREA (Only this part scrolls!) */
    .catalog-scroll-area {
      flex: 1;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: var(--surface);
      position: relative;
    }

    /* Sticky table headers */
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    thead th {
      position: sticky;
      top: 0;
      z-index: 10;
      background: var(--surface-hover);
      padding: 11px 14px;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    td { padding: 11px 14px; border-bottom: 1px solid var(--border); vertical-align: middle; color: var(--text); }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: var(--surface-hover); }

    /* Badges */
    .badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; }
    .badge-avail { background: var(--success-bg); color: var(--success); }
    .badge-issued { background: var(--danger-bg); color: var(--danger); }
    .badge-overdue { background: var(--warning-bg); color: var(--warning); }
    .badge-genre { background: var(--surface-hover); color: var(--text-muted); }
    .badge-mid { background: var(--primary-light); color: var(--primary); font-family: monospace; font-size: 11px; }

    /* Buttons */
    button { cursor: pointer; transition: 0.15s; font-size: 12px; font-weight: 600; border-radius: 6px; border: none; padding: 7px 12px; display: inline-flex; align-items: center; gap: 5px; }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-secondary { background: var(--surface-hover); color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { background: var(--border); }
    .btn-success { background: var(--success); color: white; }
    .btn-success:hover { background: var(--success-hover); }
    .btn-danger { background: var(--danger); color: white; }
    .btn-danger:hover { background: var(--danger-hover); }
    .btn-sm { padding: 5px 9px; font-size: 12px; }

    /* Modals */
    .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: none; align-items: center; justify-content: center; z-index: 100; backdrop-filter: blur(3px); }
    .modal-overlay.active { display: flex; }
    .modal-box { background: var(--surface); border-radius: var(--radius); width: 95%; max-width: 540px; padding: 22px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); max-height: 90vh; overflow-y: auto; border: 1px solid var(--border); color: var(--text); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .modal-title { font-size: 17px; font-weight: 800; }
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; font-size: 12px; font-weight: 700; margin-bottom: 5px; color: var(--text); }
    .form-control { width: 100%; padding: 8px 11px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; outline: none; background: var(--surface); color: var(--text); }
    .form-control:focus { border-color: var(--primary); }

    .short-book-banner {
      display: flex;
      align-items: center;
      gap: 12px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 14px;
      margin-bottom: 14px;
    }

    /* Live Member Search List in Give Modal */
    .member-search-results {
      max-height: 180px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 6px;
      margin-top: 6px;
      background: var(--surface);
    }
    .member-search-item {
      padding: 8px 12px;
      border-bottom: 1px solid var(--border);
      cursor: pointer;
      transition: background 0.15s;
    }
    .member-search-item:last-child { border-bottom: none; }
    .member-search-item:hover { background: var(--surface-hover); }
    .member-search-item.selected {
      background: var(--primary-light);
      border-left: 3px solid var(--primary);
    }

    .toast { position: fixed; bottom: 24px; right: 24px; background: #1e293b; color: white; padding: 12px 18px; border-radius: 8px; font-size: 13px; font-weight: 600; display: none; z-index: 200; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
    .toast.success { background: #15803d; display: block; }
    .toast.error { background: #b91c1c; display: block; }

    .pagination { display: flex; justify-content: space-between; align-items: center; padding-top: 10px; font-size: 12px; color: var(--text-muted); flex-shrink: 0; }

    /* ========================================================= */
    /* NEW: SCANNER, LIBRARY CARD, THERMAL RECEIPT, & PATRON KIOSK */
    /* ========================================================= */
    
    /* Scanner Modal Viewfinder */
    .scanner-viewfinder {
      position: relative;
      width: 100%;
      height: 240px;
      background: #0f172a;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
      border: 2px dashed rgba(59, 130, 246, 0.4);
    }
    .scanner-video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .scanner-reticle {
      position: absolute;
      top: 20px;
      left: 20px;
      right: 20px;
      bottom: 20px;
      border: 2px solid rgba(59, 130, 246, 0.8);
      border-radius: 8px;
      box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.4);
      pointer-events: none;
    }
    .scanner-laser {
      position: absolute;
      left: 10%;
      right: 10%;
      height: 2px;
      background: #ef4444;
      box-shadow: 0 0 10px #ef4444;
      animation: laserSweep 2s ease-in-out infinite alternate;
    }
    @keyframes laserSweep {
      0% { top: 25px; opacity: 0.8; }
      100% { top: 215px; opacity: 0.8; }
    }

    /* Printable Library Card (CR80 Standard Card Proportion) */
    .library-card-wrap {
      display: flex;
      justify-content: center;
      padding: 10px 0;
    }
    .library-card {
      width: 380px;
      height: 230px;
      border-radius: 14px;
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      color: #ffffff;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 15px 35px rgba(0,0,0,0.35);
      border: 1px solid rgba(255,255,255,0.15);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .library-card::before {
      content: '';
      position: absolute;
      top: -40px;
      right: -40px;
      width: 160px;
      height: 160px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(139, 92, 246, 0.25));
      filter: blur(20px);
      pointer-events: none;
    }
    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      position: relative;
      z-index: 2;
    }
    .card-brand {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .card-brand-title {
      font-size: 15px;
      font-weight: 800;
      letter-spacing: -0.3px;
    }
    .card-brand-sub {
      font-size: 9px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #94a3b8;
    }
    .card-type-badge {
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      color: #fff;
      font-size: 9px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .card-middle {
      display: flex;
      align-items: center;
      gap: 14px;
      position: relative;
      z-index: 2;
    }
    .card-avatar {
      width: 48px;
      height: 48px;
      border-radius: 10px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      border: 2px solid rgba(255,255,255,0.3);
      box-shadow: 0 4px 10px rgba(0,0,0,0.3);
      flex-shrink: 0;
    }
    .card-info { flex: 1; }
    .card-name { font-size: 16px; font-weight: 800; margin-bottom: 2px; }
    .card-id-code {
      font-size: 13px;
      font-family: monospace;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: 0.5px;
    }
    .card-contact { font-size: 10px; color: #94a3b8; margin-top: 2px; }
    .card-bottom {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      position: relative;
      z-index: 2;
    }
    .card-barcode-box {
      background: #ffffff;
      padding: 4px 8px;
      border-radius: 6px;
      color: #000;
      display: inline-block;
    }
    .card-seal {
      font-size: 9px;
      color: #94a3b8;
      text-align: right;
      line-height: 1.2;
    }

    /* Printable Thermal Loan Receipt (80mm styling) */
    .receipt-wrap {
      display: flex;
      justify-content: center;
      padding: 10px 0;
    }
    .receipt-paper {
      width: 320px;
      background: #ffffff;
      color: #0f172a;
      border: 1px dashed #cbd5e1;
      padding: 20px 18px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.1);
      font-family: 'Courier New', Courier, monospace;
      font-size: 12px;
      line-height: 1.4;
      border-radius: 4px;
    }
    .receipt-header {
      text-align: center;
      border-bottom: 1px dashed #64748b;
      padding-bottom: 10px;
      margin-bottom: 10px;
    }
    .receipt-title { font-size: 16px; font-weight: 900; letter-spacing: 0.5px; }
    .receipt-divider { border-top: 1px dashed #94a3b8; margin: 10px 0; }
    .receipt-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .receipt-due {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 6px;
      padding: 8px 10px;
      margin: 10px 0;
      text-align: center;
      font-weight: 700;
    }
    .receipt-footer {
      text-align: center;
      font-size: 10px;
      color: #64748b;
      margin-top: 12px;
      border-top: 1px dashed #64748b;
      padding-top: 8px;
    }

    /* Print Media Rules */
    @media print {
      body * { visibility: hidden !important; }
      #printable-content, #printable-content * { visibility: visible !important; }
      #printable-content {
        position: fixed !important;
        left: 50% !important;
        top: 20px !important;
        transform: translateX(-50%) !important;
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      .no-print { display: none !important; }
    }

    /* Patron Self-Service Kiosk Styles */
    .patron-kiosk-box {
      max-width: 900px;
      margin: 0 auto;
    }
    .patron-search-hero {
      background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(124,58,237,0.08));
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 22px;
      margin-bottom: 18px;
      text-align: center;
    }
    .patron-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      background: var(--surface-hover);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 18px;
      margin-bottom: 16px;
    }
    .patron-pill-stat {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 14px;
      text-align: center;
    }
    .patron-pill-val { font-size: 18px; font-weight: 800; }
    .patron-pill-lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text-muted); }
  </style>
</head>
<body>
  <!-- Header (Admin Only) -->
  <header>
    <div class="nav-container">
      <a href="#" class="logo">
        <div class="logo-mark">
          <span>📚</span>
        </div>
        <div class="logo-text-group">
          <div class="logo-title">
            <span class="logo-campus">Campus</span><span class="logo-shelf">Shelf</span>
            <span class="logo-badge">PRO</span>
          </div>
          <div class="logo-tagline">Smart Campus Library</div>
        </div>
      </a>

      <div class="nav-tabs">
        <button class="tab-btn active" onclick="switchTab('catalog')">📚 Catalog</button>
        <button class="tab-btn" onclick="switchTab('holds')">⏳ Holds (Waitlist)</button>
        <button class="tab-btn" onclick="switchTab('members')">👥 Members</button>
        <button class="tab-btn" onclick="switchTab('patron')">👤 Patron Kiosk</button>
        <button class="tab-btn" onclick="switchTab('analytics')">📊 Analytics</button>
      </div>

      <div class="nav-actions">
        <button class="btn-primary" onclick="openScannerModal()" style="padding:6px 12px; font-weight:700; gap:6px;">
          <span>📷</span> <span>Scan Barcode</span>
        </button>
        <div class="admin-pill">
          <span>👑 Librarian Admin</span>
        </div>
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle Dark/Light Mode" id="theme-btn">🌙</button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main>
    <!-- Top KPI Bar (Clickable cards that jump / open details) -->
    <div class="kpi-grid">
      <div class="kpi-card" id="kpi-card-total" onclick="handleKpiClick('total')">
        <div class="kpi-label"><span>Total Inventory</span> <span>🔍</span></div>
        <div class="kpi-value" id="kpi-total">500</div>
        <div class="kpi-hint" style="color:var(--text-muted);">Click to show all</div>
      </div>
      <div class="kpi-card avail" id="kpi-card-avail" onclick="handleKpiClick('available')">
        <div class="kpi-label"><span>Available Copies</span> <span>🟢</span></div>
        <div class="kpi-value" style="color:var(--success)" id="kpi-available">0</div>
        <div class="kpi-hint" style="color:var(--success);">Click to jump to Part 1</div>
      </div>
      <div class="kpi-card issued" id="kpi-card-issued" onclick="handleKpiClick('issued')">
        <div class="kpi-label"><span>Issued Copies</span> <span>🔴</span></div>
        <div class="kpi-value" style="color:var(--danger)" id="kpi-issued">0</div>
        <div class="kpi-hint" style="color:var(--danger);">Click to jump to Part 2</div>
      </div>
      <div class="kpi-card overdue" id="kpi-card-overdue" onclick="handleKpiClick('overdue')">
        <div class="kpi-label"><span>Overdue Loans</span> <span>⚠️</span></div>
        <div class="kpi-value" style="color:var(--warning)" id="kpi-overdue">0</div>
        <div class="kpi-hint" style="color:var(--warning);">Click to view list & receive</div>
      </div>
      <div class="kpi-card" id="kpi-card-fines" onclick="handleKpiClick('fines')">
        <div class="kpi-label"><span>Pending Fines ($0.50/day)</span> <span>💰</span></div>
        <div class="kpi-value" style="color:#ef4444" id="kpi-fines">$0.00</div>
        <div class="kpi-hint" style="color:#ef4444;">Click to view breakdown</div>
      </div>
      <div class="kpi-card" id="kpi-card-holds" onclick="handleKpiClick('holds')">
        <div class="kpi-label"><span>Active Holds</span> <span>⏳</span></div>
        <div class="kpi-value" style="color:var(--primary)" id="kpi-holds">0</div>
        <div class="kpi-hint" style="color:var(--primary);">Click to view waitlist</div>
      </div>
    </div>

    <!-- TAB 1: CATALOG (2 PARTS: AVAILABLE vs ISSUED) -->
    <div id="tab-catalog" class="tab-content active">
      <div class="panel" id="catalog-panel">
        <div class="panel-header">
          <div class="panel-title">📚 Library Inventory</div>
          <div style="display:flex; gap:6px; flex-wrap:wrap;">
            <button class="btn-primary" onclick="openAddBookModal()">➕ Add Book</button>
            <button class="btn-secondary" onclick="exportBooksCSV()">📥 Export CSV</button>
          </div>
        </div>

        <!-- 2 PROMINENT PARTS: AVAILABLE vs ISSUED -->
        <div class="catalog-parts-bar" id="catalog-parts-bar">
          <button class="part-tab-btn part-available active" id="part-btn-available" onclick="switchCatalogPart('Available')">
            🟢 Part 1: Available Books <span class="part-count-badge" id="part-count-avail">...</span>
          </button>
          <button class="part-tab-btn part-issued" id="part-btn-issued" onclick="switchCatalogPart('Issued')">
            🔴 Part 2: Issued Books <span class="part-count-badge" id="part-count-issued">...</span>
          </button>
        </div>

        <!-- Filter Controls (Locked in place) -->
        <div class="filter-bar">
          <input type="text" id="catalog-search" class="search-input" placeholder="Search title, author, or ISBN..." onkeyup="if(event.key==='Enter') applyFilters()">
          <select id="filter-genre" class="select-filter" onchange="applyFilters()">
            <option value="All">All Genres</option>
            <option value="Classics">Classics</option>
            <option value="Sci-Fi & Fantasy">Sci-Fi & Fantasy</option>
            <option value="Mystery & Thriller">Mystery & Thriller</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Non-Fiction">Non-Fiction</option>
            <option value="Philosophy">Philosophy</option>
          </select>
          <select id="filter-sort" class="select-filter" onchange="applyFilters()">
            <option value="id_asc">Sort: ID (Default)</option>
            <option value="title_asc">Sort: Title (A-Z)</option>
            <option value="title_desc">Sort: Title (Z-A)</option>
            <option value="author_asc">Sort: Author (A-Z)</option>
            <option value="shelf_asc">Sort: Shelf Location</option>
          </select>
          <button class="btn-primary btn-sm" onclick="applyFilters()">Filter</button>
          <button class="btn-secondary btn-sm" onclick="resetFilters()">Reset</button>
        </div>

        <!-- ONLY THIS AREA SCROLLS! (Independent Scroll Container) -->
        <div class="catalog-scroll-area">
          <table>
            <thead id="catalog-table-head"></thead>
            <tbody id="books-table-body">
              <tr><td colspan="7" style="text-align:center; padding:30px;">Loading catalog...</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Bar (Locked at bottom) -->
        <div class="pagination">
          <span id="page-info">Showing 1 to 25 books</span>
          <div style="display:flex; gap:6px;">
            <button class="btn-secondary btn-sm" id="btn-prev-page" onclick="prevPage()">◀ Previous</button>
            <button class="btn-secondary btn-sm" id="btn-next-page" onclick="nextPage()">Next ▶</button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: HOLDS (WAITLIST) -->
    <div id="tab-holds" class="tab-content">
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title">⏳ Book Holds & Waitlist</div>
          <p style="font-size:12px; color:var(--text-muted);">When an issued book is returned, the next patron in the waitlist is automatically assigned.</p>
        </div>

        <div class="catalog-scroll-area">
          <table>
            <thead>
              <tr>
                <th>Hold ID</th>
                <th>Book Title</th>
                <th>Patron Name & Member ID</th>
                <th>Reservation Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="holds-table-body">
              <tr><td colspan="6" style="text-align:center; padding:30px;">Loading reservations...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: MEMBERS -->
    <div id="tab-members" class="tab-content">
      <div class="panel">
        <div class="panel-header">
          <div class="panel-title">👥 Registered Library Members</div>
          <button class="btn-primary" onclick="openAddMemberModal()">➕ Register Member</button>
        </div>

        <div class="catalog-scroll-area">
          <table>
            <thead>
              <tr>
                <th>Member ID</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role / Type</th>
                <th>Active Loans</th>
                <th>Max Limit</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="members-table-body">
              <tr><td colspan="8" style="text-align:center; padding:30px;">Loading members...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: ANALYTICS -->
    <div id="tab-analytics" class="tab-content">
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px; flex-shrink:0;">
        <div class="panel" style="margin-bottom:0;">
          <h3 style="font-size:14px; font-weight:700; margin-bottom:12px;">📊 Inventory Availability Breakdown</h3>
          <div id="donut-chart-box" style="display:flex; align-items:center; justify-content:center; height:200px;"></div>
        </div>
        <div class="panel" style="margin-bottom:0;">
          <h3 style="font-size:14px; font-weight:700; margin-bottom:12px;">📚 Popular Genres Distribution</h3>
          <div id="bar-chart-box" style="height:200px; display:flex; align-items:flex-end; gap:12px; padding:10px 0;"></div>
        </div>
      </div>

      <div class="panel" style="flex:1;">
        <div class="panel-title" style="margin-bottom:8px;">💡 Library Health Summary</div>
        <p style="color:var(--text-muted); font-size:13px; line-height:1.6;">
          Your collection hosts <strong>500 curated volumes</strong>.
          The automated fine engine operates at <strong>$0.50/day</strong> for overdue books.
          When books are returned with pending holds, the waitlist reservation system automatically prioritizes the queue.
        </p>
      </div>
    </div>

    <!-- TAB 5: PATRON / STUDENT SELF-SERVICE KIOSK -->
    <div id="tab-patron" class="tab-content">
      <div class="patron-kiosk-box">
        <div class="patron-search-hero">
          <h2 style="font-size:20px; font-weight:800; margin-bottom:6px;">👤 Patron Self-Service Kiosk</h2>
          <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">
            Search your Member ID (#M-X), Name, or Email to view your active borrowed books, due dates, fines, and place holds on waitlisted books.
          </p>
          <div style="max-width:480px; margin:0 auto; display:flex; gap:8px;">
            <input type="text" id="patron-search-input" class="form-control" placeholder="Enter Member ID (#M-1) or email..." onkeydown="if(event.key==='Enter') lookupPatron()">
            <button class="btn-primary" onclick="lookupPatron()">🔍 Lookup</button>
          </div>
          <div style="display:flex; justify-content:center; gap:6px; margin-top:10px; flex-wrap:wrap;">
            <span style="font-size:11px; color:var(--text-muted);">Quick test:</span>
            <button class="btn-sm btn-secondary" onclick="quickLookupPatron(1)" style="font-size:11px;">#M-1 (Elena)</button>
            <button class="btn-sm btn-secondary" onclick="quickLookupPatron(2)" style="font-size:11px;">#M-2 (Marcus)</button>
            <button class="btn-sm btn-secondary" onclick="quickLookupPatron(3)" style="font-size:11px;">#M-3 (Aisha)</button>
          </div>
        </div>

        <div id="patron-dashboard-content" style="display:none;">
          <!-- Patron Profile Header -->
          <div class="patron-card-header">
            <div style="display:flex; align-items:center; gap:12px;">
              <div style="width:44px; height:44px; border-radius:10px; background:var(--primary); color:white; display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:800;" id="patron-avatar-initials">P</div>
              <div>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="badge badge-mid" id="patron-mid-badge">#M-1</span>
                  <strong style="font-size:16px;" id="patron-name-display">Patron Name</strong>
                  <span class="badge badge-genre" id="patron-type-badge">Student</span>
                </div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:2px;" id="patron-contact-display"></div>
              </div>
            </div>
            <div style="display:flex; gap:10px;">
              <div class="patron-pill-stat">
                <div class="patron-pill-val" style="color:var(--primary);" id="patron-loans-count">0</div>
                <div class="patron-pill-lbl">Active Loans</div>
              </div>
              <div class="patron-pill-stat">
                <div class="patron-pill-val" style="color:var(--warning);" id="patron-holds-count">0</div>
                <div class="patron-pill-lbl">Waitlist Holds</div>
              </div>
              <div class="patron-pill-stat">
                <div class="patron-pill-val" style="color:var(--danger);" id="patron-fines-total">$0.00</div>
                <div class="patron-pill-lbl">Pending Fines</div>
              </div>
              <button class="btn-secondary" onclick="printCurrentPatronCard()" style="font-weight:700;">🪪 Print Card</button>
            </div>
          </div>

          <!-- Section 1: My Current Loans -->
          <div class="panel" style="margin-bottom:16px;">
            <div class="panel-header">
              <div class="panel-title">📖 My Currently Borrowed Books</div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Book Title</th>
                  <th>Shelf Return Location</th>
                  <th>Issued Date</th>
                  <th>Due Date</th>
                  <th>Status & Fines</th>
                </tr>
              </thead>
              <tbody id="patron-loans-table-body">
                <tr><td colspan="5" style="text-align:center; padding:20px; color:var(--text-muted);">No active loans.</td></tr>
              </tbody>
            </table>
          </div>

          <!-- Section 2: My Active Holds (Waitlist) -->
          <div class="panel" style="margin-bottom:16px;">
            <div class="panel-header">
              <div class="panel-title">⏳ My Active Book Holds (Waitlist)</div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Book Title</th>
                  <th>Reserved Date</th>
                  <th>Hold Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody id="patron-holds-table-body">
                <tr><td colspan="4" style="text-align:center; padding:20px; color:var(--text-muted);">No active holds.</td></tr>
              </tbody>
            </table>
          </div>

          <!-- Section 3: Place a Hold on any Issued Book -->
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">📌 Place a Hold on a Currently Borrowed Book</div>
            </div>
            <p style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">
              Can't find a book on the shelf because someone else checked it out? Reserve your spot in line — as soon as it's returned, it will be held for you!
            </p>
            <div style="display:flex; gap:8px; margin-bottom:12px;">
              <input type="text" id="patron-hold-search" class="form-control" placeholder="Search issued books to place a hold (e.g. 1984, Dune, Gatsby)..." oninput="filterPatronHoldBooks(this.value)">
            </div>
            <div id="patron-hold-books-list" style="max-height:220px; overflow-y:auto; border:1px solid var(--border); border-radius:6px;"></div>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- MODAL: SHORT "GIVE BOOK" BOX (With Live Typing Member Search by Name, Phone, Email, or Member ID) -->
  <div id="modal-give-book" class="modal-overlay">
    <div class="modal-box">
      <div class="modal-header">
        <div class="modal-title">📤 Give Book to Borrower</div>
        <button onclick="closeModal('modal-give-book')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <!-- Book Info Preview -->
      <div class="short-book-banner">
        <span class="badge badge-avail" id="give-book-id-badge">#1</span>
        <div>
          <strong id="give-book-title" style="font-size:14px; display:block;"></strong>
          <span id="give-book-author" style="font-size:12px; color:var(--text-muted);"></span>
        </div>
      </div>

      <input type="hidden" id="give-book-id">
      <input type="hidden" id="give-selected-member-id" value="">

      <!-- Borrower Selection with Live Search -->
      <div class="form-group">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <label style="margin-bottom:0;">Whom to give this book to? *</label>
          <button type="button" class="btn-sm btn-secondary" onclick="toggleNewBorrowerForm()" id="btn-toggle-new-borrower">+ Type New Borrower</button>
        </div>

        <!-- Selected Member Pill (shown once selected) -->
        <div id="give-selected-member-box" style="display:none; background:var(--primary-light); border:1px solid var(--primary); border-radius:6px; padding:10px; margin-bottom:10px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span class="badge badge-mid" id="give-selected-mid">#M-1</span>
              <strong id="give-selected-mname" style="margin-left:6px;"></strong>
              <div style="font-size:11px; color:var(--text-muted); margin-top:2px;" id="give-selected-mcontact"></div>
            </div>
            <button type="button" class="btn-sm btn-secondary" onclick="clearSelectedMember()">Change</button>
          </div>
        </div>

        <!-- Live Member Search Box -->
        <div id="give-search-wrap">
          <input type="text" id="give-member-search-input" class="form-control" 
                 placeholder="🔍 Search by Name, Phone, Email, or Member ID (#M-1)..." 
                 oninput="filterMemberSearch(this.value)">
          <div class="member-search-results" id="give-member-search-results"></div>
        </div>

        <!-- Type New Borrower Form (Fallback) -->
        <div id="give-new-borrower-wrap" style="display:none; background:var(--surface-hover); padding:10px; border-radius:6px; margin-top:8px;">
          <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase; margin-bottom:6px;">New Borrower Details</div>
          <input type="text" id="give-new-name" class="form-control" placeholder="Borrower Full Name *" style="margin-bottom:6px;">
          <input type="text" id="give-new-contact" class="form-control" placeholder="Phone or Email (Optional)" style="margin-bottom:6px;">
          <select id="give-new-type" class="form-control">
            <option value="Student">Student (Max 3 Books)</option>
            <option value="Faculty">Faculty (Max 10 Books)</option>
            <option value="General Public">General Public (Max 2 Books)</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Loan Duration</label>
        <select id="give-loan-days" class="form-control">
          <option value="14">14 Days (Standard Loan)</option>
          <option value="7">7 Days (Short Loan)</option>
          <option value="21">21 Days (Extended Loan)</option>
          <option value="30">30 Days (Faculty Special)</option>
        </select>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:16px;">
        <button class="btn-secondary" onclick="closeModal('modal-give-book')">Cancel</button>
        <button class="btn-success" onclick="confirmGiveBook()">✓ Confirm & Give Book</button>
      </div>
    </div>
  </div>

  <!-- MODAL: "RECEIVE BOOK" CONFIRMATION BOX (Confirms details of book & who returns it) -->
  <div id="modal-receive-book" class="modal-overlay">
    <div class="modal-box">
      <div class="modal-header">
        <div class="modal-title">📥 Confirm & Receive Book Back</div>
        <button onclick="closeModal('modal-receive-book')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <input type="hidden" id="receive-book-id">

      <!-- Book Details -->
      <div style="background:var(--surface-hover); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:12px;">
        <div style="font-size:11px; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Book Details</div>
        <div style="font-size:15px; font-weight:800; margin-top:3px;" id="receive-book-title"></div>
        <div style="font-size:12px; color:var(--text-muted);" id="receive-book-author"></div>
        <div style="font-size:12px; margin-top:6px; color:var(--primary);">📍 Returning to: <strong id="receive-book-shelf"></strong></div>
      </div>

      <!-- Who is Returning It (With Member ID) -->
      <div style="background:var(--primary-light); border:1px solid var(--primary); border-radius:8px; padding:12px; margin-bottom:12px;">
        <div style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">Who is returning it? (Borrower Details)</div>
        <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
          <span class="badge badge-mid" id="receive-borrower-mid">#M-1</span>
          <strong style="font-size:15px;" id="receive-borrower-name"></strong>
        </div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:2px;" id="receive-borrower-contact"></div>
        <div style="margin-top:8px; font-size:12px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:4px;">
          <span>Issued On: <strong id="receive-issue-date"></strong></span>
          <span>Due Date: <strong id="receive-due-date"></strong></span>
        </div>
        <div id="receive-overdue-alert" style="margin-top:8px; font-size:12px;"></div>
      </div>

      <div style="margin-bottom:14px;">
        <label style="display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; cursor:pointer;">
          <input type="checkbox" id="receive-condition-check" checked style="width:16px; height:16px;">
          <span>Book copy inspected and received in good condition</span>
        </label>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px;">
        <button class="btn-secondary" onclick="closeModal('modal-receive-book')">Cancel</button>
        <button class="btn-success" onclick="confirmReceiveBook()">✓ Confirm & Receive Book</button>
      </div>
    </div>
  </div>

  <!-- MODAL: OVERDUE LOANS DETAILS (Triggered by KPI Click) -->
  <div id="modal-overdue-details" class="modal-overlay">
    <div class="modal-box" style="max-width: 680px;">
      <div class="modal-header">
        <div class="modal-title">⚠️ Overdue Loans Details</div>
        <button onclick="closeModal('modal-overdue-details')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:12px;">
        These books are past their return due date. Fines accrue at <strong>$0.50/day</strong>.
      </p>
      <div class="table-responsive" style="max-height:360px;">
        <table>
          <thead>
            <tr>
              <th>Book Title & ID</th>
              <th>Borrower & Member ID</th>
              <th>Due Date</th>
              <th>Overdue Days</th>
              <th>Fine</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="overdue-table-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- MODAL: PENDING FINES BREAKDOWN (Triggered by KPI Click) -->
  <div id="modal-fines-details" class="modal-overlay">
    <div class="modal-box" style="max-width: 650px;">
      <div class="modal-header">
        <div class="modal-title">💰 Outstanding Fines Breakdown</div>
        <button onclick="closeModal('modal-fines-details')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>
      <div style="background:var(--warning-bg); border:1px solid var(--warning); border-radius:8px; padding:12px; margin-bottom:14px;">
        <div style="font-size:11px; font-weight:700; color:var(--warning); text-transform:uppercase;">Fine Settlement Policy</div>
        <div style="font-size:13px; font-weight:600; margin-top:2px;">Fines are collected or settled upon receiving the book back into the library.</div>
      </div>
      <div class="table-responsive" style="max-height:360px;">
        <table>
          <thead>
            <tr>
              <th>Borrower & Member ID</th>
              <th>Book Title</th>
              <th>Days Overdue</th>
              <th>Pending Fine</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="fines-table-body"></tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- MODAL: ADD BOOK -->
  <div id="modal-book" class="modal-overlay">
    <div class="modal-box">
      <div class="modal-header">
        <div class="modal-title">➕ Add New Book Copy</div>
        <button onclick="closeModal('modal-book')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>
      <div style="background:var(--primary-light); border:1px solid var(--primary); padding:10px; border-radius:6px; margin-bottom:12px;">
        <label style="font-size:11px; font-weight:700; color:var(--primary); text-transform:uppercase;">⚡ Quick Auto-Fill via ISBN</label>
        <div style="display:flex; gap:6px; margin-top:4px;">
          <input type="text" id="isbn-autofill-input" class="form-control" placeholder="Enter ISBN (e.g. 9780061120084)">
          <button class="btn-primary btn-sm" type="button" onclick="lookupISBN()">Lookup</button>
        </div>
        <div id="isbn-status" style="font-size:11px; margin-top:4px; font-weight:600;"></div>
      </div>

      <div class="form-group">
        <label>Book Title *</label>
        <input type="text" id="book-title-input" class="form-control" placeholder="e.g. Dune" required>
      </div>
      <div class="form-group">
        <label>Author *</label>
        <input type="text" id="book-author-input" class="form-control" placeholder="e.g. Frank Herbert" required>
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Genre</label>
          <select id="book-genre-input" class="form-control">
            <option value="Classics">Classics</option>
            <option value="Sci-Fi & Fantasy">Sci-Fi & Fantasy</option>
            <option value="Mystery & Thriller">Mystery & Thriller</option>
            <option value="Computer Science">Computer Science</option>
            <option value="Non-Fiction">Non-Fiction</option>
            <option value="Philosophy">Philosophy</option>
            <option value="General">General</option>
          </select>
        </div>
        <div class="form-group">
          <label>Shelf Location</label>
          <input type="text" id="book-shelf-input" class="form-control" placeholder="Shelf A-01">
        </div>
      </div>
      <div class="form-group">
        <label>ISBN</label>
        <input type="text" id="book-isbn-input" class="form-control" placeholder="e.g. 9780441172719">
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:16px;">
        <button class="btn-secondary" onclick="closeModal('modal-book')">Cancel</button>
        <button class="btn-primary" onclick="saveBook()">Save Book</button>
      </div>
    </div>
  </div>

  <!-- MODAL: REGISTER MEMBER -->
  <div id="modal-member" class="modal-overlay">
    <div class="modal-box">
      <div class="modal-header">
        <div class="modal-title">👥 Register New Member</div>
        <button onclick="closeModal('modal-member')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>
      <div class="form-group">
        <label>Full Name *</label>
        <input type="text" id="member-name-input" class="form-control" placeholder="e.g. Sarah Jenkins" required>
      </div>
      <div class="form-group">
        <label>Email Address *</label>
        <input type="email" id="member-email-input" class="form-control" placeholder="e.g. sjenkins@univ.edu" required>
      </div>
      <div class="form-group">
        <label>Phone Number</label>
        <input type="text" id="member-phone-input" class="form-control" placeholder="+1-555-0199">
      </div>
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div class="form-group">
          <label>Member Type</label>
          <select id="member-type-select" class="form-control">
            <option value="Student">Student (Max 3 Books)</option>
            <option value="Faculty">Faculty (Max 10 Books)</option>
            <option value="General Public">General Public (Max 2 Books)</option>
          </select>
        </div>
        <div class="form-group">
          <label>Borrow Limit</label>
          <input type="number" id="member-limit-input" class="form-control" value="3" min="1" max="20">
        </div>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:16px;">
        <button class="btn-secondary" onclick="closeModal('modal-member')">Cancel</button>
        <button class="btn-primary" onclick="saveMember()">Register</button>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div id="toast" class="toast"></div>


  <!-- MODAL: BARCODE & QR CAMERA SCANNER -->
  <div id="modal-scanner" class="modal-overlay">
    <div class="modal-box" style="max-width: 480px;">
      <div class="modal-header">
        <div class="modal-title">📷 Barcode & Card Scanner</div>
        <button onclick="closeScannerModal()" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <!-- Viewfinder with sweep laser -->
      <div class="scanner-viewfinder">
        <video id="scanner-video" class="scanner-video" autoplay playsinline muted></video>
        <div class="scanner-reticle"></div>
        <div class="scanner-laser"></div>
        <div id="scanner-camera-fallback" style="display:none; position:absolute; color:#94a3b8; font-size:12px; text-align:center; padding:20px;">
          📹 Camera preview active.<br>Point barcode or student card at camera or type code below.
        </div>
      </div>

      <div class="form-group">
        <label>Scan or Type Barcode / Copy ID / Member ID / ISBN:</label>
        <div style="display:flex; gap:8px;">
          <input type="text" id="scanner-manual-input" class="form-control" placeholder="e.g. 4, CS-BOOK-0004, #M-1, or 9780061120084..." onkeydown="if(event.key==='Enter') executeScanLookup()">
          <button class="btn-primary" onclick="executeScanLookup()">Scan</button>
        </div>
        <div style="font-size:11px; color:var(--text-muted); margin-top:6px;">
          💡 USB Handheld barcode scanners work automatically — just point and click the scanner trigger!
        </div>
      </div>

      <div id="scanner-result-box" style="display:none; padding:10px; background:var(--primary-light); border:1px solid var(--primary); border-radius:6px; margin-top:10px;">
        <strong id="scanner-result-title" style="display:block; font-size:13px;"></strong>
        <span id="scanner-result-desc" style="font-size:11px; color:var(--text-muted);"></span>
      </div>
    </div>
  </div>

  <!-- MODAL: PRINTABLE PATRON LIBRARY CARD -->
  <div id="modal-library-card" class="modal-overlay">
    <div class="modal-box" style="max-width: 460px; text-align:center;">
      <div class="modal-header">
        <div class="modal-title">🪪 Official Campus Library Card</div>
        <button onclick="closeModal('modal-library-card')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <div id="printable-card-area" class="library-card-wrap">
        <div class="library-card" id="library-card-element">
          <div class="card-top">
            <div class="card-brand">
              <span style="font-size:20px;">🏛️</span>
              <div>
                <div class="card-brand-title">CampusShelf</div>
                <div class="card-brand-sub">University Central Library</div>
              </div>
            </div>
            <span class="card-type-badge" id="card-render-type">STUDENT</span>
          </div>

          <div class="card-middle">
            <div class="card-avatar" id="card-render-avatar">👤</div>
            <div class="card-info" style="text-align:left;">
              <div class="card-name" id="card-render-name">Elena Rostova</div>
              <div class="card-id-code" id="card-render-mid">#M-1</div>
              <div class="card-contact" id="card-render-contact">elena@campus.edu • 555-0142</div>
            </div>
          </div>

          <div class="card-bottom">
            <div class="card-barcode-box" id="card-render-barcode-box">
              <!-- SVG Barcode injected here -->
            </div>
            <div class="card-seal">
              AUTHORIZED<br>PATRON PASS
            </div>
          </div>
        </div>
      </div>

      <div style="display:flex; justify-content:center; gap:10px; margin-top:16px;">
        <button class="btn-primary" onclick="printCard()" style="padding:8px 18px; font-weight:700;">🖨️ Print Library Card</button>
        <button class="btn-secondary" onclick="closeModal('modal-library-card')">Close</button>
      </div>
    </div>
  </div>

  <!-- MODAL: PRINTABLE THERMAL BORROWING RECEIPT -->
  <div id="modal-receipt" class="modal-overlay">
    <div class="modal-box" style="max-width: 420px; text-align:center;">
      <div class="modal-header">
        <div class="modal-title">🧾 Checkout Receipt</div>
        <button onclick="closeModal('modal-receipt')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <div id="printable-receipt-area" class="receipt-wrap">
        <div class="receipt-paper" id="receipt-paper-element">
          <div class="receipt-header">
            <div class="receipt-title">🏛️ CAMPUS SHELF</div>
            <div style="font-size:10px; color:#64748b; margin-top:2px;">Central Campus Library System</div>
            <div style="font-size:10px; margin-top:4px;" id="receipt-date-time">Nov 7, 2026 • 12:00 PM</div>
          </div>

          <div class="receipt-row">
            <span>PATRON:</span>
            <strong id="receipt-borrower-name">Elena Rostova</strong>
          </div>
          <div class="receipt-row">
            <span>MEMBER ID:</span>
            <strong id="receipt-borrower-mid">#M-1</strong>
          </div>

          <div class="receipt-divider"></div>

          <div style="text-align:left; margin-bottom:4px;">
            <strong id="receipt-book-title" style="font-size:13px; display:block;">Book Title</strong>
            <span style="font-size:11px; color:#64748b;" id="receipt-book-author">by Author</span>
          </div>
          <div class="receipt-row">
            <span>COPY ID:</span>
            <strong id="receipt-book-copy">#4</strong>
          </div>
          <div class="receipt-row">
            <span>RETURN SHELF:</span>
            <strong id="receipt-book-shelf">Shelf A-04</strong>
          </div>

          <div class="receipt-due">
            <div style="font-size:10px; text-transform:uppercase; color:#2563eb;">RETURN DUE DATE:</div>
            <div style="font-size:15px; font-weight:900;" id="receipt-due-date">Nov 21, 2026</div>
          </div>

          <div style="margin:10px 0;" id="receipt-barcode-box">
            <!-- SVG Barcode injected here -->
          </div>

          <div class="receipt-footer">
            Overdue fines accrue at $0.50 per day.<br>
            Please return copy to designated shelf on time.<br>
            Thank you for reading with CampusShelf!
          </div>
        </div>
      </div>

      <div style="display:flex; justify-content:center; gap:10px; margin-top:16px;">
        <button class="btn-primary" onclick="printReceipt()" style="padding:8px 18px; font-weight:700;">🖨️ Print Receipt</button>
        <button class="btn-secondary" onclick="closeModal('modal-receipt')">Close</button>
      </div>
    </div>
  </div>

  <!-- MODAL: BOOK BARCODE & SHELF LABEL -->
  <div id="modal-book-barcode" class="modal-overlay">
    <div class="modal-box" style="max-width: 420px; text-align:center;">
      <div class="modal-header">
        <div class="modal-title">🏷️ Book Shelf & Barcode Label</div>
        <button onclick="closeModal('modal-book-barcode')" style="background:none; border:none; font-size:18px; color:var(--text);">✕</button>
      </div>

      <div style="background:white; color:#0f172a; padding:18px; border-radius:8px; border:1px solid #cbd5e1; margin-bottom:14px;" id="book-barcode-print-area">
        <div style="font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:1px; color:#64748b; margin-bottom:2px;">CAMPUS SHELF LIBRARY</div>
        <h3 id="book-label-title" style="font-size:15px; font-weight:800; margin-bottom:2px;">Book Title</h3>
        <div id="book-label-author" style="font-size:11px; color:#64748b; margin-bottom:8px;">Author</div>
        <div style="display:inline-block; padding:4px 10px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; font-weight:700; font-size:12px; margin-bottom:10px;" id="book-label-shelf">
          📍 Shelf A-01
        </div>
        <div id="book-label-barcode-svg"></div>
      </div>

      <div style="display:flex; justify-content:center; gap:10px;">
        <button class="btn-primary" onclick="printBookLabel()">🖨️ Print Label</button>
        <button class="btn-secondary" onclick="closeModal('modal-book-barcode')">Close</button>
      </div>
    </div>
  </div>

  <script>
    // State
    let currentTab = 'catalog';
    let currentPart = 'Available';
    let currentPage = 1;
    const pageSize = 25;
    let totalBooks = 500;
    let allMembers = [];
    let isTypingNewBorrower = false;

    // Theme Setup
    function initTheme() {
      const saved = localStorage.getItem('theme') || 'light';
      document.documentElement.setAttribute('data-theme', saved);
      document.getElementById('theme-btn').textContent = saved === 'dark' ? '☀️' : '🌙';
    }
    function toggleTheme() {
      const cur = document.documentElement.getAttribute('data-theme') || 'light';
      const nxt = cur === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nxt);
      localStorage.setItem('theme', nxt);
      document.getElementById('theme-btn').textContent = nxt === 'dark' ? '☀️' : '🌙';
    }
    initTheme();

    function showToast(msg, isError = false) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.className = 'toast ' + (isError ? 'error' : 'success');
      setTimeout(() => { t.className = 'toast'; }, 3500);
    }

    function switchTab(tabId) {
      currentTab = tabId;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById(`tab-${tabId}`).classList.add('active');

      if (tabId === 'catalog') loadCatalog();
      if (tabId === 'holds') loadHolds();
      if (tabId === 'members') loadMembers();
      if (tabId === 'analytics') loadAnalytics();
    }

    // ------------------------------------------------------------------
    // KPI CARD CLICK HANDLERS (Jumping / Highlighting / Details)
    // ------------------------------------------------------------------
    function handleKpiClick(type) {
      if (type === 'total') {
        switchTab('catalog');
        resetFilters();
        highlightElement(document.getElementById('catalog-panel'));
        showToast('Viewing Total Inventory (500 copies)');
      } else if (type === 'available') {
        switchTab('catalog');
        switchCatalogPart('Available');
        highlightElement(document.getElementById('part-btn-available'));
        showToast('Viewing Available Books');
      } else if (type === 'issued') {
        switchTab('catalog');
        switchCatalogPart('Issued');
        highlightElement(document.getElementById('part-btn-issued'));
        showToast('Viewing Issued Books');
      } else if (type === 'overdue') {
        openOverdueLoansModal();
      } else if (type === 'fines') {
        openFinesBreakdownModal();
      } else if (type === 'holds') {
        switchTab('holds');
        highlightElement(document.getElementById('tab-holds'));
        showToast('Viewing Active Waitlist Holds');
      }
    }

    function highlightElement(el) {
      if (!el) return;
      el.classList.remove('pulse-highlight');
      void el.offsetWidth; // trigger reflow
      el.classList.add('pulse-highlight');
    }

    async function openOverdueLoansModal() {
      const res = await fetch('/api/loans');
      const data = await res.json();
      const overdueLoans = (data.loans || []).filter(l => l.status === 'Overdue');
      const tbody = document.getElementById('overdue-table-body');

      if (overdueLoans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:25px; color:var(--success); font-weight:700;">✓ Excellent! There are currently no overdue loans.</td></tr>';
      } else {
        tbody.innerHTML = overdueLoans.map(l => `
          <tr>
            <td><strong>${escapeHtml(l.book_title)}</strong> (Copy #${l.book_id})</td>
            <td>
              <span class="badge badge-mid">#M-${l.member_id}</span> 
              <strong>${escapeHtml(l.member_name)}</strong>
              <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(l.member_phone || l.member_email || '—')}</div>
            </td>
            <td><strong>${l.due_date}</strong></td>
            <td><span class="badge badge-overdue">+${l.overdue_days} days</span></td>
            <td><strong style="color:var(--danger);">$${l.fine_amount ? l.fine_amount.toFixed(2) : '0.00'}</strong></td>
            <td>
              <button class="btn-sm btn-primary" onclick="closeModal('modal-overdue-details'); openReceiveBookModal(${l.book_id})">📥 Receive</button>
            </td>
          </tr>
        `).join('');
      }
      openModal('modal-overdue-details');
    }

    async function openFinesBreakdownModal() {
      const res = await fetch('/api/loans');
      const data = await res.json();
      const finesLoans = (data.loans || []).filter(l => l.fine_amount > 0);
      const tbody = document.getElementById('fines-table-body');

      if (finesLoans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:25px; color:var(--success); font-weight:700;">✓ Zero outstanding fines!</td></tr>';
      } else {
        tbody.innerHTML = finesLoans.map(l => `
          <tr>
            <td>
              <span class="badge badge-mid">#M-${l.member_id}</span> 
              <strong>${escapeHtml(l.member_name)}</strong>
              <div style="font-size:11px; color:var(--text-muted);">${escapeHtml(l.member_phone || '—')}</div>
            </td>
            <td><strong>${escapeHtml(l.book_title)}</strong> (Copy #${l.book_id})</td>
            <td><span class="badge badge-overdue">+${l.overdue_days} days</span></td>
            <td><strong style="color:var(--danger); font-size:14px;">$${l.fine_amount.toFixed(2)}</strong></td>
            <td>
              <button class="btn-sm btn-success" onclick="closeModal('modal-fines-details'); openReceiveBookModal(${l.book_id})">📥 Settle & Receive</button>
            </td>
          </tr>
        `).join('');
      }
      openModal('modal-fines-details');
    }

    // ------------------------------------------------------------------
    // SWITCH BETWEEN PART 1 (AVAILABLE) AND PART 2 (ISSUED)
    // ------------------------------------------------------------------
    function switchCatalogPart(part) {
      currentPart = part;
      currentPage = 1;

      const btnAvail = document.getElementById('part-btn-available');
      const btnIssued = document.getElementById('part-btn-issued');

      if (part === 'Available') {
        btnAvail.classList.add('active');
        btnIssued.classList.remove('active');
      } else {
        btnIssued.classList.add('active');
        btnAvail.classList.remove('active');
      }

      renderCatalogHeaders();
      loadCatalog();
    }

    function renderCatalogHeaders() {
      const thead = document.getElementById('catalog-table-head');
      if (currentPart === 'Available') {
        thead.innerHTML = `
          <tr>
            <th style="width: 50px;">ID</th>
            <th>Title & Author</th>
            <th>Genre</th>
            <th>ISBN</th>
            <th>Shelf Location</th>
            <th>Status</th>
            <th style="width: 130px; text-align:center;">Action</th>
          </tr>
        `;
      } else {
        thead.innerHTML = `
          <tr>
            <th style="width: 50px;">ID</th>
            <th>Book Title</th>
            <th>Currently With (Borrower & Member ID)</th>
            <th>Contact</th>
            <th>Issued Date</th>
            <th>Due Date</th>
            <th>Status / Overdue</th>
            <th style="width: 140px; text-align:center;">Action</th>
          </tr>
        `;
      }
    }

    // ------------------------------------------------------------------
    // LOAD CATALOG DATA
    // ------------------------------------------------------------------
    async function loadCatalog() {
      const q = document.getElementById('catalog-search').value.trim();
      const genre = document.getElementById('filter-genre').value;
      const sort = document.getElementById('filter-sort').value;

      const url = `/api/books?status=${currentPart}&q=${encodeURIComponent(q)}&genre=${encodeURIComponent(genre)}&sort=${sort}&page=${currentPage}&limit=${pageSize}`;
      const res = await fetch(url);
      const data = await res.json();

      totalBooks = data.total;
      updateKpis(data.kpis);

      document.getElementById('part-count-avail').textContent = data.kpis.available;
      document.getElementById('part-count-issued').textContent = data.kpis.issued;

      const start = totalBooks > 0 ? (currentPage - 1) * pageSize + 1 : 0;
      const end = Math.min(currentPage * pageSize, totalBooks);
      document.getElementById('page-info').textContent = totalBooks > 0
        ? `Showing ${start} to ${end} of ${totalBooks} ${currentPart.toLowerCase()} books`
        : `No ${currentPart.toLowerCase()} books found`;
      document.getElementById('btn-prev-page').disabled = currentPage === 1;
      document.getElementById('btn-next-page').disabled = end >= totalBooks;

      const tbody = document.getElementById('books-table-body');
      if (!data.books || data.books.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:35px; color:var(--text-muted);">No ${currentPart.toLowerCase()} books match the search/filter criteria.</td></tr>`;
      } else {
        if (currentPart === 'Available') {
          tbody.innerHTML = data.books.map(b => `
            <tr>
              <td><strong>#${b.id}</strong></td>
              <td>
                <div style="font-weight:700; color:var(--text);">${escapeHtml(b.title)}</div>
                <div style="font-size:12px; color:var(--text-muted);">${escapeHtml(b.author)}</div>
              </td>
              <td><span class="badge badge-genre">${escapeHtml(b.genre || 'General')}</span></td>
              <td><code>${escapeHtml(b.isbn || '—')}</code></td>
              <td><span style="font-size:12px; color:var(--text-muted);">📍 ${escapeHtml(b.shelf_location || 'A-01')}</span></td>
              <td><span class="badge badge-avail">${b.status}</span></td>
              <td style="text-align:center; display:flex; gap:4px; justify-content:center;">
                <button class="btn-sm btn-success" onclick="openGiveBookModal(${b.id}, '${escapeHtml(b.title)}', '${escapeHtml(b.author)}')">📤 Give</button>
                <button class="btn-sm btn-secondary" onclick="showBookBarcodeModal(${b.id}, '${escapeHtml(b.title)}', '${escapeHtml(b.isbn)}', '${escapeHtml(b.shelf_location)}')" title="View & Print Barcode">🏷️</button>
              </td>
            </tr>
          `).join('');
        } else {
          // Issued Books Table View (Includes Unique Member ID)
          tbody.innerHTML = data.books.map(b => {
            const isOverdue = b.overdue_days > 0;
            const midBadge = b.member_id ? `<span class="badge badge-mid">#M-${b.member_id}</span>` : '';
            return `
              <tr>
                <td><strong>#${b.id}</strong></td>
                <td>
                  <div style="font-weight:700; color:var(--text);">${escapeHtml(b.title)}</div>
                  <div style="font-size:12px; color:var(--text-muted);">${escapeHtml(b.author)} (📍 ${escapeHtml(b.shelf_location || 'A-01')})</div>
                </td>
                <td>
                  <div style="display:flex; align-items:center; gap:6px;">
                    ${midBadge}
                    <strong>${escapeHtml(b.borrower_name || 'Borrower')}</strong>
                  </div>
                </td>
                <td><span style="font-size:12px; color:var(--text-muted);">${escapeHtml(b.borrower_phone || b.borrower_email || '—')}</span></td>
                <td>${b.issue_date || '—'}</td>
                <td><strong>${b.due_date || '—'}</strong></td>
                <td>
                  ${isOverdue 
                    ? `<span class="badge badge-overdue">⚠️ +${b.overdue_days} days ($${b.fine_amount ? b.fine_amount.toFixed(2) : '0.00'})</span>` 
                    : `<span class="badge badge-avail">On schedule</span>`
                  }
                </td>
                <td style="text-align:center;">
                  <button class="btn-sm btn-primary" onclick="openReceiveBookModal(${b.id})">📥 Receive Book</button>
                </td>
              </tr>
            `;
          }).join('');
        }
      }
    }

    function applyFilters() { currentPage = 1; loadCatalog(); }
    function resetFilters() {
      document.getElementById('catalog-search').value = '';
      document.getElementById('filter-genre').value = 'All';
      document.getElementById('filter-sort').value = 'id_asc';
      currentPage = 1;
      loadCatalog();
    }
    function prevPage() { if (currentPage > 1) { currentPage--; loadCatalog(); } }
    function nextPage() { currentPage++; loadCatalog(); }

    function updateKpis(k) {
      if (!k) return;
      document.getElementById('kpi-total').textContent = k.total;
      document.getElementById('kpi-available').textContent = k.available;
      document.getElementById('kpi-issued').textContent = k.issued;
      document.getElementById('kpi-overdue').textContent = k.overdue;
      document.getElementById('kpi-fines').textContent = '$' + k.fines.toFixed(2);
      document.getElementById('kpi-holds').textContent = k.holds || 0;
    }

    // ------------------------------------------------------------------
    // GIVE BOOK FLOW (With Live Member Search by Name, Phone, Email, ID)
    // ------------------------------------------------------------------
    async function openGiveBookModal(bookId, bookTitle, bookAuthor) {
      document.getElementById('give-book-id').value = bookId;
      document.getElementById('give-book-id-badge').textContent = `#${bookId}`;
      document.getElementById('give-book-title').textContent = bookTitle;
      document.getElementById('give-book-author').textContent = `by ${bookAuthor}`;

      // Reset selection state
      clearSelectedMember();
      isTypingNewBorrower = false;
      document.getElementById('give-new-borrower-wrap').style.display = 'none';
      document.getElementById('give-search-wrap').style.display = 'block';
      document.getElementById('btn-toggle-new-borrower').textContent = '+ Type New Borrower';
      document.getElementById('give-member-search-input').value = '';

      // Load all members for instant search
      const res = await fetch('/api/members');
      const data = await res.json();
      allMembers = data.members || [];
      renderMemberSearchResults(allMembers);

      openModal('modal-give-book');
    }

    function filterMemberSearch(query) {
      const q = query.trim().toLowerCase();
      if (!q) {
        renderMemberSearchResults(allMembers);
        return;
      }

      const filtered = allMembers.filter(m => {
        const idMatch = String(m.id) === q || `m-${m.id}` === q || `#m-${m.id}` === q;
        const nameMatch = (m.name || '').toLowerCase().includes(q);
        const phoneMatch = (m.phone || '').toLowerCase().includes(q);
        const emailMatch = (m.email || '').toLowerCase().includes(q);
        return idMatch || nameMatch || phoneMatch || emailMatch;
      });

      renderMemberSearchResults(filtered, q);
    }

    function renderMemberSearchResults(list, query = '') {
      const container = document.getElementById('give-member-search-results');
      if (!list || list.length === 0) {
        container.innerHTML = `
          <div style="padding:12px; font-size:12px; color:var(--text-muted); text-align:center;">
            No member found matching "${escapeHtml(query)}".<br>
            <a href="javascript:void(0)" onclick="toggleNewBorrowerForm()" style="color:var(--primary); font-weight:700;">Click here to type new borrower details</a>
          </div>
        `;
        return;
      }

      container.innerHTML = list.map(m => `
        <div class="member-search-item" onclick="selectMemberForGive(${m.id})">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <span class="badge badge-mid">#M-${m.id}</span>
              <strong style="margin-left:4px;">${escapeHtml(m.name)}</strong>
              <span style="font-size:11px; color:var(--text-muted); margin-left:4px;">(${escapeHtml(m.member_type)})</span>
            </div>
            <span style="font-size:11px; font-weight:600; color:${m.active_loans >= m.max_books ? 'var(--danger)' : 'var(--text-muted)'};">
              ${m.active_loans}/${m.max_books} books borrowed
            </span>
          </div>
          <div style="font-size:11px; color:var(--text-muted); margin-top:2px;">
            📞 ${escapeHtml(m.phone || 'No phone')} &bull; ✉️ ${escapeHtml(m.email)}
          </div>
        </div>
      `).join('');
    }

    function selectMemberForGive(memberId) {
      const member = allMembers.find(m => m.id === memberId);
      if (!member) return;

      document.getElementById('give-selected-member-id').value = member.id;
      document.getElementById('give-selected-mid').textContent = `#M-${member.id}`;
      document.getElementById('give-selected-mname').textContent = member.name;
      document.getElementById('give-selected-mcontact').textContent = `📞 ${member.phone || '—'} • ✉️ ${member.email}`;

      document.getElementById('give-selected-member-box').style.display = 'block';
      document.getElementById('give-search-wrap').style.display = 'none';
      document.getElementById('give-new-borrower-wrap').style.display = 'none';
      isTypingNewBorrower = false;
    }

    function clearSelectedMember() {
      document.getElementById('give-selected-member-id').value = '';
      document.getElementById('give-selected-member-box').style.display = 'none';
      document.getElementById('give-search-wrap').style.display = 'block';
      document.getElementById('give-member-search-input').value = '';
      renderMemberSearchResults(allMembers);
    }

    function toggleNewBorrowerForm() {
      isTypingNewBorrower = !isTypingNewBorrower;
      const wrap = document.getElementById('give-new-borrower-wrap');
      const searchWrap = document.getElementById('give-search-wrap');
      const btn = document.getElementById('btn-toggle-new-borrower');

      if (isTypingNewBorrower) {
        wrap.style.display = 'block';
        searchWrap.style.display = 'none';
        document.getElementById('give-selected-member-box').style.display = 'none';
        btn.textContent = '← Choose Existing';
        document.getElementById('give-new-name').focus();
      } else {
        wrap.style.display = 'none';
        searchWrap.style.display = 'block';
        btn.textContent = '+ Type New Borrower';
      }
    }

    async function confirmGiveBook() {
      const book_id = document.getElementById('give-book-id').value;
      const loan_days = document.getElementById('give-loan-days').value;
      const selectedMemberId = document.getElementById('give-selected-member-id').value;
      let payload = { book_id, loan_days };

      if (!isTypingNewBorrower) {
        if (!selectedMemberId) {
          showToast('Please search and select a member from the list.', true);
          return;
        }
        payload.member_id = selectedMemberId;
      } else {
        const name = document.getElementById('give-new-name').value.trim();
        const contact = document.getElementById('give-new-contact').value.trim();
        const mtype = document.getElementById('give-new-type').value;

        if (!name) {
          showToast('Please enter the borrower full name.', true);
          return;
        }
        payload.new_borrower_name = name;
        payload.new_borrower_contact = contact;
        payload.new_borrower_type = mtype;
      }

      const res = await fetch('/api/loans', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (res.ok) {
        showToast(data.message);
        closeModal('modal-give-book');
        loadCatalog();
      } else {
        showToast(data.error, true);
      }
    }

    // ------------------------------------------------------------------
    // RECEIVE BOOK FLOW (CONFIRMATION POPUP - FIXED)
    // ------------------------------------------------------------------
    async function openReceiveBookModal(bookId) {
      try {
        const res = await fetch(`/api/books/${bookId}/loan_info`);
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || 'Failed to fetch loan information.', true);
          return;
        }

        const info = data.loan_info;
        document.getElementById('receive-book-id').value = bookId;
        document.getElementById('receive-book-title').textContent = info.title;
        document.getElementById('receive-book-author').textContent = `by ${info.author} (Copy #${bookId})`;
        document.getElementById('receive-book-shelf').textContent = info.shelf_location || 'Shelf A-01';

        document.getElementById('receive-borrower-mid').textContent = `#M-${info.member_id}`;
        document.getElementById('receive-borrower-name').textContent = info.borrower_name || 'Patron';
        document.getElementById('receive-borrower-contact').textContent = info.borrower_phone || info.borrower_email || 'No contact on file';
        document.getElementById('receive-issue-date').textContent = info.issue_date;
        document.getElementById('receive-due-date').textContent = info.due_date;

        const alertDiv = document.getElementById('receive-overdue-alert');
        if (info.overdue_days > 0) {
          alertDiv.innerHTML = `<span style="color:var(--danger); font-weight:800;">⚠️ OVERDUE by ${info.overdue_days} days! Fine due: $${info.fine_amount ? info.fine_amount.toFixed(2) : '0.00'}</span>`;
        } else {
          alertDiv.innerHTML = `<span style="color:var(--success); font-weight:700;">✓ Returned on schedule. No overdue fines.</span>`;
        }

        document.getElementById('receive-condition-check').checked = true;
        openModal('modal-receive-book');
      } catch (err) {
        showToast('Connection error: ' + err.message, true);
      }
    }

    async function confirmReceiveBook() {
      const bookId = document.getElementById('receive-book-id').value;
      const checked = document.getElementById('receive-condition-check').checked;
      if (!checked) {
        if (!confirm('Proceed without condition inspection check?')) return;
      }

      try {
        const res = await fetch(`/api/books/${bookId}/return`, { method: 'POST' });
        const data = await res.json();

        if (res.ok) {
          showToast(data.message);
          closeModal('modal-receive-book');
          loadCatalog();
        } else {
          showToast(data.error || 'Return action failed.', true);
        }
      } catch (err) {
        showToast('Connection error: ' + err.message, true);
      }
    }

    // ------------------------------------------------------------------
    // HOLDS & MEMBERS
    // ------------------------------------------------------------------
    async function loadHolds() {
      const res = await fetch('/api/reservations');
      const data = await res.json();
      const tbody = document.getElementById('holds-table-body');
      if (!data.reservations || data.reservations.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px;">No pending holds.</td></tr>';
        return;
      }
      tbody.innerHTML = data.reservations.map(r => `
        <tr>
          <td><strong>#H-${r.id}</strong></td>
          <td><strong>${escapeHtml(r.book_title)}</strong> (Copy #${r.book_id})</td>
          <td>
            <span class="badge badge-mid">#M-${r.member_id}</span>
            <strong style="margin-left:4px;">${escapeHtml(r.member_name)}</strong> 
            <span style="font-size:11px; color:var(--text-muted);">(${escapeHtml(r.member_type)})</span>
          </td>
          <td>${r.reserve_date}</td>
          <td><span class="badge badge-issued">${r.status}</span></td>
          <td>
            <button class="btn-sm btn-danger" onclick="cancelHold(${r.id})">Cancel Hold</button>
          </td>
        </tr>
      `).join('');
    }

    async function cancelHold(holdId) {
      if (!confirm('Cancel this hold?')) return;
      const res = await fetch(`/api/reservations/${holdId}`, { method: 'DELETE' });
      const data = await res.json();
      if (res.ok) { showToast(data.message); loadHolds(); } else { showToast(data.error, true); }
    }

    async function loadMembers() {
      const res = await fetch('/api/members');
      const data = await res.json();
      allMembers = data.members;
      const tbody = document.getElementById('members-table-body');
      tbody.innerHTML = allMembers.map(m => `
        <tr>
          <td><strong style="color:var(--primary); font-family:monospace;">#M-${m.id}</strong></td>
          <td><strong>${escapeHtml(m.name)}</strong></td>
          <td>${escapeHtml(m.email)}</td>
          <td>${escapeHtml(m.phone || '—')}</td>
          <td><span class="badge badge-genre">${escapeHtml(m.member_type)}</span></td>
          <td><strong style="color:${m.active_loans >= m.max_books ? 'var(--danger)' : 'var(--text)'}">${m.active_loans}</strong></td>
          <td>${m.max_books} books</td>
          <td style="display:flex; gap:4px;">
            <button class="btn-sm btn-secondary" onclick="openLibraryCardModal(${m.id})" title="Print Library Card">🪪 Card</button>
            <button class="btn-sm btn-danger" onclick="deleteMember(${m.id}, '${escapeHtml(m.name)}', ${m.active_loans})">🗑️</button>
          </td>
        </tr>
      `).join('');
    }

    function openAddMemberModal() {
      document.getElementById('member-name-input').value = '';
      document.getElementById('member-email-input').value = '';
      document.getElementById('member-phone-input').value = '';
      document.getElementById('member-type-select').value = 'Student';
      document.getElementById('member-limit-input').value = '3';
      openModal('modal-member');
    }

    async function saveMember() {
      const name = document.getElementById('member-name-input').value.trim();
      const email = document.getElementById('member-email-input').value.trim();
      const phone = document.getElementById('member-phone-input').value.trim();
      const member_type = document.getElementById('member-type-select').value;
      const max_books = parseInt(document.getElementById('member-limit-input').value, 10);

      if (!name || !email) { showToast('Name and Email required.', true); return; }

      const res = await fetch('/api/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, phone, member_type, max_books })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message);
        closeModal('modal-member');
        loadMembers();
      } else {
        showToast(data.error, true);
      }
    }

    async function deleteMember(id, name, activeLoans) {
      if (activeLoans > 0) {
        showToast(`Cannot delete member with ${activeLoans} active unreturned loan(s).`, true);
        return;
      }
      if (!confirm(`Delete member '${name}' (#M-${id})?`)) return;
      const res = await fetch(`/api/members/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (res.ok) { showToast(data.message); loadMembers(); } else { showToast(data.error, true); }
    }

    // ------------------------------------------------------------------
    // ADD BOOK & ISBN LOOKUP
    // ------------------------------------------------------------------
    function openAddBookModal() {
      document.getElementById('book-title-input').value = '';
      document.getElementById('book-author-input').value = '';
      document.getElementById('book-isbn-input').value = '';
      document.getElementById('book-shelf-input').value = 'Shelf A-01';
      document.getElementById('isbn-autofill-input').value = '';
      document.getElementById('isbn-status').textContent = '';
      openModal('modal-book');
    }

    async function lookupISBN() {
      const isbn = document.getElementById('isbn-autofill-input').value.trim().replace(/[-\\s]/g, '');
      const statusEl = document.getElementById('isbn-status');
      if (!isbn) {
        statusEl.textContent = 'Please enter an ISBN.';
        statusEl.style.color = 'var(--danger)';
        return;
      }
      statusEl.textContent = 'Querying Open Library database...';
      statusEl.style.color = 'var(--primary)';

      try {
        const res = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`);
        const data = await res.json();
        const key = `ISBN:${isbn}`;

        if (!data[key]) {
          statusEl.textContent = 'Book not found in Open Library. Fill fields manually.';
          statusEl.style.color = 'var(--warning)';
          return;
        }

        const b = data[key];
        document.getElementById('book-title-input').value = b.title || '';
        document.getElementById('book-author-input').value = b.authors ? b.authors.map(a => a.name).join(', ') : '';
        document.getElementById('book-isbn-input').value = isbn;
        statusEl.textContent = `✓ Auto-filled: "${b.title}"!`;
        statusEl.style.color = 'var(--success)';
      } catch (e) {
        statusEl.textContent = 'Network error looking up ISBN. Fill manually.';
        statusEl.style.color = 'var(--danger)';
      }
    }

    async function saveBook() {
      const title = document.getElementById('book-title-input').value.trim();
      const author = document.getElementById('book-author-input').value.trim();
      const genre = document.getElementById('book-genre-input').value;
      const shelf_location = document.getElementById('book-shelf-input').value.trim();
      const isbn = document.getElementById('book-isbn-input').value.trim();
      const cover_url = isbn ? `https://covers.openlibrary.org/b/isbn/${isbn}-M.jpg` : '';

      if (!title || !author) {
        showToast('Title and Author are required.', true);
        return;
      }

      const res = await fetch('/api/books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, author, genre, shelf_location, isbn, cover_url })
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message);
        closeModal('modal-book');
        loadCatalog();
      } else {
        showToast(data.error, true);
      }
    }

    // ------------------------------------------------------------------
    // ANALYTICS & CHARTS
    // ------------------------------------------------------------------
    async function loadAnalytics() {
      const res = await fetch('/api/analytics');
      const data = await res.json();

      const total = data.total_books || 1;
      const pAvail = data.available / total;
      const pIssued = data.issued / total;

      const r = 65;
      const c = 2 * Math.PI * r;
      const sAvail = c * pAvail;
      const sIssued = c * pIssued;

      document.getElementById('donut-chart-box').innerHTML = `
        <div style="display:flex; align-items:center; gap:20px;">
          <svg width="150" height="150" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="${r}" fill="none" stroke="var(--border)" stroke-width="24" />
            <circle cx="100" cy="100" r="${r}" fill="none" stroke="#16a34a" stroke-width="24"
              stroke-dasharray="${sAvail} ${c}" stroke-dashoffset="0" transform="rotate(-90 100 100)" />
            <circle cx="100" cy="100" r="${r}" fill="none" stroke="#dc2626" stroke-width="24"
              stroke-dasharray="${sIssued} ${c}" stroke-dashoffset="${-sAvail}" transform="rotate(-90 100 100)" />
            <text x="100" y="96" text-anchor="middle" font-size="22" font-weight="800" fill="currentColor">${total}</text>
            <text x="100" y="116" text-anchor="middle" font-size="11" font-weight="700" fill="var(--text-muted)">BOOKS</text>
          </svg>
          <div style="font-size:12px; display:flex; flex-direction:column; gap:6px;">
            <div><span style="display:inline-block; width:10px; height:10px; background:#16a34a; border-radius:2px; margin-right:6px;"></span>Available: <strong>${data.available}</strong> (${Math.round(pAvail*100)}%)</div>
            <div><span style="display:inline-block; width:10px; height:10px; background:#dc2626; border-radius:2px; margin-right:6px;"></span>Issued: <strong>${data.issued}</strong> (${Math.round(pIssued*100)}%)</div>
          </div>
        </div>
      `;

      const maxG = Math.max(...data.genres.map(g => g.count), 1);
      document.getElementById('bar-chart-box').innerHTML = data.genres.map(g => {
        const h = Math.round((g.count / maxG) * 140);
        return `
          <div style="flex:1; display:flex; flex-direction:column; align-items:center; gap:4px;">
            <div style="font-size:11px; font-weight:700; color:var(--text);">${g.count}</div>
            <div style="width:100%; max-width:40px; height:${h}px; background:var(--primary); border-radius:4px 4px 0 0;"></div>
            <div style="font-size:10px; color:var(--text-muted); text-align:center; height:28px; overflow:hidden;">${escapeHtml(g.genre)}</div>
          </div>
        `;
      }).join('');
    }

    function openModal(id) { document.getElementById(id).classList.add('active'); }
    function closeModal(id) { document.getElementById(id).classList.remove('active'); }
    function exportBooksCSV() { window.location.href = '/api/export/books.csv'; }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
    }

    renderCatalogHeaders();
    loadCatalog();
  </script>
</body>
</html>
"""


# ----------------------------------------------------------------------
# Backend Request Handler
# ----------------------------------------------------------------------
class LibraryHTTPHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status_code=HTTPStatus.OK):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Serve Web UI
        if path in ("/", "/index.html"):
            update_overdue_fines()
            body = FULL_WEB_APP_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # CSV Export
        if path == "/api/export/books.csv":
            output = io.StringIO()
            w = csv.writer(output)
            w.writerow(["Copy ID", "Title", "Author", "ISBN", "Genre", "Shelf Location", "Status"])
            with get_db() as conn:
                for r in conn.execute("SELECT id, title, author, isbn, genre, shelf_location, status FROM books ORDER BY id ASC"):
                    w.writerow([r["id"], r["title"], r["author"], r["isbn"], r["genre"], r["shelf_location"], r["status"]])
            data = output.getvalue().encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=library_books.csv")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Get Loan Info for Return Confirmation (FIXED: split index 3)
        if path.startswith("/api/books/") and path.endswith("/loan_info"):
            try:
                b_id = int(path.split("/")[3])
            except (IndexError, ValueError):
                self.send_json({"error": "Invalid book ID in path"}, HTTPStatus.BAD_REQUEST)
                return

            with get_db() as conn:
                sql = """
                    SELECT b.id as book_id, b.title, b.author, b.isbn, b.shelf_location,
                           l.id as loan_id, l.issue_date, l.due_date, l.fine_amount,
                           m.id as member_id, m.name as borrower_name, m.email as borrower_email, m.phone as borrower_phone
                    FROM books b
                    JOIN loans l ON b.id = l.book_id AND l.status IN ('Active', 'Overdue')
                    JOIN members m ON l.member_id = m.id
                    WHERE b.id = ?
                """
                row = conn.execute(sql, (b_id,)).fetchone()
                if not row:
                    self.send_json({"error": "No active loan found for this book copy."}, HTTPStatus.NOT_FOUND)
                    return

                d = dict(row)
                today = datetime.now()
                due = datetime.strptime(d["due_date"], "%Y-%m-%d")
                d["overdue_days"] = max(0, (today - due).days) if today > due else 0
                self.send_json({"loan_info": d})
            return

        # Get Books (Filtered by Available or Issued Part)
        if path == "/api/books":
            q = query.get("q", [""])[0].strip()
            genre = query.get("genre", ["All"])[0]
            status = query.get("status", ["Available"])[0]
            sort = query.get("sort", ["id_asc"])[0]
            page = int(query.get("page", [1])[0])
            limit = int(query.get("limit", [25])[0])
            offset = (page - 1) * limit

            where = []
            params = []

            # Part status filter
            if status in ("Available", "Issued"):
                where.append("b.status = ?")
                params.append(status)

            if q:
                where.append("(b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?)")
                like = f"%{q}%"
                params.extend([like, like, like])

            if genre != "All":
                where.append("b.genre = ?")
                params.append(genre)

            where_sql = ("WHERE " + " AND ".join(where)) if where else ""

            sort_map = {
                "id_asc": "b.id ASC",
                "title_asc": "b.title ASC",
                "title_desc": "b.title DESC",
                "author_asc": "b.author ASC",
                "shelf_asc": "b.shelf_location ASC",
            }
            order_sql = sort_map.get(sort, "b.id ASC")

            with get_db() as conn:
                count_sql = f"SELECT COUNT(*) FROM books b {where_sql}"
                total = conn.execute(count_sql, params).fetchone()[0]

                if status == "Issued":
                    # Join loan & borrower details for Issued part
                    fetch_sql = f"""
                        SELECT b.id, b.title, b.author, b.isbn, b.genre, b.shelf_location, b.cover_url, b.status,
                               l.id as loan_id, l.issue_date, l.due_date, l.fine_amount,
                               m.id as member_id, m.name as borrower_name, m.phone as borrower_phone, m.email as borrower_email
                        FROM books b
                        LEFT JOIN loans l ON b.id = l.book_id AND l.status IN ('Active', 'Overdue')
                        LEFT JOIN members m ON l.member_id = m.id
                        {where_sql}
                        ORDER BY {order_sql} LIMIT ? OFFSET ?
                    """
                else:
                    fetch_sql = f"""
                        SELECT b.id, b.title, b.author, b.isbn, b.genre, b.shelf_location, b.cover_url, b.status
                        FROM books b
                        {where_sql}
                        ORDER BY {order_sql} LIMIT ? OFFSET ?
                    """

                rows = conn.execute(fetch_sql, params + [limit, offset]).fetchall()
                today = datetime.now()

                books = []
                for r in rows:
                    d = dict(r)
                    if d.get("due_date"):
                        due = datetime.strptime(d["due_date"], "%Y-%m-%d")
                        d["overdue_days"] = max(0, (today - due).days) if today > due else 0
                    books.append(d)

                kpi_row = conn.execute(
                    """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status='Available' THEN 1 ELSE 0 END) as available,
                        SUM(CASE WHEN status='Issued' THEN 1 ELSE 0 END) as issued
                    FROM books
                    """
                ).fetchone()

                overdue_row = conn.execute(
                    "SELECT COUNT(*) as count, SUM(fine_amount) as total_fines FROM loans WHERE status = 'Overdue'"
                ).fetchone()

                holds_count = conn.execute("SELECT COUNT(*) FROM reservations WHERE status='Waiting'").fetchone()[0]

                kpis = {
                    "total": kpi_row["total"] or 0,
                    "available": kpi_row["available"] or 0,
                    "issued": kpi_row["issued"] or 0,
                    "overdue": overdue_row["count"] or 0,
                    "fines": overdue_row["total_fines"] or 0.0,
                    "holds": holds_count,
                }

            self.send_json({"books": books, "total": total, "kpis": kpis})
            return

        # Get Loans (Full List for Overdue & Fines Details)
        if path == "/api/loans":
            update_overdue_fines()
            with get_db() as conn:
                sql = """
                    SELECT l.id, l.book_id, b.title as book_title, b.shelf_location,
                           l.member_id, m.name as member_name, m.phone as member_phone, m.email as member_email,
                           m.member_type, l.issue_date, l.due_date, l.fine_amount, l.status
                    FROM loans l
                    JOIN books b ON l.book_id = b.id
                    JOIN members m ON l.member_id = m.id
                    WHERE l.status IN ('Active', 'Overdue')
                    ORDER BY CASE WHEN l.status='Overdue' THEN 1 ELSE 2 END, l.due_date ASC
                """
                rows = conn.execute(sql).fetchall()
                today = datetime.now()
                loans = []
                for r in rows:
                    d = dict(r)
                    due = datetime.strptime(d["due_date"], "%Y-%m-%d")
                    d["overdue_days"] = max(0, (today - due).days) if today > due else 0
                    loans.append(d)
            self.send_json({"loans": loans})
            return


        # Get Patron Dashboard data (Self-Service Kiosk)
        if path.startswith("/api/patron/"):
            raw_q = unquote(path[len("/api/patron/"):].strip())
            with get_db() as conn:
                member = None
                clean_q = raw_q.replace("#", "").replace("m-", "").replace("M-", "").strip()
                if clean_q.isdigit():
                    member = conn.execute("SELECT * FROM members WHERE id = ?", (int(clean_q),)).fetchone()
                if not member:
                    member = conn.execute(
                        "SELECT * FROM members WHERE LOWER(email) = ? OR phone = ? OR LOWER(name) LIKE ?",
                        (raw_q.lower(), raw_q, f"%{raw_q.lower()}%")
                    ).fetchone()
                
                if not member:
                    self.send_json({"error": "Patron not found. Enter Member ID (e.g. #M-1) or email."}, HTTPStatus.NOT_FOUND)
                    return

                m_id = member["id"]
                loans = conn.execute("""
                    SELECT l.id, l.book_id, b.title as book_title, b.author as book_author, b.shelf_location,
                           l.issue_date, l.due_date, l.fine_amount, l.status
                    FROM loans l
                    JOIN books b ON l.book_id = b.id
                    WHERE l.member_id = ? AND l.status IN ('Active', 'Overdue')
                    ORDER BY l.due_date ASC
                """, (m_id,)).fetchall()

                holds = conn.execute("""
                    SELECT r.id, r.book_id, b.title as book_title, b.author as book_author,
                           r.reserve_date, r.status
                    FROM reservations r
                    JOIN books b ON r.book_id = b.id
                    WHERE r.member_id = ? AND r.status = 'Waiting'
                    ORDER BY r.id ASC
                """, (m_id,)).fetchall()

            self.send_json({
                "member": dict(member),
                "loans": [dict(r) for r in loans],
                "holds": [dict(r) for r in holds]
            })
            return

        # Get Reservations
        if path == "/api/reservations":
            with get_db() as conn:
                sql = """
                    SELECT r.id, r.book_id, b.title as book_title, r.member_id, m.name as member_name,
                           m.member_type, r.reserve_date, r.status
                    FROM reservations r
                    JOIN books b ON r.book_id = b.id
                    JOIN members m ON r.member_id = m.id
                    WHERE r.status = 'Waiting'
                    ORDER BY r.id ASC
                """
                reservations = [dict(r) for r in conn.execute(sql).fetchall()]
            self.send_json({"reservations": reservations})
            return

        # Get Members
        if path == "/api/members":
            with get_db() as conn:
                sql = """
                    SELECT m.id, m.name, m.email, m.phone, m.member_type, m.max_books,
                           COUNT(l.id) as active_loans
                    FROM members m
                    LEFT JOIN loans l ON m.id = l.member_id AND l.status IN ('Active', 'Overdue')
                    GROUP BY m.id
                    ORDER BY m.id ASC
                """
                members = [dict(r) for r in conn.execute(sql).fetchall()]
            self.send_json({"members": members})
            return

        # Analytics
        if path == "/api/analytics":
            with get_db() as conn:
                b_stats = conn.execute(
                    "SELECT COUNT(*) as total, SUM(CASE WHEN status='Available' THEN 1 ELSE 0 END) as available, SUM(CASE WHEN status='Issued' THEN 1 ELSE 0 END) as issued FROM books"
                ).fetchone()
                overdue_count = conn.execute("SELECT COUNT(*) FROM loans WHERE status = 'Overdue'").fetchone()[0]
                genres = [dict(r) for r in conn.execute("SELECT genre, COUNT(*) as count FROM books GROUP BY genre ORDER BY count DESC").fetchall()]

            self.send_json({
                "total_books": b_stats["total"] or 0,
                "available": b_stats["available"] or 0,
                "issued": b_stats["issued"] or 0,
                "overdue": overdue_count,
                "genres": genres,
            })
            return

        self.send_json({"error": "Not Found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}

        # Issue / Give Book
        if path == "/api/loans":
            b_id = int(body.get("book_id", 0))
            loan_days = int(body.get("loan_days", 14))
            m_id = body.get("member_id")

            with get_db() as conn:
                # If typing new borrower name
                if not m_id:
                    name = body.get("new_borrower_name", "").strip()
                    contact = body.get("new_borrower_contact", "").strip()
                    mtype = body.get("new_borrower_type", "Student")
                    if not name:
                        self.send_json({"error": "Borrower name is required."}, HTTPStatus.BAD_REQUEST)
                        return

                    email = contact if "@" in contact else f"{name.lower().replace(' ', '')}@library.local"
                    phone = contact if "@" not in contact else ""
                    try:
                        c = conn.execute(
                            "INSERT INTO members (name, email, phone, member_type, max_books) VALUES (?, ?, ?, ?, 3)",
                            (name, email, phone, mtype),
                        )
                        m_id = c.lastrowid
                    except sqlite3.IntegrityError:
                        row = conn.execute("SELECT id FROM members WHERE name = ? OR email = ?", (name, email)).fetchone()
                        m_id = row["id"]

                member = conn.execute("SELECT name, max_books FROM members WHERE id = ?", (m_id,)).fetchone()
                book = conn.execute("SELECT title, status FROM books WHERE id = ?", (b_id,)).fetchone()

                if not book or book["status"] != "Available":
                    self.send_json({"error": "This book is not available to issue."}, HTTPStatus.BAD_REQUEST)
                    return

                issue_date = datetime.now().strftime("%Y-%m-%d")
                due_date = (datetime.now() + timedelta(days=loan_days)).strftime("%Y-%m-%d")

                conn.execute(
                    "INSERT INTO loans (book_id, member_id, issue_date, due_date, fine_amount, status) VALUES (?, ?, ?, ?, 0.0, 'Active')",
                    (b_id, m_id, issue_date, due_date),
                )
                conn.execute("UPDATE books SET status = 'Issued' WHERE id = ?", (b_id,))
                conn.commit()

            self.send_json({"message": f"Book '{book['title']}' given to {member['name']} (#M-{m_id})! Due on {due_date}."})
            return

        # Receive / Return Book (FIXED: split index 3)
        if path.startswith("/api/books/") and path.endswith("/return"):
            try:
                b_id = int(path.split("/")[3])
            except (IndexError, ValueError):
                self.send_json({"error": "Invalid book ID in path"}, HTTPStatus.BAD_REQUEST)
                return

            today_str = datetime.now().strftime("%Y-%m-%d")

            with get_db() as conn:
                book = conn.execute("SELECT title, status FROM books WHERE id = ?", (b_id,)).fetchone()
                if not book:
                    self.send_json({"error": "Book copy not found"}, HTTPStatus.NOT_FOUND)
                    return

                loan = conn.execute(
                    """
                    SELECT l.id, l.fine_amount, m.id as member_id, m.name as borrower_name
                    FROM loans l
                    JOIN members m ON l.member_id = m.id
                    WHERE l.book_id = ? AND l.status IN ('Active', 'Overdue')
                    """,
                    (b_id,),
                ).fetchone()

                if loan:
                    conn.execute(
                        "UPDATE loans SET status = 'Returned', return_date = ? WHERE id = ?",
                        (today_str, loan["id"]),
                    )

                # Check if there is an active hold
                hold = conn.execute(
                    """
                    SELECT r.id, r.member_id, m.name
                    FROM reservations r
                    JOIN members m ON r.member_id = m.id
                    WHERE r.book_id = ? AND r.status = 'Waiting'
                    ORDER BY r.id ASC
                    """,
                    (b_id,),
                ).fetchone()

                if hold:
                    conn.execute("UPDATE reservations SET status = 'Fulfilled' WHERE id = ?", (hold["id"],))
                    conn.execute("UPDATE books SET status = 'Available' WHERE id = ?", (b_id,))
                    conn.execute(
                        "INSERT INTO notifications (member_id, message, notice_type) VALUES (?, ?, 'Hold Ready')",
                        (hold["member_id"], f"Your reserved copy '{book['title']}' has arrived and is ready for pickup!"),
                    )
                    conn.commit()
                    self.send_json({"message": f"Book '{book['title']}' received back! Auto-held for waitlist patron {hold['name']} (#M-{hold['member_id']})."})
                    return

                conn.execute("UPDATE books SET status = 'Available' WHERE id = ?", (b_id,))
                conn.commit()

            borrower_info = f"{loan['borrower_name']} (#M-{loan['member_id']})" if loan else "Patron"
            self.send_json({"message": f"Book '{book['title']}' successfully received back from {borrower_info} and marked Available!"})
            return


        # Place a Hold / Reservation (Self-Service or Admin)
        if path == "/api/reservations":
            book_id = int(body.get("book_id", 0))
            member_id = int(body.get("member_id", 0))
            today_str = datetime.now().strftime("%Y-%m-%d")

            with get_db() as conn:
                book = conn.execute("SELECT title, status FROM books WHERE id = ?", (book_id,)).fetchone()
                member = conn.execute("SELECT name FROM members WHERE id = ?", (member_id,)).fetchone()
                if not book or not member:
                    self.send_json({"error": "Book or Member not found"}, HTTPStatus.NOT_FOUND)
                    return

                existing = conn.execute(
                    "SELECT id FROM reservations WHERE book_id = ? AND member_id = ? AND status = 'Waiting'",
                    (book_id, member_id),
                ).fetchone()
                if existing:
                    self.send_json({"error": f"{member['name']} already has an active hold on '{book['title']}'."}, HTTPStatus.CONFLICT)
                    return

                conn.execute(
                    "INSERT INTO reservations (book_id, member_id, reserve_date, status) VALUES (?, ?, ?, 'Waiting')",
                    (book_id, member_id, today_str),
                )
                conn.commit()

            self.send_json({"message": f"Hold placed for {member['name']} on '{book['title']}'!"}, HTTPStatus.CREATED)
            return

        # Cancel a Hold
        if path.startswith("/api/reservations/") and path.endswith("/cancel"):
            try:
                res_id = int(path.split("/")[3])
            except (IndexError, ValueError):
                self.send_json({"error": "Invalid hold ID"}, HTTPStatus.BAD_REQUEST)
                return
            with get_db() as conn:
                conn.execute("UPDATE reservations SET status = 'Cancelled' WHERE id = ?", (res_id,))
                conn.commit()
            self.send_json({"message": "Hold cancelled successfully."})
            return

        # Add Book
        if path == "/api/books":
            title = body.get("title", "").strip()
            author = body.get("author", "").strip()
            isbn = body.get("isbn", "").strip()
            genre = body.get("genre", "General").strip()
            shelf = body.get("shelf_location", "Shelf A-01").strip()
            cover = body.get("cover_url", "").strip()

            if not title or not author:
                self.send_json({"error": "Title and Author are required."}, HTTPStatus.BAD_REQUEST)
                return

            if not cover and isbn:
                cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

            with get_db() as conn:
                c = conn.execute(
                    "INSERT INTO books (title, author, isbn, genre, shelf_location, cover_url, status) VALUES (?, ?, ?, ?, ?, ?, 'Available')",
                    (title, author, isbn, genre, shelf, cover),
                )
                conn.commit()
                new_id = c.lastrowid
            self.send_json({"message": f"Book '{title}' added as Copy #{new_id}.", "id": new_id}, HTTPStatus.CREATED)
            return

        # Register Member
        if path == "/api/members":
            name = body.get("name", "").strip()
            email = body.get("email", "").strip()
            phone = body.get("phone", "").strip()
            mtype = body.get("member_type", "Student")
            max_b = int(body.get("max_books", 3))

            if not name or not email:
                self.send_json({"error": "Name and Email are required."}, HTTPStatus.BAD_REQUEST)
                return

            try:
                with get_db() as conn:
                    c = conn.execute(
                        "INSERT INTO members (name, email, phone, member_type, max_books) VALUES (?, ?, ?, ?, ?)",
                        (name, email, phone, mtype, max_b),
                    )
                    conn.commit()
                    m_id = c.lastrowid
                self.send_json({"message": f"Member '{name}' registered successfully (Member ID: #M-{m_id})."})
            except sqlite3.IntegrityError:
                self.send_json({"error": f"Email '{email}' is already registered."}, HTTPStatus.BAD_REQUEST)
            return

        self.send_json({"error": "Not Found"}, HTTPStatus.NOT_FOUND)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/reservations/"):
            r_id = int(path.split("/")[3])
            with get_db() as conn:
                conn.execute("DELETE FROM reservations WHERE id = ?", (r_id,))
                conn.commit()
            self.send_json({"message": f"Hold #{r_id} cancelled."})
            return

        if path.startswith("/api/members/"):
            m_id = int(path.split("/")[3])
            with get_db() as conn:
                active = conn.execute(
                    "SELECT COUNT(*) FROM loans WHERE member_id = ? AND status IN ('Active', 'Overdue')",
                    (m_id,),
                ).fetchone()[0]
                if active > 0:
                    self.send_json({"error": f"Cannot delete member with {active} unreturned book(s)."}, HTTPStatus.BAD_REQUEST)
                    return
                conn.execute("DELETE FROM members WHERE id = ?", (m_id,))
                conn.commit()
            self.send_json({"message": f"Member #M-{m_id} deleted."})
            return

        self.send_json({"error": "Not Found"}, HTTPStatus.NOT_FOUND)


def run_server():
    init_database()
    update_overdue_fines()
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, LibraryHTTPHandler)
    print("=" * 70)
    print("  📚 CampusShelf — Smart Campus Library System")
    print(f"  👉 Open in your browser: http://localhost:{PORT}")
    print(f"  📁 Database: {DB_PATH}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down gracefully.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
