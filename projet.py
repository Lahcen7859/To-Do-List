import json
from datetime import datetime, timedelta
from plyer import notification

class ToDoList:
    def __init__(self, file_name="tasks.json"):
        self.tasks = []
        self.file_name = file_name
        self.load_tasks()

    def add_task(self, task, deadline=None, priority="Moyenne"):
        """Ajoute une nouvelle tâche à la liste avec une date limite et une priorité."""
        self.tasks.append({
            "task": task,
            "completed": False,
            "deadline": deadline,
            "priority": priority
        })
        self.save_tasks()
        print(f"Tâche ajoutée : {task}, Date limite : {deadline}, Priorité : {priority}")

    def view_saved_tasks(self):
        """Affiche toutes les tâches enregistrées."""
        try:
            with open(self.file_name, "r") as file:
                saved_tasks = json.load(file)
                if saved_tasks:
                    print("\nTâches enregistrées :")
                    for i, task_info in enumerate(saved_tasks, start=1):
                        status = "[X]" if task_info["completed"] else "[ ]"
                        deadline = f", Date limite : {task_info['deadline']}" if task_info['deadline'] else ""
                        priority = f", Priorité : {task_info['priority']}" if task_info['priority'] else ""
                        print(f"{i}. {status} {task_info['task']}{deadline}{priority}")
                else:
                    print("Aucune tâche enregistrée.")
        except FileNotFoundError:
            print("Fichier de tâches introuvable.")

    def view_tasks_by_status(self, completed_status):
        """Affiche les tâches filtrées par statut (terminées ou non)."""
        status_text = "terminées" if completed_status else "non terminées"
        filtered_tasks = [task for task in self.tasks if task["completed"] == completed_status]

        if filtered_tasks:
            print(f"\nTâches {status_text} :")
            for i, task_info in enumerate(filtered_tasks, start=1):
                deadline = f", Date limite : {task_info['deadline']}" if task_info['deadline'] else ""
                priority = f", Priorité : {task_info['priority']}" if task_info['priority'] else ""
                print(f"{i}. {task_info['task']}{deadline}{priority}")
        else:
            print(f"Aucune tâche {status_text} trouvée.")

    def edit_task(self, task_number):
        """Modifie une tâche existante en fonction de son numéro."""
        if 1 <= task_number <= len(self.tasks):
            task = self.tasks[task_number - 1]
            print(f"Tâche actuelle : {task['task']}, Date limite : {task['deadline']}, Priorité : {task['priority']}")

            new_task = input("Entrez le nouveau texte de la tâche ou appuyez sur Entrée pour conserver l'ancien texte : ")
            if new_task:
                task['task'] = new_task

            new_deadline = input("Entrez la nouvelle date limite (format YYYY-MM-DD) ou appuyez sur Entrée pour conserver l'ancienne : ")
            if new_deadline:
                task['deadline'] = new_deadline

            new_priority = input("Entrez la nouvelle priorité (Basse, Moyenne, Haute) ou appuyez sur Entrée pour conserver l'ancienne : ")
            if new_priority:
                task['priority'] = new_priority

            self.save_tasks()
            print(f"Tâche modifiée : {task['task']}, Date limite : {task['deadline']}, Priorité : {task['priority']}")
        else:
            print("Numéro de tâche invalide.")

    def delete_task(self, task_number):
        """Supprime une tâche en fonction de son numéro."""
        if 1 <= task_number <= len(self.tasks):
            removed_task = self.tasks.pop(task_number - 1)
            self.save_tasks()
            print(f"Tâche supprimée : {removed_task['task']}")
        else:
            print("Numéro de tâche invalide.")

    def mark_task_completed(self, task_number):
        """Marque une tâche comme terminée en fonction de son numéro."""
        if 1 <= task_number <= len(self.tasks):
            self.tasks[task_number - 1]["completed"] = True
            self.save_tasks()
            print(f"Tâche marquée comme terminée : {self.tasks[task_number - 1]['task']}")
        else:
            print("Numéro de tâche invalide.")

    def save_tasks(self):
        """Sauvegarde les tâches dans un fichier JSON."""
        with open(self.file_name, "w") as file:
            json.dump(self.tasks, file)

    def load_tasks(self):
        """Charge les tâches depuis un fichier JSON."""
        try:
            with open(self.file_name, "r") as file:
                self.tasks = json.load(file)
        except FileNotFoundError:
            self.tasks = []

    def check_reminders(self):
        """Affiche les rappels pour les tâches dont la date limite approche (dans les 24 heures)."""
        now = datetime.now()
        reminder_time = now + timedelta(hours=24)

        for task in self.tasks:
            if task["deadline"]:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
                if deadline <= reminder_time and not task["completed"]:
                    print(f"Rappel : La tâche '{task['task']}' a une date limite proche (le {task['deadline']})")
                    notification.notify(
                        title="Rappel de tâche",
                        message=f"La tâche '{task['task']}' approche de sa date limite.",
                        timeout=10  # Durée de la notification en secondes
                    )

# Menu interactif
if __name__ == "__main__":
    todo_list = ToDoList()

    while True:
        print("\n--- Gestionnaire de tâches ---")
        print("1. Ajouter une tâche")
        print("2. Afficher les tâches enregistrées")
        print("3. Afficher les tâches terminées")
        print("4. Afficher les tâches non terminées")
        print("5. Modifier une tâche")
        print("6. Supprimer une tâche")
        print("7. Marquer une tâche comme terminée")
        print("8. Vérifier les rappels")
        print("9. Quitter")

        choix = input("Choisissez une option : ")

        if choix == "1":
            nouvelle_tache = input("Entrez une nouvelle tâche : ")
            deadline = input("Entrez une date limite (format YYYY-MM-DD) ou laissez vide : ")
            deadline = deadline if deadline else None
            priority = input("Entrez la priorité (Basse, Moyenne, Haute) : ")
            priority = priority if priority else "Moyenne"
            todo_list.add_task(nouvelle_tache, deadline, priority)
        elif choix == "2":
            todo_list.view_saved_tasks()
        elif choix == "3":
            todo_list.view_tasks_by_status(completed_status=True)
        elif choix == "4":
            todo_list.view_tasks_by_status(completed_status=False)
        elif choix == "5":
            try:
                num_tache = int(input("Entrez le numéro de la tâche à modifier : "))
                todo_list.edit_task(num_tache)
            except ValueError:
                print("Veuillez entrer un numéro valide.")
        elif choix == "6":
            try:
                num_tache = int(input("Entrez le numéro de la tâche à supprimer : "))
                todo_list.delete_task(num_tache)
            except ValueError:
                print("Veuillez entrer un numéro valide.")
        elif choix == "7":
            try:
                num_tache = int(input("Entrez le numéro de la tâche à marquer comme terminée : "))
                todo_list.mark_task_completed(num_tache)
            except ValueError:
                print("Veuillez entrer un numéro valide.")
        elif choix == "8":
            todo_list.check_reminders()
        elif choix == "9":
            print("Au revoir !")
            break
        else:
            print("Option invalide. Veuillez réessayer.")
