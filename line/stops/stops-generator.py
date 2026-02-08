import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os

def generate_line_xml():
    chemin_csv = r"C:\Users\UTILISATEUR\Desktop\Trans node\Trans-Node\line\stops\liste-des-distances-inter-arrets-par-ligne-par-sens.csv"
    
    if not os.path.exists(chemin_csv):
        print(f"Erreur : Fichier introuvable : {chemin_csv}")
        return

    # Lecture du CSV
    df = pd.read_csv(chemin_csv, sep=';', encoding='utf-8')
    
    # 1. Préparation des correspondances
    # On crée un dictionnaire : { 'CODE_ARRET': {ensemble des lignes} }
    dict_correspondances = df.groupby('Arrêt')['Ligne'].apply(set).to_dict()

    # 2. Demande utilisateur
    choix = input("Entrez 'T' pour tout générer, ou le nom précis de la ligne (ex: 11, T1, COXI, Emma) : ").strip()

    if choix.upper() == 'T':
        lignes_a_traiter = df['Ligne'].unique()
    else:
        if choix in df['Ligne'].astype(str).unique():
            lignes_a_traiter = [choix]
        else:
            print(f"La ligne '{choix}' n'existe pas dans le fichier.")
            return

    output_dir = "fichiers_xml"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for ligne_id in lignes_a_traiter:
        group_ligne = df[df['Ligne'].astype(str) == str(ligne_id)]
        
        root = ET.Element("lign")
        root.set("id", str(ligne_id))
        
        for sens_id, group_sens in group_ligne.groupby('Direction'):
            dest_el = ET.SubElement(root, "destination")
            
            # Destination (après le >)
            full_desc = str(group_sens['Description'].iloc[0])
            nom_destination = full_desc.split('>')[-1].strip() if '>' in full_desc else full_desc
            
            ET.SubElement(dest_el, "description").text = nom_destination
            ET.SubElement(dest_el, "sens_id").text = str(int(float(sens_id)))

            # Tri par séquence pour identifier le dernier arrêt
            group_sens = group_sens.sort_values('Séquence')
            max_sequence = group_sens['Séquence'].max()

            for _, row in group_sens.iterrows():
                seq_val = int(row['Séquence'])
                seq_el = ET.SubElement(dest_el, f"sequence_{seq_val}")
                
                code_arret = str(row['Arrêt'])
                nom_arret = str(row['Description.1'])
                
                ET.SubElement(seq_el, "code_arret").text = code_arret
                ET.SubElement(seq_el, "nom_arret").text = nom_arret
                ET.SubElement(seq_el, "tts").text = nom_arret # TTS identique au nom
                
                # Terminus : 1 si c'est la dernière séquence, sinon 0
                val_terminus = "1" if row['Séquence'] == max_sequence else "0"
                ET.SubElement(seq_el, "terminus").text = val_terminus
                
                # Correspondances (toutes les lignes sauf la ligne actuelle)
                lignes_correspondantes = dict_correspondances.get(code_arret, set())
                autres_lignes = [str(l) for l in lignes_correspondantes if str(l) != str(ligne_id)]
                ET.SubElement(seq_el, "correspondance").text = ", ".join(autres_lignes)
                
                ET.SubElement(seq_el, "desservi").text = "1"
                ET.SubElement(seq_el, "pmr").text = "0"

        # Export avec formatage
        xml_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(xml_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        file_path = os.path.join(output_dir, f"{ligne_id}.xml")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml)
        print(f"Fichier {ligne_id}.xml généré.")

if __name__ == "__main__":
    generate_line_xml()
    