import pandas as pd
import ast
from tqdm import tqdm

# ==========================
# 1️⃣ Chargement du fichier
# ==========================
INPUT_FILE = "animaux_spa_key_words.csv"
OUTPUT_FILE = "animaux_spa_expanded.csv"

tqdm.pandas()
df = pd.read_csv(INPUT_FILE, dtype=str, encoding="utf-8")
print(f"📦 {df.shape[0]} lignes chargées.")

# ==========================
# 2️⃣ Colonnes contenant des listes
# ==========================
list_cols = [
    "reason_abandon",
    "behavior_keywords",
    "compatibility_keywords",
    "health_keywords",
    "adoption_keywords"
]

# ==========================
# 3️⃣ Convertir les chaînes en vraies listes Python
# ==========================


def to_list(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return x
    s = str(x).strip()
    if not s or s.lower() in ["nan", "none"]:
        return []
    try:
        val = ast.literal_eval(s)
        if isinstance(val, list):
            return val
        else:
            return [val]
    except Exception:
        cleaned = s.replace("[", "").replace("]", "").replace("'", "")
        return [v.strip() for v in cleaned.split(",") if v.strip()]


for col in list_cols:
    df[col] = df[col].progress_apply(to_list)

# ==========================
# 4️⃣ Expansion des lignes
# ==========================
expanded_rows = []

for _, row in tqdm(df.iterrows(), total=len(df), desc="🔄 Expansion des listes"):
    # Trouver la longueur max parmi les colonnes à liste
    max_len = max(len(row[col]) for col in list_cols)
    if max_len == 0:
        expanded_rows.append(row.to_dict())
        continue

    for i in range(max_len):
        new_row = row.copy()
        for col in list_cols:
            items = row[col]
            new_row[f"{col}_separated"] = items[i] if i < len(items) else None
        expanded_rows.append(new_row.to_dict())

# Créer le DataFrame final
df_expanded = pd.DataFrame(expanded_rows)

# ==========================
# 5️⃣ Supprimer les colonnes *_keywords originales
# ==========================
df_expanded.drop(columns=list_cols, inplace=True)

# ==========================
# 6️⃣ Sauvegarde
# ==========================
df_expanded.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
print(f"✅ Fichier exporté : {OUTPUT_FILE}")
print(f"📊 Nombre total de lignes : {len(df_expanded)}")
