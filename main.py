import tkinter as tk
from tkinter import messagebox
import sqlite3
import requests
from bs4 import BeautifulSoup
import re

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("sites.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            url TEXT,
            word TEXT,
            count INTEGER
        )
        """)
        self.conn.commit()

    def add(self, url, word, count):
        self.cursor.execute("INSERT INTO sites VALUES (?, ?, ?)", (url, word, count))
        self.conn.commit()

    def get_all(self):
        self.cursor.execute("SELECT * FROM sites ORDER BY count DESC")
        return self.cursor.fetchall()

    def clear(self):
        self.cursor.execute("DELETE FROM sites")
        self.conn.commit()


class Parser:
    def parse(self, url, word):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text().lower()

            return text.count(word.lower())

        except Exception as e:
            print("Помилка:", e)
            return 0


class App:
    def __init__(self, root):
        self.db = Database()
        self.parser = Parser()

        root.title("Аналіз сайтів")
        root.geometry("500x400")

        tk.Label(root, text="URL сайту:").pack()
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack()

        tk.Label(root, text="Слово:").pack()
        self.word_entry = tk.Entry(root, width=30)
        self.word_entry.pack()

        tk.Button(root, text="Знайти", command=self.search).pack(pady=5)
        tk.Button(root, text="Показати результати", command=self.show_results).pack(pady=5)
        tk.Button(root, text="Очистити базу", command=self.clear_db).pack(pady=5)

        self.output = tk.Text(root, height=10)
        self.output.pack()

    def search(self):
        url = self.url_entry.get()
        word = self.word_entry.get()

        if not url or not word:
            messagebox.showwarning("Помилка", "Введи URL і слово")
            return

        count = self.parser.parse(url, word)
        self.db.add(url, word, count)

        messagebox.showinfo("Результат", f"Знайдено: {count}")

    def show_results(self):
        self.output.delete(1.0, tk.END)
        results = self.db.get_all()

        for r in results:
            self.output.insert(tk.END, f"{r[0]} | {r[1]} | {r[2]}\n")

    def clear_db(self):
        self.db.clear()
        self.output.delete(1.0, tk.END)
        messagebox.showinfo("OK", "Базу очищено")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()