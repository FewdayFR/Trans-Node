# 🚌 TranNode - Système d'Information Voyageur

![Logo TranNode](h)

**TranNode** est une solution open source de Système d'Information Voyageur (SIV) conçue pour le Raspberry Pi. Inspiré par les systèmes professionnels (type Lumiplan), il permet de gérer l'affichage des arrêts et les annonces vocales en temps réel dans les bus.

## ✨ Fonctionnalités
* 🖥️ **Affichage TFT/LCD** : Interface moderne affichant le prochain arrêt, la destination et la progression sur la ligne.
* 🗣️ **Annonces Vocales (TTS)** : Intégration de **Piper TTS** pour une synthèse vocale fluide, naturelle et 100% locale (sans connexion internet).
* 📂 **Pilotage par XML** : Gestion simplifiée de la topologie du réseau (lignes, arrêts, correspondances) et des messages d'alerte.
* ⚡ **Performance C++** : Développé en C++ avec **Qt 6** pour une fluidité maximale sur matériel embarqué.

## 🛠️ Stack Technique
* **Langage** : C++
* **Framework** : Qt 6
* **Audio** : Piper (modèles ONNX)
* **Données** : Parsing XML
* **Matériel** : Raspberry Pi via un écran.
## 📂 Structure du projet
* `/src` : Code source C++ et fichiers d'en-tête.
* `/data` : Fichiers XML de configuration des lignes et arrêts.
* `/assets` : Logos des lignes et jingles sonores.

## 🚀 Installation (Work in Progress)
Le projet est actuellement en phase de développement.
