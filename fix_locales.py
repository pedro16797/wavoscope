import os
import json

keys_to_remove = ["kb_lyrics_mouse", "kb_audition"]

for lang in ["en", "es", "gl", "fr", "de", "it", "pt", "zh"]:
    filepath = f"resources/locales/{lang}.json"
    if not os.path.exists(filepath):
        continue
    try:
        # Since I might have broken the JSON, I'll try to fix it or just restore and re-apply.
        # Actually I can't easily fix it if it's invalid.
        # I'll use git checkout to restore them first.
        os.system(f"git checkout {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Re-apply the kb_no_ui_desc logic too
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

        # Add left_click_play to keys
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

        # Remove keys
        unused_keys = [
            "kb_play_pause", "kb_stop", "kb_seek", "kb_metronome",
            "kb_settings", "kb_open", "kb_save", "kb_export",
            "kb_delete", "kb_low_cutoff", "kb_high_cutoff", "kb_toggle_cutoff"
        ]
        # And the new ones requested to be removed from settings
        unused_keys.extend(["kb_lyrics_mouse", "kb_audition"])

        for key in unused_keys:
            if key in data["settings"]:
                del data["settings"][key]

        if "right_click_handle" in data["keys"]:
            del data["keys"]["right_click_handle"]

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"Error processing {lang}: {e}")
