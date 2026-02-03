# 🚌 TranNode - Système d'Information Voyageur Open source 

![Logo TranNode](https://raw.githubusercontent.com/FewdayFR/Trans-Node/refs/heads/main/assets/1000001254.png)

> [!CAUTION]
> ### ⚠️ PROJET EN COURS DE DÉVELOPPEMENT (Work In Progress)
> Ce projet est actuellement en phase alpha. Les fonctionnalités décrites ci-dessous peuvent être incomplètes ou sujettes à des changements majeurs. L'utilisation en production n'est pas recommandée pour le moment.

**TranNode** est une solution open source de Système d'Information Voyageur (SIV) conçue pour le Raspberry Pi. Inspiré par les systèmes professionnels, il permet de gérer l'affichage des arrêts et les annonces vocales en temps réel dans les bus.

## ✨ Fonctionnalités
* 🖥️ **Affichage HDMI** : Interface moderne affichant le prochain arrêt, la destination et la progression sur la ligne.
* 🗣️ **Annonces Vocales (TTS)** : Intégration de **Piper TTS** pour une synthèse vocale fluide, naturelle.
* 📂 **Pilotage par XML** : Gestion simplifiée de la topologie du réseau (lignes, arrêts, correspondances) et des messages d'alerte.
* ⚡ **Performance C++** : Développé en C++ avec **Qt 6** pour une fluidité maximale sur matériel embarqué.

## 🛠️ Stack Technique
* **Langage** : C++
* **Framework** : Qt 6 
* **Audio** : Piper (modèles ONNX)
* **Données** : Parsing XML 
* **Matériel** : Raspberry pi avec écran
## 📂 Structure du projet
* `/src` : Code source C++ et fichiers d'en-tête.
* `/data` : Fichiers XML de configuration des lignes et arrêts.
* `/assets` : Logos des lignes et jingles sonores.

## 🚀 Installation
> [!IMPORTANT]
> Les scripts d'installation automatique et les binaires ne sont pas encore disponibles.

 > [!CAUTION]
>📜 Licence
Ce projet est sous licence CC BY-NC 4.0 (Creative Commons Attribution - Pas d’Utilisation Commerciale).
>⚠️ L'utilisation de ce logiciel à des fins commerciales est strictement interdite sans autorisation préalable de l'auteur.

Made with passion and heart ❤️ by Fewday
