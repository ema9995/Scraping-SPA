# SPA - Projet Animal Solidarity

## Description du projet

Ce projet a pour objectif de lutter contre l’abandon des animaux de compagnie en aidant les futurs adoptants à mieux choisir leur animal.

Nous avons commencé par analyser les principales causes d’abandon afin de comprendre les incompatibilités entre les humains et leurs animaux (manque de temps, contraintes financières, comportement, etc.).

À partir de cette analyse, nous avons développé une solution web permettant de guider les utilisateurs vers un animal adapté à leur mode de vie.

L’objectif principal est d’éviter les adoptions impulsives ou inadaptées en proposant un système de correspondance entre l’utilisateur et l’animal qui lui convient le mieux.

## Site web

Nous avons développé un site web : https://joyful-companions.lovable.app/

Il propose un questionnaire interactif permettant d’évaluer le profil de l’utilisateur (temps disponible, environnement, rythme de vie, etc.).

À la fin du questionnaire, un animal de compagnie est recommandé en fonction des réponses, afin de favoriser une adoption responsable.

## Objectifs du projet

- Comprendre les causes principales d’abandon des animaux
- Sensibiliser à l’adoption responsable
- Réduire les abandons liés à une mauvaise compatibilité
- Aider les utilisateurs à choisir un animal adapté à leur mode de vie

## Informations techniques du projet
python3 1_scrap_site_spa.py
temps de scrapping: 1m29 (pour collecter tous les données)

# Pour l'API: (la clé API doit être ajoutée au code)
python3 2_api_csv.py
==> Objectif: avoir des catégories à partir de la description

# Pour séparer les listes des catégories:
python3 3_csv_mots_clés_séparés.py
==> Objectif: séparer la liste des catégories créée à partir de l'API pour avoir que les mots clés au lieu de la liste

# Pour le CSV final:
python3 4_csv_final.py
==> Objectif: recatégoriser le résu
