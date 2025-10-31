import pandas as pd
import json
import re
from tqdm import tqdm
from openai import OpenAI
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = (
    "sk....."
)
INPUT_FILE = "animaux_spa_premier.csv"
OUTPUT_FILE = "animaux_spa_key_words.csv"
SAVE_INTERVAL = 50  # Sauvegarde automatique toutes les 50 lignes

client = OpenAI(api_key=API_KEY)
tqdm.pandas()

# ============================================================
# CHARGEMENT DU FICHIER
# ============================================================

df = pd.read_csv(INPUT_FILE)
if "description" not in df.columns:
    raise ValueError("La colonne 'description' est manquante dans ton fichier CSV.")

# Reprise si un fichier de sortie existe déjà
if Path(OUTPUT_FILE).exists():
    print(f"Reprise depuis {OUTPUT_FILE}")
    df_existing = pd.read_csv(OUTPUT_FILE)
    if "behavior_keywords" in df_existing.columns:
        df = df_existing.copy()

# ============================================================
# FONCTION D’ANALYSE — VERSION MOTS-CLÉS
# ============================================================


def analyze_description(text):
    if pd.isna(text) or len(text.strip()) == 0:
        return {
            "reason_abandon": [],
            "behavior_keywords": [],
            "compatibility_keywords": [],
            "health_keywords": [],
            "adoption_keywords": []
        }

    prompt = f""" Analyse la description suivante d'un animal
    d'un refuge et génère uniquement des mots-clés concis.
    Identifie :
    - la raison de l’abandon
    - le comportement
    - les compatibilités (chiens, chats, enfants)
    - la santé
    - les besoins pour l’adoption

    Description :
    \"\"\"{text}\"\"\"

    Retourne UNIQUEMENT un JSON valide au format :
    {{
      "reason_abandon": ["mot1", "mot2"],
      "behavior_keywords": ["mot1", "mot2", "mot3"],
      "compatibility_keywords": ["chiens_ok", "chats_non", "enfants_oui"],
      "health_keywords": ["stérilisé", "vacciné", "malade"],
      "adoption_keywords": ["calme", "affectueux", "maison_jardin"]
    }}
    """

    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0
        )

        content = response.output[0].content[0].text.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError("Réponse non-JSON")
        result = json.loads(match.group(0))

    except Exception as e:
        print(f"Erreur API ou parsing : {e}")
        result = {}

    # Normalisation : minuscules, suppression des doublons et espaces
    for key in ["reason_abandon", "behavior_keywords", "compatibility_keywords",
                "health_keywords", "adoption_keywords"]:
        val = result.get(key)
        if isinstance(val, list):
            cleaned = sorted(set(v.lower().strip() for v in val if isinstance(v, str)))
            result[key] = cleaned
        elif isinstance(val, str):
            result[key] = [v.strip().lower() for v in val.split(",")]
        else:
            result[key] = []

    return result


# ============================================================
# TRAITEMENT AVEC SAUVEGARDE PROGRESSIVE
# ============================================================

results = []

for i, desc in enumerate(tqdm(df["description"], desc="Analyse des descriptions")):
    result = analyze_description(desc)
    results.append(result)

    # Sauvegarde partielle régulière
    if (i + 1) % SAVE_INTERVAL == 0:
        temp_df = pd.concat([df.iloc[:i+1], pd.json_normalize(results)], axis=1)
        temp_df.to_csv(OUTPUT_FILE, index=False)
        print(f"Sauvegarde intermédiaire à {i+1} lignes")

# Fusion finale et export complet
structured_df = pd.json_normalize(results)
df_final = pd.concat([df, structured_df], axis=1)
df_final.to_csv(OUTPUT_FILE, index=False)

print(f"Traitement terminé et fichier sauvegardé : {OUTPUT_FILE}")
