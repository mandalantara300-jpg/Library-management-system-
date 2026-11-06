# 📚 CampusShelf — Smart Campus Library Management System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-CampusShelf%20Web%20App-2563eb?style=for-the-badge&logo=google-chrome&logoColor=white)](https://mandalantara300-jpg.github.io/Library-management-system-/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Active-success?style=for-the-badge&logo=github)](https://mandalantara300-jpg.github.io/Library-management-system-/)

> 🌐 **Live Website Link**: 👉 **[https://mandalantara300-jpg.github.io/Library-management-system-/](https://mandalantara300-jpg.github.io/Library-management-system-/)** 👈
>
> **Click the link above to immediately open and use CampusShelf right now in any browser, tablet, or phone — zero setup or installation required!**

---

## 🌟 What is CampusShelf?

CampusShelf is a modern, production-grade **Campus Library Management System** with 500 popular books pre-loaded, real-time barcode scanning, printable credit-card library badges, 80mm thermal borrowing receipts, hold queues, overdue fine tracking, and a self-service student kiosk.

It is available in three distinct editions:
1. 🌐 **Live Web Application (Cloud Hosted)**: Open anywhere at **[mandalantara300-jpg.github.io/Library-management-system-](https://mandalantara300-jpg.github.io/Library-management-system-/)**.
2. 💻 **Localhost Full-Stack Web Edition**: Powered by Python's built-in standard library (`web_app.py` with SQLite `library.db`).
3. 🖥️ **Desktop GUI Edition**: Native Tkinter desktop application (`main.py`).

---

## 🚀 Advanced Features & Tools

### 1. 📷 Real-Time Barcode & Card Camera Scanner
* **Camera Viewfinder**: Real-time camera feed with targeting reticle and red laser sweep line animation (`navigator.mediaDevices.getUserMedia`).
* **Handheld USB Scanner Compatible**: Supports physical USB barcode scanner guns (keyboard wedge input with auto-submit).
* **Smart Auto-Routing**:
  * Scanning a **Book Barcode** or typing an ID automatically opens the **"📤 Give Book"** dialog if available, or **"📥 Receive Book"** dialog if currently issued!
  * Scanning a **Member ID** (`#M-X`) instantly loads their profile or selects them as the borrower!

### 2. 🪪 Printable Student & Faculty Library Cards
* High-definition credit card proportions (CR80 ratio) with modern gradient backdrop and university seal.
* Displays:
  * Member Photo Avatar with initials
  * Member Name & Unique Member ID (`#M-X`)
  * Member Type pill (`STUDENT` / `FACULTY` / `STAFF`)
  * Contact info (Email & Phone)
  * Live **Code 39 SVG Barcode** for laser/optical scanning
* **1-Click Print**: Formatted with dedicated print CSS so clicking **"Print Library Card"** isolates and prints only the card at full DPI on card stock or paper. Available via the **"🪪 Card"** button on any member row.

### 3. 🧾 Printable 80mm Thermal Checkout Receipts
* Generates thermal-style borrowing receipts on loan checkout:
  * Library header & timestamp
  * Patron name & Member ID (`#M-X`)
  * Book title, author, Copy ID, and designated **Return Shelf Location** (e.g. `Shelf A-04`)
  * **Return Due Date** highlighted in bold
  * Barcode of the loan transaction
  * Fine terms ($0.50/day overdue fee reminder)
* Print-ready dialog for standard thermal POS receipt printers or standard 8.5x11 paper.

### 4. 👤 Patron / Student Self-Service Kiosk
* A dedicated patron portal tab (`👤 Patron Kiosk`) where students and staff can:
  * Look up their account with Member ID (`#M-1`) or email.
  * View currently checked out books with color-coded **due date countdown badges** (green on-schedule, red overdue with fines).
  * Check active hold queue reservations.
  * **Self-Service Waitlist Holds**: Search all currently borrowed books in the collection and click **"📌 Place Hold"** to reserve their spot in line!

### 5. 🏷️ Book Shelf & Barcode Label Generator
* In the Available Catalog, click **"🏷️"** on any book copy to generate a printable shelf & spine label with the book copy's barcode, shelf coordinate (e.g. `Shelf B-06`), ISBN, title, and author.

### 6. 🔒 Independent Catalog Scrolling & Two-Part Layout
* **Locked Navigation**: The top navbar, KPI cards, 2-part switcher, and search controls stay permanently pinned at the top.
* **Scrolls Independently**: Only the 500-book catalog list scrolls vertically, with sticky table headers so you never lose context.
* **🟢 Part 1: Available Books**: Ready for immediate borrowing with **"📤 Give Book"** and **"🏷️ Barcode Label"**.
* **🔴 Part 2: Issued Books**: Displays borrower, contact, due date, overdue badges, and **"📥 Receive Book"** + **"🧾 Receipt"**.

### 7. 👆 Interactive Clickable KPI Summary Cards
* **Total Inventory**: Resets filters and highlights the catalog with an animated glow pulse.
* **Available Copies**: Automatically jumps to Part 1 with a highlight pulse.
* **Issued Copies**: Automatically jumps to Part 2 with a highlight pulse.
* **Overdue Loans**: Opens a modal listing overdue loans with 1-click **Receive Book** action.
* **Pending Fines**: Opens a fine breakdown modal ($0.50/day policy) with settle actions.
* **Active Holds**: Switches directly to the Waitlist tab to view book hold queues.

### 8. 500 Curated Popular Books Pre-Loaded
* Pre-seeded with 500 real books across Classics, Sci-Fi & Fantasy, Mystery, Tech, Non-Fiction, and Philosophy (`seed_500_books.py`).
* Unique Copy IDs, Shelves (e.g. `Shelf B-06`), ISBNs, and Open Library Cover URLs.

### 9. ⚡ Live ISBN Auto-Fill (Open Library API)
* Click **➕ Add Book**, enter an ISBN (e.g. `9780061120084`), and click **"Lookup"** to fetch Title, Author, and Cover Art in 1 second.

### 10. 🌙 Dark Mode / Light Mode & SVG Analytics
* 1-click theme toggle (persists in `localStorage`).
* Real-time SVG Donut Chart (Available vs Issued) and Genre Distribution Bar Chart.

---

## 💻 How to Run Locally

### Web Edition on Localhost
```bash
git clone https://github.com/mandalantara300-jpg/Library-management-system-.git
cd Library-management-system-
python3 web_app.py
```
Open in your browser:
👉 **[http://localhost:8000](http://localhost:8000)**

### Desktop Edition (Native Tkinter Window)
```bash
python3 main.py
```

---

## ☁️ 1-Click Cloud Deployment (Free)

CampusShelf is cloud-ready and contains zero external dependencies:

* **Live GitHub Pages URL**: [https://mandalantara300-jpg.github.io/Library-management-system-/](https://mandalantara300-jpg.github.io/Library-management-system-/)
* **Deploy to Render**: Connect repo on [render.com](https://render.com) using the included `render.yaml`.
* **Deploy with Docker**:
  ```bash
  docker build -t campusshelf .
  docker run -p 8000:8000 campusshelf
  ```
