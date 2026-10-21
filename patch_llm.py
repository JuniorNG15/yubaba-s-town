import sys

chemin = "backend/llm.py"
with open(chemin, encoding="utf-8", newline=None) as f:
    texte = f.read()
if "raison_d_abord" in texte:
    print("Deja applique, rien a faire :", chemin)
    sys.exit(0)
remplacements = [
    ("def decider(systeme, question, options, timeout=120):",
     "def decider(systeme, question, options, timeout=120, raison_d_abord=False):"),
    ('        "required": ["choix", "raison"],\n    }\n',
     '        "required": ["choix", "raison"],\n    }\n'
     '    if raison_d_abord:\n'
     '        p = schema["properties"]\n'
     '        schema["properties"] = {"raison": p["raison"], "choix": p["choix"]}\n'),
]
for ancien, nouveau in remplacements:
    n = texte.count(ancien)
    if n != 1:
        print(f"ERREUR : motif trouve {n} fois : {ancien!r}")
        sys.exit(1)
    texte = texte.replace(ancien, nouveau)
with open(chemin, "w", encoding="utf-8", newline="\n") as f:
    f.write(texte)
print("OK", chemin)
