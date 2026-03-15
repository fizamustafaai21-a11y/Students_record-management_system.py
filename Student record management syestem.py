import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

FIELDS = ["RollNo", "FullName", "Age", "Email", "Phone"]
DATABASE_FILE = "students.csv"


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Student Management System")
        self.root.geometry("800x550")
        self.root.resizable(False, False)

        self.sort_reverse = False
        self.current_sort_column = None

        # ======= Title =======
        title_label = tk.Label(
            root,
            text="🎓 Student Management System",
            font=("Arial", 20, "bold"),
            bg="#0078D7",
            fg="white",
            pady=10,
        )
        title_label.pack(fill=tk.X)

        # ======= Button Frame =======
        btn_frame = tk.Frame(root, pady=10)
        btn_frame.pack()

        buttons = [
            ("Register New Student", self.register_student),
            ("Modify Student", self.modify_student),
            ("Remove Student", self.remove_student),
            ("Exit", root.quit),
        ]

        for text, command in buttons:
            tk.Button(
                btn_frame,
                text=text,
                width=22,
                height=2,
                bg="#E5E5E5",
                command=command,
            ).pack(side=tk.LEFT, padx=5)

        # ======= Search Bar =======
        search_frame = tk.Frame(root, pady=5)
        search_frame.pack()

        tk.Label(search_frame, text="🔍 Search:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="Search", command=self.filter_students, bg="#0078D7", fg="white").pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(search_frame, text="Reset", command=self.load_students, bg="#444", fg="white").pack(side=tk.LEFT)

        # ======= Table (Treeview) =======
        self.tree = ttk.Treeview(root, columns=FIELDS, show="headings", height=15)
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#0078D7", foreground="black")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)

        for col in FIELDS:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=130, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(x=775, y=150, height=340)

        # ======= Status Bar =======
        self.status_label = tk.Label(root, text="", font=("Arial", 10), bg="#F0F0F0")
        self.status_label.pack(fill=tk.X)

        self.load_students()

    # ======= Data Loading =======
    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            with open(DATABASE_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                students = list(reader)
                for student in students:
                    self.tree.insert("", tk.END, values=[student[f] for f in FIELDS])
                self.status_label.config(text=f"📋 Total Students: {len(students)}")
        except FileNotFoundError:
            self.status_label.config(text="⚠️ No data file found.")

    # ======= Register =======
    def register_student(self):
        win = tk.Toplevel(self.root)
        win.title("Register New Student")
        win.geometry("400x350")

        entries = {}
        for i, field in enumerate(FIELDS):
            tk.Label(win, text=field, font=("Arial", 11)).grid(row=i, column=0, pady=5, padx=10, sticky="w")
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1, pady=5)
            entries[field] = entry

        def save_student():
            student_info = {f: e.get().strip() for f, e in entries.items()}
            if any(v == "" for v in student_info.values()):
                messagebox.showerror("Error", "Please fill all fields!")
                return

            with open(DATABASE_FILE, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow(student_info)

            messagebox.showinfo("Success", "Student registered successfully!")
            win.destroy()
            self.load_students()

        tk.Button(win, text="Save", bg="#0078D7", fg="white", command=save_student).grid(
            row=len(FIELDS), column=0, columnspan=2, pady=15
        )

    # ======= Modify =======
    def modify_student(self):
        roll = simpledialog.askstring("Modify Student", "Enter Roll Number to Update:")
        if not roll:
            return

        students = []
        found_student = None
        try:
            with open(DATABASE_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for s in reader:
                    if s["RollNo"] == roll:
                        found_student = s
                    students.append(s)
        except FileNotFoundError:
            messagebox.showerror("Error", "No data found!")
            return

        if not found_student:
            messagebox.showerror("Error", "Student not found!")
            return

        win = tk.Toplevel(self.root)
        win.title("Modify Student")
        win.geometry("400x350")

        entries = {}
        for i, field in enumerate(FIELDS):
            tk.Label(win, text=field, font=("Arial", 11)).grid(row=i, column=0, pady=5, padx=10, sticky="w")
            entry = tk.Entry(win, width=30)
            entry.insert(0, found_student[field])
            entry.grid(row=i, column=1, pady=5)
            entries[field] = entry

        def save_changes():
            for s in students:
                if s["RollNo"] == roll:
                    for f in FIELDS:
                        s[f] = entries[f].get().strip()

            with open(DATABASE_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(students)

            messagebox.showinfo("Success", "Student updated successfully!")
            win.destroy()
            self.load_students()

        tk.Button(win, text="Save Changes", bg="#0078D7", fg="white", command=save_changes).grid(
            row=len(FIELDS), column=0, columnspan=2, pady=15
        )

    # ======= Remove =======
    def remove_student(self):
        roll = simpledialog.askstring("Remove Student", "Enter Roll Number to Delete:")
        if not roll:
            return
        students = []
        deleted = False
        try:
            with open(DATABASE_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for s in reader:
                    if s["RollNo"] != roll:
                        students.append(s)
                    else:
                        deleted = True
            if deleted:
                with open(DATABASE_FILE, "w", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=FIELDS)
                    writer.writeheader()
                    writer.writerows(students)
                messagebox.showinfo("Deleted", f"Student {roll} deleted successfully.")
                self.load_students()
            else:
                messagebox.showwarning("Not Found", "Student not found!")
        except FileNotFoundError:
            messagebox.showerror("Error", "No data file found!")

    # ======= Filter/Search =======
    def filter_students(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.load_students()
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            with open(DATABASE_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                students = [
                    s
                    for s in reader
                    if keyword in s["RollNo"].lower() or keyword in s["FullName"].lower()
                ]
                for s in students:
                    self.tree.insert("", tk.END, values=[s[f] for f in FIELDS])
                self.status_label.config(text=f"🔍 Showing {len(students)} results for '{keyword}'")
        except FileNotFoundError:
            messagebox.showerror("Error", "No data file found!")

    # ======= Sort Table =======
    def sort_by_column(self, col):
        data = [self.tree.item(item)["values"] for item in self.tree.get_children()]
        if not data:
            return
        idx = FIELDS.index(col)
        data.sort(key=lambda x: x[idx], reverse=self.sort_reverse)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in data:
            self.tree.insert("", tk.END, values=item)
        self.sort_reverse = not self.sort_reverse


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()