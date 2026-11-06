"""
Library Management System - Desktop Pro Edition
===============================================
A complete desktop application built with Python 3, Tkinter (ttk), and SQLite3.
Only standard-library Python modules are used.

Features:
- Access and manage the 500-book curated library inventory.
- Track Title, Author, Genre, Shelf Location, ISBN, and Status.
- Two-part status filtering (Available vs Issued copies).
- "Give Book" dialog asking whom to give the book to.
- "Receive Book" confirmation dialog displaying borrower details and return verification.
- Add, update, delete physical copies with validation.
- Fast search across Title, Author, Genre, and ISBN.
- Automatic database sync with the web version (library.db).
"""

from datetime import datetime, timedelta
import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "library.db")


def init_database():
    """Initializes the database and ensures 500 books are seeded."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
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
    cursor.execute(
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
    cursor.execute(
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
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    conn.close()

    if count < 500:
        seed_script = os.path.join(BASE_DIR, "seed_500_books.py")
        if os.path.exists(seed_script):
            import seed_500_books
            seed_500_books.seed_database()

    return sqlite3.connect(DB_PATH)


class LibraryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CampusShelf — Desktop Library Management")
        self.root.geometry("1020x700")
        self.root.minsize(880, 600)

        try:
            self.conn = init_database()
            self.cursor = self.conn.cursor()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database:\n{e}")
            self.root.destroy()
            return

        self.selected_book_id = None
        self._setup_style()
        self._create_widgets()
        self.refresh_table()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_style(self):
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.style.configure("Treeview", rowheight=24, font=("Helvetica", 9))
        self.style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        self.style.configure("SubHeader.TLabel", font=("Helvetica", 9), foreground="#555555")

    def _create_widgets(self):
        main_container = ttk.Frame(self.root, padding=12)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Frame(main_container)
        header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(header, text="📚 CampusShelf Library Management", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="Browse 500 popular books, manage physical copies, loans, and inventory.", style="SubHeader.TLabel").pack(anchor="w")

        # Form Section
        form_frame = ttk.LabelFrame(main_container, text="Book Details", padding=8)
        form_frame.pack(fill=tk.X, pady=(0, 6))

        # Row 0: Title & Author
        ttk.Label(form_frame, text="Book Title *:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_title = ttk.Entry(form_frame, width=35)
        self.entry_title.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Author *:").grid(row=0, column=2, sticky="w", padx=(15, 5), pady=2)
        self.entry_author = ttk.Entry(form_frame, width=30)
        self.entry_author.grid(row=0, column=3, sticky="w", padx=5, pady=2)

        # Row 1: Genre & Shelf
        ttk.Label(form_frame, text="Genre:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.combo_genre = ttk.Combobox(
            form_frame,
            values=["Classics", "Sci-Fi & Fantasy", "Mystery & Thriller", "Computer Science", "Non-Fiction", "Philosophy", "General"],
            width=33,
            state="readonly",
        )
        self.combo_genre.current(0)
        self.combo_genre.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        ttk.Label(form_frame, text="Shelf Location:").grid(row=1, column=2, sticky="w", padx=(15, 5), pady=2)
        self.entry_shelf = ttk.Entry(form_frame, width=30)
        self.entry_shelf.insert(0, "Shelf A-01")
        self.entry_shelf.grid(row=1, column=3, sticky="w", padx=5, pady=2)

        # Row 2: ISBN & Selection status
        ttk.Label(form_frame, text="ISBN:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_isbn = ttk.Entry(form_frame, width=35)
        self.entry_isbn.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        self.lbl_selected_info = ttk.Label(
            form_frame,
            text="No book selected (click a row below to give/receive)",
            foreground="#666666",
            font=("Helvetica", 9, "italic"),
        )
        self.lbl_selected_info.grid(row=2, column=2, columnspan=2, sticky="w", padx=(15, 5), pady=2)

        # Search Bar with 2 Parts: Available vs Issued
        search_frame = ttk.LabelFrame(main_container, text="Search & Filter (Available vs Issued)", padding=6)
        search_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(search_frame, text="Inventory Part:").pack(side=tk.LEFT, padx=(0, 4))
        self.filter_part = ttk.Combobox(
            search_frame,
            values=["All Copies", "🟢 Available Copies", "🔴 Issued Copies"],
            state="readonly",
            width=18,
        )
        self.filter_part.current(0)
        self.filter_part.pack(side=tk.LEFT, padx=(0, 10))
        self.filter_part.bind("<<ComboboxSelected>>", lambda e: self.search_books())

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_search = ttk.Entry(search_frame, width=22)
        self.entry_search.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_search.bind("<Return>", lambda e: self.search_books())

        ttk.Label(search_frame, text="Genre:").pack(side=tk.LEFT, padx=(0, 4))
        self.filter_genre = ttk.Combobox(
            search_frame,
            values=["All Genres", "Classics", "Sci-Fi & Fantasy", "Mystery & Thriller", "Computer Science", "Non-Fiction", "Philosophy"],
            state="readonly",
            width=14,
        )
        self.filter_genre.current(0)
        self.filter_genre.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(search_frame, text="🔍 Search", command=self.search_books).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(search_frame, text="↺ Show All (500)", command=self.show_all_books).pack(side=tk.LEFT)

        # Actions
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(action_frame, text="➕ Add Book", command=self.add_book).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="✏️ Update Selected", command=self.update_book).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="🗑️ Delete Selected", command=self.delete_book).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(action_frame, text="📤 Give Book (Issue)", command=self.issue_book).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📥 Receive Book (Return)", command=self.return_book).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(action_frame, text="Clear Form", command=self.clear_form).pack(side=tk.RIGHT)

        # Table Section (Independent Scroll Area)
        table_frame = ttk.LabelFrame(main_container, text="Books Catalog (Only this section scrolls)", padding=4)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "author", "genre", "shelf", "isbn", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("genre", text="Genre")
        self.tree.heading("shelf", text="Shelf")
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("title", width=260, anchor="w")
        self.tree.column("author", width=180, anchor="w")
        self.tree.column("genre", width=120, anchor="w")
        self.tree.column("shelf", width=90, anchor="center")
        self.tree.column("isbn", width=120, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.tag_configure("status_available", foreground="#166534")
        self.tree.tag_configure("status_issued", foreground="#dc2626")

        # Status Bar
        self.status_bar = ttk.Label(main_container, text="Ready", relief=tk.SUNKEN, padding=(6, 3))
        self.status_bar.pack(fill=tk.X, pady=(4, 0))

    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        item = selected[0]
        vals = self.tree.item(item, "values")
        if not vals:
            return

        book_id, title, author, genre, shelf, isbn, status = vals
        self.selected_book_id = int(book_id)

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, title)
        self.entry_author.delete(0, tk.END)
        self.entry_author.insert(0, author)
        self.combo_genre.set(genre)
        self.entry_shelf.delete(0, tk.END)
        self.entry_shelf.insert(0, shelf)
        self.entry_isbn.delete(0, tk.END)
        self.entry_isbn.insert(0, isbn if isbn != "—" else "")

        self.lbl_selected_info.config(
            text=f"Selected Copy ID: {book_id} | Status: {status}",
            foreground="#166534" if status == "Available" else "#dc2626",
        )

    def clear_form(self):
        self.entry_title.delete(0, tk.END)
        self.entry_author.delete(0, tk.END)
        self.entry_shelf.delete(0, tk.END)
        self.entry_shelf.insert(0, "Shelf A-01")
        self.entry_isbn.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        self.selected_book_id = None
        self.lbl_selected_info.config(
            text="No book selected (click a row below to give/receive)",
            foreground="#666666",
        )
        self.entry_title.focus_set()

    def refresh_table(self, rows=None):
        try:
            if rows is None:
                self.cursor.execute(
                    "SELECT id, title, author, genre, shelf_location, isbn, status FROM books ORDER BY id ASC"
                )
                rows = self.cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            total = len(rows)
            avail = 0
            issued = 0

            for r in rows:
                b_id, title, author, genre, shelf, isbn, status = r
                tag = "status_available" if status == "Available" else "status_issued"
                self.tree.insert(
                    "",
                    tk.END,
                    values=(b_id, title, author, genre or "General", shelf or "A-01", isbn or "—", status),
                    tags=(tag,),
                )
                if status == "Available":
                    avail += 1
                elif status == "Issued":
                    issued += 1

            self.status_bar.config(
                text=f"Total: {total} copies  |  🟢 Available: {avail}  |  🔴 Issued: {issued}"
            )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load records:\n{e}")

    def add_book(self):
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.combo_genre.get()
        shelf = self.entry_shelf.get().strip() or "Shelf A-01"
        isbn = self.entry_isbn.get().strip()

        if not title or not author:
            messagebox.showwarning("Validation Error", "Title and Author are required.")
            return

        try:
            cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn else ""
            self.cursor.execute(
                """
                INSERT INTO books (title, author, genre, shelf_location, isbn, cover_url, status)
                VALUES (?, ?, ?, ?, ?, ?, 'Available')
                """,
                (title, author, genre, shelf, isbn, cover),
            )
            self.conn.commit()
            new_id = self.cursor.lastrowid
            self.clear_form()
            self.refresh_table()
            messagebox.showinfo("Success", f"Book '{title}' added as Copy ID #{new_id}.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add book:\n{e}")

    def update_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("No Selection", "Please select a book from the table to update.")
            return

        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        genre = self.combo_genre.get()
        shelf = self.entry_shelf.get().strip() or "Shelf A-01"
        isbn = self.entry_isbn.get().strip()

        if not title or not author:
            messagebox.showwarning("Validation Error", "Title and Author cannot be empty.")
            return

        try:
            cover = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn else ""
            self.cursor.execute(
                """
                UPDATE books
                SET title = ?, author = ?, genre = ?, shelf_location = ?, isbn = ?, cover_url = ?
                WHERE id = ?
                """,
                (title, author, genre, shelf, isbn, cover, self.selected_book_id),
            )
            self.conn.commit()
            self.refresh_table()
            messagebox.showinfo("Success", f"Copy #{self.selected_book_id} updated successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to update book:\n{e}")

    def delete_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("No Selection", "Please select a book to delete.")
            return

        try:
            self.cursor.execute("SELECT title, status FROM books WHERE id = ?", (self.selected_book_id,))
            row = self.cursor.fetchone()
            if not row:
                return
            title, status = row
            if status == "Issued":
                messagebox.showerror("Denied", f"Cannot delete '{title}' because it is currently ISSUED.")
                return

            if not messagebox.askyesno("Confirm", f"Delete Copy #{self.selected_book_id} ('{title}')?"):
                return

            self.cursor.execute("DELETE FROM loans WHERE book_id = ?", (self.selected_book_id,))
            self.cursor.execute("DELETE FROM books WHERE id = ?", (self.selected_book_id,))
            self.conn.commit()
            self.clear_form()
            self.refresh_table()
            messagebox.showinfo("Deleted", f"Copy #{self.selected_book_id} deleted successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete book:\n{e}")

    # ------------------------------------------------------------------
    # GIVE BOOK (Short box prompting whom to give it to)
    # ------------------------------------------------------------------
    def issue_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("No Selection", "Please select an available book from the table to give/issue.")
            return

        try:
            self.cursor.execute("SELECT title, status FROM books WHERE id = ?", (self.selected_book_id,))
            row = self.cursor.fetchone()
            if not row:
                return
            title, status = row
            if status == "Issued":
                messagebox.showwarning("Already Issued", f"'{title}' is already issued to a borrower.")
                return

            # Short box asking whom to give the book to
            borrower_name = simpledialog.askstring(
                "Give Book - Whom to give to?",
                f"Giving Copy #{self.selected_book_id}: '{title}'\n\nEnter Borrower Full Name:",
                parent=self.root,
            )
            if not borrower_name or not borrower_name.strip():
                return
            borrower_name = borrower_name.strip()

            # Find or create member
            email = f"{borrower_name.lower().replace(' ', '')}@library.local"
            try:
                self.cursor.execute("INSERT INTO members (name, email, member_type, max_books) VALUES (?, ?, 'Student', 3)", (borrower_name, email))
                member_id = self.cursor.lastrowid
            except sqlite3.IntegrityError:
                self.cursor.execute("SELECT id FROM members WHERE name = ? OR email = ?", (borrower_name, email))
                member_id = self.cursor.fetchone()[0]

            issue_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

            self.cursor.execute(
                "INSERT INTO loans (book_id, member_id, issue_date, due_date, fine_amount, status) VALUES (?, ?, ?, ?, 0.0, 'Active')",
                (self.selected_book_id, member_id, issue_date, due_date),
            )
            self.cursor.execute("UPDATE books SET status = 'Issued' WHERE id = ?", (self.selected_book_id,))
            self.conn.commit()

            self.refresh_table()
            messagebox.showinfo(
                "Book Given",
                f"✓ Book '{title}' has been successfully given to {borrower_name}!\n\nDue Date (14 Days): {due_date}",
            )
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to issue book:\n{e}")

    # ------------------------------------------------------------------
    # RECEIVE BOOK (Confirming details of book & who is returning it)
    # ------------------------------------------------------------------
    def return_book(self):
        if not self.selected_book_id:
            messagebox.showwarning("No Selection", "Please select an issued book from the table to receive back.")
            return

        try:
            self.cursor.execute("SELECT title, status, shelf_location FROM books WHERE id = ?", (self.selected_book_id,))
            row = self.cursor.fetchone()
            if not row:
                return
            title, status, shelf = row
            if status == "Available":
                messagebox.showwarning("Already Available", f"'{title}' is already marked as available in the library.")
                return

            # Query active loan and borrower
            self.cursor.execute(
                """
                SELECT l.id, l.issue_date, l.due_date, l.fine_amount, m.name, m.phone, m.email
                FROM loans l
                JOIN members m ON l.member_id = m.id
                WHERE l.book_id = ? AND l.status IN ('Active', 'Overdue')
                """,
                (self.selected_book_id,),
            )
            loan_row = self.cursor.fetchone()

            borrower_name = loan_row[4] if loan_row else "Patron"
            issue_date = loan_row[1] if loan_row else "—"
            due_date = loan_row[2] if loan_row else "—"
            fine = loan_row[3] if loan_row else 0.0

            confirm_msg = (
                f"📥 Confirm Book Return\n"
                f"-----------------------------------------\n"
                f"Book: '{title}' (Copy #{self.selected_book_id})\n"
                f"Returning to: {shelf}\n\n"
                f"Who is returning it: {borrower_name}\n"
                f"Issued on: {issue_date} | Due on: {due_date}\n"
            )
            if fine > 0:
                confirm_msg += f"\n⚠️ OVERDUE FINE DUE: ${fine:.2f}\n"

            confirm_msg += "\nConfirm and receive this book back into the library?"

            if not messagebox.askyesno("Confirm Return", confirm_msg):
                return

            today_str = datetime.now().strftime("%Y-%m-%d")
            self.cursor.execute("UPDATE books SET status = 'Available' WHERE id = ?", (self.selected_book_id,))
            self.cursor.execute(
                "UPDATE loans SET status = 'Returned', return_date = ? WHERE book_id = ? AND status IN ('Active', 'Overdue')",
                (today_str, self.selected_book_id),
            )
            self.conn.commit()

            self.refresh_table()
            messagebox.showinfo("Book Received", f"✓ Book '{title}' received back from {borrower_name} and marked Available!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to return book:\n{e}")

    def search_books(self):
        q = self.entry_search.get().strip()
        genre = self.filter_genre.get()
        part = self.filter_part.get()

        clauses = []
        params = []

        if part == "🟢 Available Copies":
            clauses.append("status = 'Available'")
        elif part == "🔴 Issued Copies":
            clauses.append("status = 'Issued'")

        if q:
            clauses.append("(title LIKE ? OR author LIKE ? OR isbn LIKE ?)")
            like_term = f"%{q}%"
            params.extend([like_term, like_term, like_term])
        if genre != "All Genres":
            clauses.append("genre = ?")
            params.append(genre)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        sql = f"SELECT id, title, author, genre, shelf_location, isbn, status FROM books {where} ORDER BY id ASC"

        try:
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()
            self.refresh_table(rows=rows)
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Search error:\n{e}")

    def show_all_books(self):
        self.entry_search.delete(0, tk.END)
        self.filter_genre.current(0)
        self.filter_part.current(0)
        self.refresh_table()

    def on_closing(self):
        try:
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
