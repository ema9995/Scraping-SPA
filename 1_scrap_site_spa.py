import requests
import csv

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
}

all_animals = []
page = 1

while True:
    url = (
        f"https://www.la-spa.fr/app/wp-json/spa/v1/animals/search/"
        f"?api=1&paged={page}&seed=683305489696047")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erreur {response.status_code} à la page {page}")
        break
    data = response.json()
    animals = data.get('results', [])
    if not animals:
        break

    # On s’assure que chaque animal a bien les champs "fad", "expr" et "sos"
    for animal in animals:
        if 'fad' not in animal:
            animal['fad'] = False
        if 'expr' not in animal and 'experienced_owner' in animal:
            animal['expr'] = animal.get('experienced_owner', False)
        elif 'expr' not in animal:
            animal['expr'] = False
        if 'sos' not in animal:
            animal['sos'] = False

    all_animals.extend(animals)
    print(f"Page {page} récupérée, {len(animals)} animaux ajoutés")
    page += 1

print(f"Total animaux récupérés : {len(all_animals)}")

# --- Détection de toutes les clés possibles ---
all_keys = set()
for animal in all_animals:
    all_keys.update(animal.keys())

# On s’assure que les colonnes clés sont bien là
for key in ["fad", "expr", "sos"]:
    all_keys.add(key)

print("Toutes les clés trouvées :", all_keys)

# --- Écriture dans un CSV ---
with open('animaux_spa_premier.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=list(all_keys))
    writer.writeheader()
    writer.writerows(all_animals)

print("CSV créé : animaux_spa_premier.csv")
