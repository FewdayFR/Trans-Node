import subprocess
import os
import platform
import time
import pygame  # Importation pour la lecture audio invisible

def faire_essai():
    # Chemins absolus
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Configuration des dossiers et fichiers
    piper_exe = os.path.join(base_path, "piper", "piper.exe")
    model = os.path.join(base_path, "models", "fr_FR-siwis-medium.onnx")
    
    # Gestion du dossier temp
    temp_dir = os.path.join(base_path, "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    output_wav = os.path.join(temp_dir, "essai_annonce.wav")
    texte = "arret ! Po , Bosquet  quai  B."

    # Vérifications
    if not os.path.exists(piper_exe) or not os.path.exists(model):
        print("ERREUR : Verifie la presence de piper.exe et du modele ONNX.")
        return

    print(f"Generation de la voix (Siwis)...")

    try:
        # 1. Génération du fichier avec Piper
        command = f'"{piper_exe}" --model "{model}" --output_file "{output_wav}"'
        process = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True)
        process.communicate(input=texte.encode('utf-8'))
        process.wait()

        if os.path.exists(output_wav):
            print("Succes ! Lecture audio via Pygame...")
            
            # 2. Initialisation de Pygame Mixer
            pygame.mixer.init()
            pygame.mixer.music.load(output_wav)
            pygame.mixer.music.play()

            # 3. Attendre que la lecture soit finie avant de fermer le script
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Libérer le fichier pour pouvoir le réécrire plus tard
            pygame.mixer.quit()
            print("Annonce terminee.")
        else:
            print("Erreur : Le fichier audio n'a pas pu etre cree.")

    except Exception as e:
        print(f"Erreur systeme : {e}")

if __name__ == "__main__":
    faire_essai()