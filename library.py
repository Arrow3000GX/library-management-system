import tkinter as tk
from tkinter import messagebox
import sqlite3

class LibraryDB:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Available'
            );
        """)
        self.conn.commit()

    def add_book(self, title, author):
        self.conn.execute(
            "INSERT INTO books (title, author, status) VALUES (?, ?, 'Available')",
            (title, author),
        )
        self.conn.commit()

    def remove_book(self, title, author):
        cur = self.conn.execute(
            "DELETE FROM books WHERE lower(title) = lower(?) AND lower(author) = lower(?) AND status='Available'",
            (title, author),
        )
        self.conn.commit()
        return cur.rowcount > 0            
    def issue_book(self, title, author, borrower):
        cur = self.conn.execute(
            "SELECT id FROM books WHERE lower(title)=lower(?) AND lower(author)=lower(?) AND status='Available' LIMIT 1",
            (title, author),
        )
        row = cur.fetchone()
        if row:
            self.conn.execute("UPDATE books SET status=? WHERE id=?", (f"Issued to {borrower}", row[0]))
            self.conn.commit()
            return True
        return False

    def return_book(self, title, author, borrower):
        cur = self.conn.execute(
            "SELECT id FROM books WHERE lower(title)=lower(?) AND lower(author)=lower(?) AND status=? LIMIT 1",
            (title, author, f"Issued to {borrower}"),
        )
        row = cur.fetchone()
        if row:
            self.conn.execute("UPDATE books SET status='Available' WHERE id=?", (row[0],))
            self.conn.commit()
            return True
        return False

    def list_books(self):
        cur = self.conn.execute(
            "SELECT title, author, status FROM books ORDER BY title"
        )
        return cur.fetchall()

    def list_borrowed_books(self, borrower):
        cur = self.conn.execute(
            "SELECT title, author FROM books WHERE status=?",
            (f"Issued to {borrower}",),
        )
        return cur.fetchall()

    def close(self):
        self.conn.close()

# --- GUI Section ---
db = LibraryDB()

root = tk.Tk()
root.title("Library Management")

def get_inputs():
    return title_entry.get().strip(), author_entry.get().strip(), name_entry.get().strip()

def clear_inputs():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)

def update_book_list():
    book_list.delete(0, tk.END)
    for title, author, status in db.list_books():
        book_list.insert(tk.END, f"{title} by {author} ({status})")

def update_borrowed_list(name):
    borrowed_list.delete(0, tk.END)
    for title, author in db.list_borrowed_books(name):
        borrowed_list.insert(tk.END, f"{title} by {author}")

def add_book():
    title, author, _ = get_inputs()
    if title and author:
        db.add_book(title, author)
        messagebox.showinfo("Success", "Book added!")
        update_book_list()
        clear_inputs()
    else:
        messagebox.showerror("Error", "Enter both title and author.")

def remove_book():
    title, author, _ = get_inputs()
    if db.remove_book(title, author):
        messagebox.showinfo("Removed", "Book removed.")
        update_book_list()
        clear_inputs()
    else:
        messagebox.showerror("Error", "Book not found or is currently issued.")

def borrow_book():
    title, author, name = get_inputs()
    if not name:
        messagebox.showerror("Error", "Enter your name.")
        return
    if db.issue_book(title, author, name):
        messagebox.showinfo("Issued", f"{title} borrowed by {name}.")
        update_book_list()
        update_borrowed_list(name)
        clear_inputs()
    else:
        messagebox.showerror("Error", "Book is not available.")

def return_book():
    title, author, name = get_inputs()
    if not name:
        messagebox.showerror("Error", "Enter your name.")
        return
    if db.return_book(title, author, name):
        messagebox.showinfo("Returned", f"{title} returned by {name}.")
        update_book_list()
        update_borrowed_list(name)
        clear_inputs()
    else:
        messagebox.showerror("Error", "You haven't borrowed this book.")

# --- GUI Layout ---
tk.Label(root, text="Title").grid(row=0, column=0)
title_entry = tk.Entry(root)
title_entry.grid(row=0, column=1)

tk.Label(root, text="Author").grid(row=1, column=0)
author_entry = tk.Entry(root)
author_entry.grid(row=1, column=1)

tk.Label(root, text="Your Name").grid(row=2, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=2, column=1)

tk.Button(root, text="Add Book", command=add_book).grid(row=3, column=0)
tk.Button(root, text="Remove Book", command=remove_book).grid(row=3, column=1)
tk.Button(root, text="Borrow Book", command=borrow_book).grid(row=4, column=0)
tk.Button(root, text="Return Book", command=return_book).grid(row=4, column=1)

tk.Label(root, text="All Books").grid(row=5, column=0, columnspan=2)
book_list = tk.Listbox(root, width=60)
book_list.grid(row=6, column=0, columnspan=2)

tk.Label(root, text="Your Borrowed Books").grid(row=7, column=0, columnspan=2)
borrowed_list = tk.Listbox(root, width=60)
borrowed_list.grid(row=8, column=0, columnspan=2)

update_book_list()

root.mainloop()
db.close()
