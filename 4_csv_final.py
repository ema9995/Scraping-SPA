import os
import re
import sys
import unicodedata
import pandas as pd

# -----------------------------
# Étape 0. Définir les fichiers I/O
# -----------------------------
# Fichier d’entrée (ton fichier)
INPUT_CSV = "animaux_spa_expanded.csv"
# Fichier de sortie (résultat)
OUTPUT_CSV = "animaux_spa_VERSION_FINALE_ZERO_RESTE.csv"

# --------------------------------
# Étape 1. Normalisation du texte
# --------------------------------


def norm(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.replace("-", "_").replace("’", "'").replace("“", "\"").replace("”", "\"")
    s = re.sub(r"[^a-z0-9_/\+'\s]", " ", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s

# -----------------------------------
# Étape 2. Tokenisation des cellules
# -----------------------------------


def split_tokens(cell: str):
    if cell is None or (isinstance(cell, float) and pd.isna(cell)) or str(cell).strip() == "":
        return []

    s = str(cell)
    for sep in [",", ";", "|", "/", "\\", "\n", "\t"]:
        s = s.replace(sep, "|")

    parts = [p for p in s.split("|") if p and p.strip()]
    toks, seen = [], set()
    for p in parts:
        t = norm(p)
        if t and t not in seen:
            toks.append(t)
            seen.add(t)

    return toks

# -------------------------------------------
# Étape 3. Utilitaire de matching "famille"
# -------------------------------------------


def any_substr(token_or_joined, substrings):
    return any(sub in token_or_joined for sub in substrings)

# ------------------------------------------------
# Étape 4. Règles de catégorisation - BEHAVIOR
# ------------------------------------------------


BEHAVIOR_RULES = [
    ("Agressif/Réactif/Protecteur", dict(substr=[
        "agress", "react", "defens", "protect", "mord", "aboie", "feul", "domin", "territor",
        "imprevis", "brusq", "brutal", "fort_caract", "caractere_fort", "protection_ressource",
        "protection_nourriture", "protection_jouets", "peut_mordre", "grogner", "pincer", "virulent"
    ])),
    ("Anxieux/Stressé/Sensible", dict(substr=[
        "anx", "stress", "angoiss", "hypervigil", "mal_a_l_aise", "sensible", "deprim",
        "emotion", "frustr", "terrori", "panique", "inquiet", "mal_aise", "mal_etre"
    ])),
    ("Craintif/Timide/Méfiant", dict(substr=[
        "craint", "timid", "mefi", "apeur", "peur", "reserve", "planque", "distante",
        "non_contact", "inapproch", "farouch", "fuit", "sur_ses_gardes", "reticent",
        "pas_contact", "hesitant"
    ])),
    ("Énergique/Joueur/Curieux", dict(substr=[
        "energ", "dynami", "joue", "actif", "sport", "vif", "fugue", "curieux",
        "plein", "explor", "tonique", "exuber", "fougue", "excitation", "foufou",
        "rapide", "gambade", "vigoureux", "balade", "balades"
    ])),
    ("Sociable/Affectueux/Joyeux", dict(substr=[
        "calin", "câlin", "affect", "sociab", "proche", "joyeux", "gentil", "adorable",
        "fusionnel", "tendre", "amical", "complice", "gratouill", "ronron", "attachant",
        "attachants", "pot_de_colle", "avenant", "caresse", "aime_caresses", "douceur", "doux",
        "amour", "loyal", "mignon", "amoureux", "coeur", "bienveillant",
        "complicite", "reconnaissant", "joie", "familier"

    ])),
    ("Indépendant/Solitaire", dict(substr=[
        "independ", "solit", "vit_seul", "seul", "individuel", "solitaire"
    ])),
    ("Éduqué/Intelligent/Propre", dict(substr=[
        "propre", "eduqu", "intelligent", "obeiss",
        "ecoute", "sage", "apprend_vite", "exemplaire", "controle", "equilibre", "obeissan"

    ])),
    ("Calme/Posé", dict(substr=[
        "calme", "pose", "tranquil", "paisibl", "detendu",
        "discret", "apais", "posee", "serenite", "seren", "rassure", "rassure"

    ])),
    ("Besoin d'éducation/Patience", dict(substr=[
        "besoin", "patien", "confianc", "apprent", "sociabilis", "respect", "limite",
        "creation_de_lien", "education", "a_apprendre", "en_cours_d_evaluation",
        "a_decouvrir", "a_conna", "progress", "travail", "guidance",
        "familiarisation", "acclimat", "a_tester", "enrichissement",
        "demande_attention", "demande_interactions", "hyperattachement",
        "gestion_emotion", "a_etudier", "requiert_patience",
        "consentement", "adaptation", "temps_d_adaptation", "temps_adaptation", "necessite_temps"

    ])),
    ("Gourmand/Voleur", dict(substr=[
        "gourmand", "glouton", "friand", "gros_mangeur", "croquette", "gourmandise", "voleu"
    ])),
]


def map_behavior_category(toks):
    for t in toks:
        for cat, rule in BEHAVIOR_RULES:
            if any_substr(t, rule["substr"]):
                return cat
    return "Besoin d'éducation/Patience" if toks else ""

# ------------------------------------------------
# Étape 5. Règles de catégorisation - HEALTH
# ------------------------------------------------


HEALTH_RULES = [
    ("Sain/Stérilisé/Vacciné", dict(substr=[
        "sain", "bonne_sante", "bon_bilan", "parfaite_sante", "en_forme",
        "tres_bonne_sant", "tres_bonne_sant",
        "vaccin", "castre", "sterilis", "identifi", "puce",
        "propre", "heureux", "securise",
        "aucune_pathologie", "pleine_forme", "brillant",
        "en_sante", "bon_etat", "sante_ok", "saine"

    ])),
    ("Maladies Virales", dict(substr=[
        "fiv", "sida", "felv", "leucose", "calic", "coryza", "gingivite", "double_positif",
        "porteur_pif", "porte_calicivirus", "calicivirus", "leucose_positive",
        "porteuse_gingivite", "gingivostomatite_chronique"

    ])),
    ("Maladies Chroniques", dict(substr=[
        "diabet", "insuffisance_ren", "cardio", "souffle", "thyroid", "pancreat", "leish",
        "hypertension", "mici", "cardiopath", "epilept", "intolerance_medicament",
        "thyroide", "coeur", "cardiaque"

    ])),
    ("Soins & Convalescence", dict(substr=[
        "traitement", "soin", "bless", "oper", "extraction", "plaie", "cicatri",
        "hospital", "injection", "sedat",
        "recovery", "reprise_de_poids", "en_reconvalescence",
        "soins_quotidiens", "soins_specifiques", "fracture", "operation",
        "antibiot", "pommade", "bains", "bandage", "soignee", "soigne",
        "repos", "rehabilitation", "reeducation", "reconstruction"

    ])),
    ("Handicap/Mobilité/Sensoriel", dict(substr=[
        "handi", "mobil", "aveugl", "sourd", "incontin", "arthros", "dysplas",
        "amput", "paralys", "boit", "atax", "malformat", "sequell",
        "perte_vue", "un_oeil", "kera", "malentend", "mal_voyant",
        "3_pattes", "borgne", "problemes_neurolog", "trouble_cardiaque",
        "raideur_patte", "troubles_locomoteurs", "perte_oeil", "equilibre", "equilibre_altere"

    ])),
    ("Âgé/Senior", dict(substr=[
        "age", "age", "senior", "vieillis", "agee", "agee", "vieillissante",
        "longue_vie", "11_ans", "15_ans", "6_mois", "annee", "annee", "vieux", "vieillissant"
    ])),
    ("Alimentation Spécifique", dict(substr=[
        "aliment", "hypoallergen", "urinar", "gastro", "regime", "surpoids", "calcul",
        "urinary", "dermatolog", "poids_ideal", "obese",
        "regime_particulier", "alimentation_renale", "alimentation_urinaire"

    ])),
    ("Fragile/SOS", dict(substr=[
        "fragil", "maig", "deprim", "sos", "stress", "retape", "denutri",
        "fatigu", "souffrant", "sante_precaire", "mauvais_etat", "squelettique",
        "anemie", "faible_esperance", "souffrance", "douloureux",
        "mourant", "emphyse", "emphyseme"

    ])),
    ("Légal/Catégorisé", dict(substr=[
        "categorie", "categorie", "legis", "permis", "musel",
        "diagnose", "documents", "casier", "certificat", "sous_loi",
        "lof", "categorie_1", "legislation_2eme_categorie",
        "documents_specifiques", "diagnose_obligatoire", "categorise"

    ])),
    ("Statut Incertain/Suivi", dict(substr=[
        "non_connu", "non_prec", "non_precise", "non_precise", "non_precise",
        "non_spec", "non_ident", "a_eval", "a_tester", "suivi", "en_travail",
        "a_surveiller", "impacte", "socialisation_a_revoir", "en_socialisation",
        "non_vu_veterinaire", "visite", "visites", "examen", "examens", "controle",
        "a_rythme_propre", "proprete_a_revoir", "environnement_calme", "pas_exterieur",
        "interieur_seulement", "vivre_en_interieur", "ne_sort_pas", "seul_felin",
        "sans_congeneres", "seul_chat", "statut", "a_apprendre", "en_cours_de_travail",
        "attente", "en_attente", "rendez", "rendez_vous", "documents", "interieur",
        "pas_exterieur", "accompagn", "attestation"
    ])),
]


def map_health_category(toks):
    for t in toks:
        for cat, rule in HEALTH_RULES:
            if any_substr(t, rule["substr"]):
                return cat
    return "Statut Incertain/Suivi" if toks else ""

# ------------------------------------------------
# Étape 6. Règles de catégorisation - ADOPTION
# ------------------------------------------------


ADOPT_RULES = [
    ("Besoin d'Extérieur/Jardin", dict(substr=[
        "jardin", "exter", "exterieur", "acces_exterieur", "plein_pied",
        "terrain", "balade", "promenade", "semi_liberte", "liberte",
        "enclos", "campagne", "sortie", "verdure", "balcon", "foin",
        "pature", "herbe", "acces_exterieur"

    ])),
    ("Vie en Appartement", dict(substr=[
        "appartement", "interieur", "interieur_seulement", "sans_acces",
        "maison_sans_exterieur", "ville", "ascenseur", "rez", "logement"
    ])),
    ("Adoptant Expérimenté/Patient", dict(substr=[
        "experience", "experimente", "experimente", "connaisseur", "patient",
        "patience", "educateur", "education", "guidance",
        "accompagnement", "coherence", "methode",
        "responsable", "reflexion", "retraite", "suivi", "pointilleux"
    ])),
    ("Environnement Calme & Stable", dict(substr=[
        "environnement_calme", "tranquil", "seren", "securis", "stable",
        "foyer", "maison", "cocon", "cadre", "routine",
        "calme", "confiance", "temps", "rencontre", "stabilite",
        "serenite", "rassurer", "stabilite", "douceur", "securite"

    ])),
    ("Besoin de Dépense/Actif", dict(substr=[
        "depens", "dynam", "actif", "activit", "sport", "randonn",
        "agility", "clicker", "stimulation", "defoulement", "exercice"

    ])),
    ("Besoin de Présence Humaine", dict(substr=[
        "presence", "present", "compagnie", "contact", "famille", "pas_seul",
        "solitude", "attention", "calin", "tendresse", "disponibil",
        "humain", "proche", "ronron", "ami", "compagnon"

    ])),
    ("Doit être Seul Animal", dict(substr=[
        "maison_sans_autres_animaux", "sans_autres", "seul_animal",
        "exclusif", "sans_animaux", "seule", "exclusivite", "seul"
    ])),
    ("Sociable avec Congénères", dict(substr=[
        "congener", "autre_chat", "autre_chien", "sociable", "binome", "duo",
        "frere", "en_duo", "troupeau", "meute", "avec", "cohabitation",
        "deux_chats", "partenaire", "copain", "deux_animaux"

    ])),
    ("SOS/Urgent", dict(substr=["sos", "urgent", "urgence"])),
    ("Légal/Suivi Spécifique", dict(substr=[
        "permis", "musel", "attestation", "certificat", "casier", "condition",
        "visite", "questionnaire", "documents", "regle", "caution", "cheque",
        "legislation", "formation"
    ])),
]


def adoption_fallback(toks):
    if not toks:
        return ""
    joined = " ".join(toks)

    if any_substr(joined, [
        "seul", "exclusif", "sans_autres", "seule", "exclusivite", "seul_animal"
    ]):
        return "Doit être Seul Animal"

    if any_substr(joined, [
        "calme", "confiance", "temps", "rencontre", "environnement", "stabil",
        "seren", "douceur", "stabilite", "tranquil", "serenite", "rassurer",
        "securis", "securite"
    ]):
        return "Environnement Calme & Stable"

    if any_substr(joined, [
        "experimen", "educateur", "connaiss", "patient", "guidance",
        "suivi", "reflexion", "responsable"
    ]):
        return "Adoptant Expérimenté/Patient"

    if any_substr(joined, [
        "presence", "present", "compagnie", "contact", "famille", "pas_seul",
        "solitude", "attention", "proche", "humain", "ronron", "ami", "compagnon"
    ]):
        return "Besoin de Présence Humaine"

    if any_substr(joined, [
        "jardin", "exter", "exterieur", "acces_exterieur", "plein_pied", "terrain",
        "balade", "promenade", "semi_liberte", "liberte", "enclos", "campagne",
        "sortie", "verdure", "balcon"
    ]):
        return "Besoin d'Extérieur/Jardin"

    return "Environnement Calme & Stable"


def map_adoption_category(toks):
    for t in toks:
        for cat, rule in ADOPT_RULES:
            if any_substr(t, rule["substr"]):
                return cat
    return adoption_fallback(toks)


def map_compatibility_norm(toks):
    if not toks:
        return ""

    tags, seen = [], set()
    for t in toks:
        if t.startswith("chats"):
            v = "chats:oui" if ("ok" in t or "oui" in t) else \
                ("chats:non" if "non" in t else "chats:inconnu")
        elif t.startswith("chiens"):
            v = "chiens:oui" if ("ok" in t or "oui" in t) else \
                ("chiens:non" if "non" in t else "chiens:inconnu")
        elif t.startswith("enfants"):
            v = "enfants:oui" if ("ok" in t or "oui" in t) else \
                ("enfants:non" if "non" in t else "enfants:inconnu")
        else:
            v = None

        if v and v not in seen:
            seen.add(v)
            tags.append(v)

    return ";".join(sorted(tags))

# -------------------------------------------
# Étape 8. Exécution globale
# -------------------------------------------


def main():
    # 8.1 Lecture du CSV source
    src = INPUT_CSV
    dst = OUTPUT_CSV
    if not os.path.exists(src):
        print(f"Erreur: le fichier d'entrée n'existe pas: {src}", file=sys.stderr)
        sys.exit(1)

    print(f"Lecture: {src}")
    df = pd.read_csv(src)

    # 8.2 Colonnes d'entrée attendues
    behavior_col = "behavior_keywords_separated"
    compat_col = "compatibility_keywords_separated"
    health_col = "health_keywords_separated"
    adopt_col = "adoption_keywords_separated"

    # 8.3 Assurer l'existence des colonnes + NaN -> ""
    for col in [behavior_col, compat_col, health_col, adopt_col]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")

    # 8.4 Application: cellule -> tokens -> catégorie/tags
    df["behavior_category"] = df[behavior_col].apply(
        lambda x: map_behavior_category(split_tokens(x)))

    df["health_category"] = df[health_col].apply(
        lambda x: map_health_category(split_tokens(x)))

    df["adoption_category"] = df[adopt_col].apply(
        lambda x: map_adoption_category(split_tokens(x)))

    df["compatibility_tags"] = df[compat_col].apply(
        lambda x: map_compatibility_norm(split_tokens(x)))

    # 8.5 Écriture du CSV résultat
    df.to_csv(dst, index=False)
    print(f"Écrit: {dst}")


if __name__ == "__main__":
    main()
