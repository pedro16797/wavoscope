import os
import json

def update_data(lang, data):
    # Description
    translations = {
        "en": "The following keybinds do not correspond to any graphical interface element.",
        "es": "Los siguientes atajos de teclado no corresponden a ningún elemento de la interfaz gráfica.",
        "gl": "Os seguintes atallos de teclado non corresponden a ningún elemento da interface gráfica.",
        "fr": "Les raccourcis clavier suivants ne correspondent à aucun élément de l'interface graphique.",
        "de": "Die folgenden Tastenkombinationen entsprechen keinem grafischen Interface-Element.",
        "it": "Le seguenti scorciatoie da tastiera non corrispondono a nessun elemento dell'interfaccia grafica.",
        "pt": "Os seguintes atalhos de teclado não correspondem a nenhum elemento da interface gráfica.",
        "zh": "以下快捷键不对应任何图形界面元素。"
    }
    data["settings"]["kb_no_ui_desc"] = translations[lang]

    # Play hint
    play_translations = {
        "en": "Left Click to Play",
        "es": "Clic izquierdo para tocar",
        "gl": "Clic esquerdo para tocar",
        "fr": "Clic gauche pour jouer",
        "de": "Linksklick zum Spielen",
        "it": "Clic sinistro per suonare",
        "pt": "Clique esquerdo para tocar",
        "zh": "左键单击播放"
    }
    data["keys"]["left_click_play"] = play_translations[lang]

    # Terminology updates from previous turns
    if lang == "en":
        data["settings"]["kb_harmony"] = "Add Chord Flag"
        data["chord"]["edit_title"] = "Edit Chord Flag"
        data["settings"]["kb_audition"] = "Audition Chord" # Even if removed, good for consistency

    # Toggle -> Add for lyrics (already mostly done in files, but let's be sure)
    lyrics_labels = {
        "en": "Add Lyrics Flag",
        "es": "Añadir marca de letra",
        "gl": "Engadir marca de letra",
        "fr": "Ajouter un marqueur de paroles",
        "de": "Songtext-Markierung hinzufügen",
        "it": "Aggiungi marcatore testo",
        "pt": "Adicionar marca de letra",
        "zh": "添加歌词标记"
    }
    data["settings"]["kb_lyrics"] = lyrics_labels[lang]

    # Remove keys
    unused_keys = [
        "kb_play_pause", "kb_stop", "kb_seek", "kb_metronome",
        "kb_settings", "kb_open", "kb_save", "kb_export",
        "kb_delete", "kb_low_cutoff", "kb_high_cutoff", "kb_toggle_cutoff",
        "kb_lyrics_mouse", "kb_audition"
    ]

    for key in unused_keys:
        if key in data["settings"]:
            del data["settings"][key]

    if "right_click_handle" in data["keys"]:
        del data["keys"]["right_click_handle"]

    return data

for lang in ["en", "es", "gl", "fr", "de", "it", "pt", "zh"]:
    filepath = f"resources/locales/{lang}.json"
    if not os.path.exists(filepath):
        continue

    # Restore to clean state first to avoid duplicate efforts or broken JSON
    os.system(f"git checkout {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data = update_data(lang, data)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
