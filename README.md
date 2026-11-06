# 📚 CampusShelf — Smart Campus Library Management System

A complete, production-grade **Library Management System** built using **100% Python standard-library modules** (`http.server`, `sqlite3`, `tkinter`, `urllib.request`). Zero external packages, zero `pip install`, and zero configuration required!

---

## 🌟 Key Features & Interface Upgrades

### 1. 🔒 Independent Catalog Scrolling
* The top navigation bar, KPI summary cards, 2-part switcher, and search/filter controls **remain permanently fixed** on screen.
* **Only the library catalog area scrolls** (with sticky column headers), so you never lose your place or have to scroll back up to search or filter!

### 2. 🟢 🔴 Two Dedicated Inventory Parts
* **🟢 Part 1: Available Books**:
  * Shows all copies currently in the library ready to be borrowed.
  * Columns: ID, Title & Author, Genre, ISBN, Shelf Location, Status.
  * Action: A prominent **"📤 Give Book"** button on each row.
* **🔴 Part 2: Issued Books**:
  * Shows all copies currently out on loan.
  * Columns: ID, Title, Currently With (Borrower), Contact, Issued Date, Due Date, Status (On schedule / Overdue).
  * Action: A prominent **"📥 Receive Book"** button on each row.
* Dynamic counter badges on the tabs update in real time (e.g. `Available: 490`, `Issued: 10`).

### 3. 📤 Short "Give Book" Box with Live Member Typing Search
* When you click **"Give Book"** on an available copy, a compact popup opens:
  * Shows the book title, author, and Copy ID badge.
  * **Typing Live Search**: Instantly filters members as you type by **Name**, **Phone Number**, **Email**, or **Unique Member ID (`#M-X`)**.
  * Displays borrower quota status (e.g. `1/3 books borrowed`).
  * Option to click **"+ Type New Borrower"** on the spot if the patron is not yet registered.
  * Choose loan duration (defaults to 14 days).
  * Click **"✓ Confirm & Give Book"** — the book immediately moves to the **Issued** part!

### 4. 📥 "Receive Book" Confirmation Box (Fixed & Verified)
* When you click **"Receive Book"** on any issued copy, the confirmation modal opens:
  * **Book Details**: Copy ID, Title, Author, and the exact **Shelf Location** to return it to (e.g. `Shelf A-04`).
  * **Who is returning it**: Borrower Unique Member ID (`#M-X`), Full Name, Phone, and Email.
  * **Overdue Status & Fine**: Live alert indicating if the book is on time or overdue by X days ($0.50/day fine).
  * Condition check: `[x] Book inspected and received in good condition`.
  * Click **"✓ Confirm & Receive Book"** — updates status to `Available` and moves it right back to Part 1!

### 5. 👆 Interactive Clickable KPI Summary Cards
Every top KPI card is now clickable with custom feedback:
* **Total Inventory**: Resets search/genre filters and highlights the entire catalog.
* **Available Copies**: Immediately jumps to **🟢 Part 1: Available Books** and pulses with an animated blue border.
* **Issued Copies**: Immediately jumps to **🔴 Part 2: Issued Books** and pulses with an animated blue border.
* **Overdue Loans**: Opens a dedicated modal listing all overdue loans with borrower contact info and a **1-click "Receive Book"** button.
* **Pending Fines**: Opens a fine breakdown modal explaining the $0.50/day policy with a list of borrowers with active overdue fines and a **"Receive & Settle Fine"** shortcut.
* **Active Holds**: Switches directly to the Waitlist tab to view book hold queues.

### 6. 🛡️ Strictly Librarian / Admin Mode
* Student login portal and role-switcher removed.
* Clean, streamlined single-portal admin workflow for library staff.

### 7. 500 Curated Popular Books Pre-Loaded
* Pre-loaded with 500 real books across Classics, Sci-Fi & Fantasy, Mystery, Tech, Non-Fiction, and Philosophy.
* Complete metadata per copy: unique Copy ID, Title, Author, Genre, Shelf Location (e.g., `Shelf B-06`), ISBN, and Cover Art thumbnail.

### 8. Book Holds & Waitlist (Reservations)
* When a book is issued, patrons or librarians can place a hold.
* Returning an issued book with a pending hold automatically fulfills the hold and notifies the patron!

### 9. ⚡ Live ISBN Auto-Fill (Open Library API)
* Click **➕ Add Book**, enter an ISBN (e.g. `9780061120084`), and click **"Lookup"**.
* Fetches Title, Author, and Cover Art in 1 second via the Open Library API.

### 10. 🌙 Dark Mode / Light Mode
* 1-click theme toggle in the header (persists preference in `localStorage`).

### 11. 📊 Analytics & Interactive SVG Charts
* Real-time Donut Chart showing Available vs Issued inventory breakdown.
* Bar Chart showing collection distribution across all genres.

---

## 🚀 How to Run

### Web Edition on Localhost (Recommended)
```bash
git clone https://github.com/mandalantara300-jpg/Library-management-system-.git
cd Library-management-system-
python3 web_app.py
```
Open in your browser:
👉 **[http://localhost:8000](http://localhost:8000)**

*(Keep the terminal running while using the web app).*

### Desktop Edition (Native Tkinter Window)
```bash
python3 main.py
```
Opens as a native desktop window with the two-part filter and give/receive dialogs connected to the same 500-book `library.db` database.

---

## 🧪 Step-by-Step Test Walkthrough

1. **Test Scrolling**:
   - In the browser, scroll through the 500 books with your mouse/trackpad.
   - Notice that **only the book catalog scrolls**! The header, stats cards, and search controls stay locked at the top.
2. **Switch Parts (Available vs Issued)**:
   - Click **"🟢 Part 1: Available Books"** to see available copies.
   - Click **"🔴 Part 2: Issued Books"** to see currently loaned books with borrower names and due dates.
3. **Give a Book**:
   - Under Available Books, click **"📤 Give Book"** on any book.
   - In the short box, choose an existing member or type a new name (e.g. `John Doe`).
   - Click **"Confirm & Give Book"**.
   - Notice the book moves from Available to Issued immediately!
4. **Receive a Book**:
   - Switch to **"🔴 Part 2: Issued Books"**.
   - Click **"📥 Receive Book"** on the copy you just issued.
   - Review the confirmation box with the borrower's details and shelf location.
   - Click **"Confirm & Receive Book"**.
   - The book moves back to Available!
