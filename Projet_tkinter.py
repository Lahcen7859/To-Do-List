import json
from datetime import datetime, timedelta
from tkinter import Tk, Frame, Label, Entry, Button, Listbox, END, messagebox, Toplevel
import threading

class ToDoList:
    def __init__(self, file_name="tasks.json"):
        self.tasks = []
        self.file_name = file_name
        self.load_tasks()

    def add_task(self, task, deadline=None, priority="Moyenne"):
        self.tasks.append({
            "task": task,
            "completed": False,
            "deadline": deadline,
            "priority": priority
        })
        self.save_tasks()

    def delete_task(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks.pop(task_index)
            self.save_tasks()

    def mark_task_completed(self, task_index):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["completed"] = True
            self.save_tasks()

    def modify_task(self, task_index, new_task, new_deadline=None, new_priority="Moyenne"):
        if 0 <= task_index < len(self.tasks):
            self.tasks[task_index]["task"] = new_task
            self.tasks[task_index]["deadline"] = new_deadline
            self.tasks[task_index]["priority"] = new_priority
            self.save_tasks()

    def save_tasks(self):
        with open(self.file_name, "w") as file:
            json.dump(self.tasks, file)

    def load_tasks(self):
        try:
            with open(self.file_name, "r") as file:
                self.tasks = json.load(file)
        except FileNotFoundError:
            self.tasks = []

class ModifyTaskWindow:
    def __init__(self, app, todo_list, task_index):
        self.app = app  # Référence à l'application principale
        self.todo_list = todo_list
        self.task_index = task_index
        self.task_data = self.todo_list.tasks[task_index]

        self.window = Toplevel(app.root)  # On crée une fenêtre secondaire
        self.window.title("Modifier la tâche")

        Label(self.window, text="Tâche :").grid(row=0, column=0, padx=5, pady=5)
        self.task_entry = Entry(self.window, width=40)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)
        self.task_entry.insert(0, self.task_data["task"])

        Label(self.window, text="Date limite (YYYY-MM-DD) :").grid(row=1, column=0, padx=5, pady=5)
        self.deadline_entry = Entry(self.window, width=20)
        self.deadline_entry.grid(row=1, column=1, padx=5, pady=5)
        if self.task_data["deadline"]:
            self.deadline_entry.insert(0, self.task_data["deadline"])

        Label(self.window, text="Priorité :").grid(row=2, column=0, padx=5, pady=5)
        self.priority_entry = Entry(self.window, width=20)
        self.priority_entry.grid(row=2, column=1, padx=5, pady=5)
        self.priority_entry.insert(0, self.task_data["priority"])

        Button(self.window, text="Modifier", command=self.modify_task).grid(row=3, column=1, pady=10, sticky="e")

    def modify_task(self):
        new_task = self.task_entry.get()
        new_deadline = self.deadline_entry.get()
        new_priority = self.priority_entry.get()

        if new_deadline:
            try:
                datetime.strptime(new_deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erreur", "La date doit être au format YYYY-MM-DD.")
                return

        self.todo_list.modify_task(self.task_index, new_task, new_deadline, new_priority)
        self.app.load_tasks_into_listbox()  # Utilise l'application principale
        self.window.destroy()

class ToDoApp:
    def __init__(self, root):
        self.todo_list = ToDoList()
        self.root = root
        self.root.title("Gestionnaire de tâches")

        # Frame pour ajouter des tâches
        self.add_frame = Frame(root)
        self.add_frame.pack(pady=10)

        Label(self.add_frame, text="Tâche :").grid(row=0, column=0, padx=5)
        self.task_entry = Entry(self.add_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5)

        Label(self.add_frame, text="Date limite (YYYY-MM-DD) :").grid(row=1, column=0, padx=5)
        self.deadline_entry = Entry(self.add_frame, width=20)
        self.deadline_entry.grid(row=1, column=1, padx=5, sticky="w")

        Label(self.add_frame, text="Priorité :").grid(row=2, column=0, padx=5)
        self.priority_entry = Entry(self.add_frame, width=20)
        self.priority_entry.grid(row=2, column=1, padx=5, sticky="w")

        Button(self.add_frame, text="Ajouter", command=self.add_task).grid(row=3, column=1, pady=10, sticky="e")

        # Liste des tâches
        self.list_frame = Frame(root)
        self.list_frame.pack(pady=10)

        Label(self.list_frame, text="Tâches :").pack()
        self.task_listbox = Listbox(self.list_frame, width=70, height=15)
        self.task_listbox.pack(pady=5)

        Button(self.list_frame, text="Marquer comme terminée", command=self.mark_task_completed).pack(side="left", padx=5)
        Button(self.list_frame, text="Modifier", command=self.modify_task).pack(side="left", padx=5)
        Button(self.list_frame, text="Supprimer", command=self.delete_task).pack(side="left", padx=5)

        self.load_tasks_into_listbox()
        self.start_notification_thread()

    def add_task(self):
        task = self.task_entry.get()
        deadline = self.deadline_entry.get()
        priority = self.priority_entry.get() if self.priority_entry.get() else "Moyenne"

        if task:
            try:
                if deadline:
                    datetime.strptime(deadline, "%Y-%m-%d")
                self.todo_list.add_task(task, deadline, priority)
                self.load_tasks_into_listbox()
                self.task_entry.delete(0, END)
                self.deadline_entry.delete(0, END)
                self.priority_entry.delete(0, END)
            except ValueError:
                messagebox.showerror("Erreur", "La date doit être au format YYYY-MM-DD.")
        else:
            messagebox.showwarning("Attention", "La tâche ne peut pas être vide !")

    def load_tasks_into_listbox(self):
        self.task_listbox.delete(0, END)
        for task in self.todo_list.tasks:
            status = "[X]" if task["completed"] else "[ ]"
            deadline = f" (Date limite : {task['deadline']})" if task['deadline'] else ""
            priority = f" [Priorité : {task['priority']}]"
            self.task_listbox.insert(END, f"{status} {task['task']}{deadline}{priority}")

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            self.todo_list.delete_task(selected_index[0])
            self.load_tasks_into_listbox()
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à supprimer.")

    def mark_task_completed(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            self.todo_list.mark_task_completed(selected_index[0])
            self.load_tasks_into_listbox()
        else:
            messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à marquer comme terminée.")

    def modify_task(self):
         selected_index = self.task_listbox.curselection()
         if selected_index:
             task_index=selected_index[0]
             ModifyTaskWindow(self, self.todo_list, task_index)
         else:
              messagebox.showwarning("Attention", "Veuillez sélectionner une tâche à modifier.")



    def check_deadlines(self):
        now = datetime.now()
        for task in self.todo_list.tasks:
            if task["deadline"] and not task["completed"]:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
                if 0 <= (deadline - now).days <= 1:
                    messagebox.showinfo("Rappel", f"La tâche '{task['task']}' est proche de sa date limite !")

    def start_notification_thread(self):
        def run():
            while True:
                self.check_deadlines()
                threading.Event().wait(60)

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = Tk()
    app = ToDoApp(root)
    root.mainloop()
