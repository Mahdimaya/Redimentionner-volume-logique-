import subprocess
import re
import tkinter as tk
from tkinter import ttk

def get_volume_groups():
    try:
        # Obtient la liste des groupes de volumes
        cmd = "vgdisplay --noheading -C -o lv_name"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)

        # Divise la sortie en lignes et supprime les espaces blancs
        volume_groups = [vg.strip() for vg in output.splitlines()]
        return volume_groups
    except subprocess.CalledProcessError as e:
        print(f"Erreur : {e}")
        return []

def get_logical_volumes(volume_group):
    try:
        # Obtient la liste des volumes logiques pour un groupe de volumes donné
        cmd = f"lvdisplay --noheading -C -o lv_name /dev/VG/{volume_group}"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)

        # Divise la sortie en lignes et supprime les espaces blancs
        logical_volumes = [lv.strip() for lv in output.splitlines()]
        return logical_volumes
    except subprocess.CalledProcessError as e:
        print(f"Erreur : {e}")
        return []

def get_logical_volume_size(logical_volume):
    try:
        # Obtient la taille actuelle du volume logique
        cmd = f"lvdisplay --noheading -C -o lv_size /dev/VG/{logical_volume}"
        output = subprocess.check_output(cmd, shell=True, universal_newlines=True)

        # Utilisation d'une expression régulière pour extraire uniquement les parties numériques
        size_match = re.search(r'([\d.,]+)', output)
        if size_match:
            size_str = size_match.group(1)
            # Remplace la virgule par un point et convertit en float
            return float(size_str.replace(",", "."))

        raise ValueError("La taille du volume logique ne peut pas être extraite.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur : {e}")
        return 0.0

def resize_volume(logical_volume, threshold):
    try:
        # Obtient la taille actuelle du volume logique
        current_size = get_logical_volume_size(logical_volume)

        # Compare la taille actuelle avec le seuil
        if current_size > threshold:
            # Redimensionne le volume logique
            cmd_resize = f"lvresize -L +{threshold}G /dev/VG/{logical_volume}"
            subprocess.run(cmd_resize, shell=True, check=True)
            print(f"Volume logique '{logical_volume}' redimensionné avec un seuil de {threshold} Go.")
        else:
            print(f"La taille actuelle du volume logique '{logical_volume}' est inférieure ou égale au seuil.")

    except ValueError as e:
        print(f"Erreur : {e}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution de la commande : {e}")

def on_resize_button_click():
    selected_vg = volume_group_combobox.get()
    selected_lv = logical_volume_combobox.get()
    threshold = float(threshold_entry.get())

    resize_volume(selected_lv, threshold)

# Création de l'interface utilisateur
root = tk.Tk()
root.title("Redimensionner le volume logique")

# Liste des groupes de volumes
volume_groups = get_volume_groups()

# Variables pour stocker les choix de l'utilisateur
selected_volume_group = tk.StringVar()
selected_logical_volume = tk.StringVar()

# Libellé et liste déroulante pour les groupes de volumes
volume_group_label = tk.Label(root, text="Sélectionnez le groupe de volumes:")
volume_group_label.pack()

volume_group_combobox = ttk.Combobox(root, textvariable=selected_volume_group, values=volume_groups)
volume_group_combobox.pack()

# Libellé et liste déroulante pour les volumes logiques
logical_volume_label = tk.Label(root, text="Sélectionnez le volume logique:")
logical_volume_label.pack()

logical_volume_combobox = ttk.Combobox(root, textvariable=selected_logical_volume)
logical_volume_combobox.pack()

# Champ d'entrée pour le seuil de redimensionnement
threshold_label = tk.Label(root, text="Entrez le seuil de redimensionnement en gigaoctets:")
threshold_label.pack()

threshold_entry = tk.Entry(root)
threshold_entry.pack()

# Bouton de redimensionnement
resize_button = tk.Button(root, text="Redimensionner", command=on_resize_button_click)
resize_button.pack()

# Démarrage de la boucle principale de l'interface utilisateur
root.mainloop()

