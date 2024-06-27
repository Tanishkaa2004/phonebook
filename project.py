import sqlite3
import tkinter as tk
from tkinter import messagebox

# Trie Node class
class TrieNode:
    def _init_(self):
        self.children = {}
        self.is_end_of_word = False
        self.phone = None

# Trie class
class Trie:
    def _init_(self):
        self.root = TrieNode()

    def insert(self, name, phone):
        node = self.root
        for char in name:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.phone = phone

    def search(self, name):
        node = self.root
        for char in name:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.phone if node.is_end_of_word else None

    def delete(self, name):
        def _delete(node, name, depth):
            if depth == len(name):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                return len(node.children) == 0
            char = name[depth]
            if char not in node.children:
                return False
            if _delete(node.children[char], name, depth + 1):
                del node.children[char]
                return len(node.children) == 0
            return False
        _delete(self.root, name, 0)

# Database setup
conn = sqlite3.connect('contacts.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (name TEXT PRIMARY KEY, phone TEXT)''')
conn.commit()

# Contact manager class
class ContactManager:
    def _init_(self):
        self.trie = Trie()
        self.load_contacts()

    def load_contacts(self):
        cursor.execute('SELECT name, phone FROM contacts')
        for row in cursor.fetchall():
            self.trie.insert(row[0], row[1])

    def add_contact(self, name, phone):
        cursor.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
        conn.commit()
        self.trie.insert(name, phone)

    def delete_contact(self, name):
        cursor.execute('DELETE FROM contacts WHERE name = ?', (name,))
        conn.commit()
        self.trie.delete(name)

    def search_contact(self, name):
        return self.trie.search(name)

contact_manager = ContactManager()

# GUI Implementation
class ContactApp(tk.Tk):
    def _init_(self, contact_manager):
        super()._init_()
        self.title("Contact Management App")
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")
        self.contact_manager = contact_manager

        # Main buttons
        self.add_button = tk.Button(self, text="Add Contact", command=self.show_add_contact_window, bg="#4CAF50", fg="white")
        self.delete_button = tk.Button(self, text="Delete Contact", command=self.show_delete_contact_window, bg="#f44336", fg="white")
        self.display_button = tk.Button(self, text="Display Contacts", command=self.show_display_contacts_window, bg="#008CBA", fg="white")
        self.search_button = tk.Button(self, text="Search Contact", command=self.show_search_contact_window, bg="#FFC107", fg="white")

        # Layout
        self.add_button.pack(pady=10, ipadx=10, ipady=5)
        self.delete_button.pack(pady=10, ipadx=10, ipady=5)
        self.display_button.pack(pady=10, ipadx=10, ipady=5)
        self.search_button.pack(pady=10, ipadx=10, ipady=5)

    def show_add_contact_window(self):
        AddContactWindow(self, self.contact_manager)

    def show_delete_contact_window(self):
        DeleteContactWindow(self, self.contact_manager)

    def show_display_contacts_window(self):
        DisplayContactsWindow(self, self.contact_manager)

    def show_search_contact_window(self):
        SearchContactWindow(self, self.contact_manager)

class AddContactWindow(tk.Toplevel):
    def _init_(self, parent, contact_manager):
        super()._init_(parent)
        self.title("Add Contact")
        self.geometry("300x200")
        self.configure(bg="#f0f0f0")
        self.contact_manager = contact_manager

        # Widgets
        self.name_label = tk.Label(self, text="Name:")
        self.name_entry = tk.Entry(self)
        self.phone_label = tk.Label(self, text="Phone:")
        self.phone_entry = tk.Entry(self)
        self.save_button = tk.Button(self, text="Save", command=self.save_contact, bg="#4CAF50", fg="white")

        # Layout
        self.name_label.pack(pady=5)
        self.name_entry.pack(pady=5)
        self.phone_label.pack(pady=5)
        self.phone_entry.pack(pady=5)
        self.save_button.pack(pady=10, ipadx=10, ipady=5)

    def save_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        if name and phone:
            self.contact_manager.add_contact(name, phone)
            messagebox.showinfo("Success", "Contact added successfully!")
            self.destroy()
        else:
            messagebox.showwarning("Input Error", "Both fields are required.")

class DeleteContactWindow(tk.Toplevel):
    def _init_(self, parent, contact_manager):
        super()._init_(parent)
        self.title("Delete Contact")
        self.geometry("300x400")
        self.configure(bg="#f0f0f0")
        self.contact_manager = contact_manager

        self.contacts_listbox = tk.Listbox(self)
        self.load_contacts()
        self.delete_button = tk.Button(self, text="Delete", command=self.delete_contact, bg="#f44336", fg="white")

        self.contacts_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        self.delete_button.pack(pady=10, ipadx=10, ipady=5)

    def load_contacts(self):
        self.contacts_listbox.delete(0, tk.END)
        cursor.execute('SELECT name FROM contacts')
        for row in cursor.fetchall():
            self.contacts_listbox.insert(tk.END, row[0])

    def delete_contact(self):
        selected_contact = self.contacts_listbox.get(tk.ACTIVE)
        if selected_contact:
            self.contact_manager.delete_contact(selected_contact)
            messagebox.showinfo("Success", "Contact deleted successfully!")
            self.load_contacts()
        else:
            messagebox.showwarning("Selection Error", "Please select a contact to delete.")

class DisplayContactsWindow(tk.Toplevel):
    def _init_(self, parent, contact_manager):
        super()._init_(parent)
        self.title("Display Contacts")
        self.geometry("300x400")
        self.configure(bg="#f0f0f0")
        self.contact_manager = contact_manager

        self.contacts_listbox = tk.Listbox(self)
        self.load_contacts()

        self.contacts_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    def load_contacts(self):
        self.contacts_listbox.delete(0, tk.END)
        cursor.execute('SELECT name, phone FROM contacts')
        for row in cursor.fetchall():
            self.contacts_listbox.insert(tk.END, f"Name: {row[0]}, Phone: {row[1]}")

class SearchContactWindow(tk.Toplevel):
    def _init_(self, parent, contact_manager):
        super()._init_(parent)
        self.title("Search Contact")
        self.geometry("300x200")
        self.configure(bg="#f0f0f0")
        self.contact_manager = contact_manager

        self.search_label = tk.Label(self, text="Enter Name:")
        self.search_entry = tk.Entry(self)
        self.search_button = tk.Button(self, text="Search", command=self.search_contact, bg="#FFC107", fg="white")
        self.result_label = tk.Label(self, text="")

        self.search_label.pack(pady=5)
        self.search_entry.pack(pady=5)
        self.search_button.pack(pady=10, ipadx=10, ipady=5)
        self.result_label.pack(pady=5)

    def search_contact(self):
        name = self.search_entry.get().strip()
        if name:
            phone = self.contact_manager.search_contact(name)
            if phone:
                self.result_label.config(text=f"Phone: {phone}")
            else:
                self.result_label.config(text="Contact not found.")
        else:
            messagebox.showwarning("Input Error", "Name field is required.")

if _name_ == "_main_":
    contact_manager = ContactManager()
    app = ContactApp(contact_manager)
    app.mainloop()
    conn.close()
