<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Outil d'Analyse et de Transcription Audio

Wavoscope est un outil puissant de visualisation audio en temps réel et d'aide à la transcription conçu pour les musiciens, les transcripteurs et les ingénieurs du son. Il fournit des formes d'onde haute fidélité, une analyse spectrale et un système de marqueurs robuste pour vous aider à déconstruire des flux audio complexes.

![Interface Principale](docs/images/main_view.png)

---

## 🚀 Prise en Main

### Gestion de Projet
Wavoscope utilise un système de fichiers "sidecar". Lorsque vous ouvrez un fichier audio, Wavoscope crée ou charge un fichier `.oscope` dans le même répertoire pour stocker vos marqueurs, boucles et paramètres.
- **Ouvrir :** Cliquez sur l'icône de dossier dans la barre de lecture pour charger n'importe quel format audio courant (MP3, WAV, FLAC, etc.).
- **Enregistrer :** Cliquez sur l'icône de disquette. L'icône brillera avec la couleur d'accent de votre thème lorsqu'il y aura des modifications non enregistrées.

---

## 🎵 Navigation & Lecture

- **Zoom :** Utilisez la **molette de la souris** sur la forme d'onde ou le spectre pour zoomer/dézoomer.
- **Défilement :** Utilisez la **molette de la souris** sur la **timeline** pour faire défiler le temps.
- **Panoramique :** **Cliquez et faites glisser** la forme d'onde ou le spectre pour vous déplacer dans la timeline.
- **Subdivisions Adaptatives :** La timeline ajuste automatiquement ses pas de grille (de 0,01s à plusieurs heures) au fur et à mesure que vous zoomez, garantissant un niveau de détail optimal sans encombrement.
- **Curseur de Lecture :** **Clic gauche** sur la forme d'onde pour déplacer la tête de lecture.
- **Contrôle de la Vitesse :** Utilisez le curseur dans la barre du bas pour ajuster la vitesse de 0,1x à 2,0x. Wavoscope utilise un étirement temporel de haute qualité qui préserve la hauteur tonale (pitch).

---

## 🔍 Analyse Spectrale & Filtrage

La moitié inférieure de l'écran affiche un spectrogramme à transformée en Q constante (CQT), mappé sur un clavier de piano. Vous pouvez ajuster la **fenêtre FFT** et le **décalage d'octave** à l'aide des commandes situées dans l'en-tête de l'analyseur de spectre.

![Filtrage Spectral](docs/images/spectrum_filter.png)

### Filtrage Avancé
Vous pouvez isoler des instruments ou des notes spécifiques à l'aide du filtre passe-bande en temps réel. Les poignées du filtre (lignes verticales sur le spectre) sont toujours disponibles :
- **Activer/Désactiver Coupure :** **Clic droit** sur une poignée de filtre pour activer ou désactiver cette limite.
- **Placement Rapide :** **Clic droit** n'importe où sur le spectrogramme pour déplacer la poignée de filtre la plus proche et l'activer.
- **Retour Visuel :** Lorsqu'une coupure est activée, la zone située en dehors de sa plage est assombrie pour vous aider à vous concentrer. Si les deux sont désactivées, le filtre est ignoré.

---

## 🚩 Marqueurs & Transcription

Wavoscope utilise un système à double marqueur pour vous aider à cartographier la structure et l'harmonie d'une piste.

### Marqueurs de Rythme (Mesures)
- **Placement :** Appuyez sur `B` (par défaut) ou faites un **clic gauche** sur la timeline pour placer un marqueur de rythme.
- **Subdivisions :** Ouvrez le dialogue du marqueur (**clic droit** sur la poignée) pour définir les subdivisions (ex: 4 pour des noires). Celles-ci apparaissent sous forme de fines lignes verticales sur la timeline.
- **Métronome :** Les marqueurs de rythme déclenchent automatiquement un clic de métronome pendant la lecture si les clics de subdivision sont activés.
- **Maj + Clic :** Place automatiquement un nouveau marqueur au même intervalle que le précédent, parfait pour cartographier rapidement un rythme régulier.
- **Sections :** Marquez un marqueur comme "Début de section" pour lui donner une étiquette (comme "Couplet" ou "Refrain").

![Dialogue Marqueur de Rythme](docs/images/rhythm_dialog.png)

### Marqueurs d'Harmonie (Accords)
- **Placement :** Appuyez sur `H` (par défaut) ou faites un **clic droit** sur la timeline pour placer un marqueur d'harmonie.
- **Éditeur d'Accords :** **Clic droit** sur un marqueur existant pour ouvrir le dialogue d'accord. Vous pouvez taper les noms d'accords (ex: "Am7", "C/G") ou utiliser les sélecteurs.
- **Analyse Automatique :** Utilisez le bouton **Suggérer** pour laisser Wavoscope analyser l'audio à cette position et recommander l'accord le plus probable.
- **Écoute :** **Maintenez le clic gauche** sur une poignée de marqueur d'harmonie ou cliquez sur le bouton "Lecture" dans le dialogue pour entendre l'accord joué via le synthétiseur interne.

![Dialogue Marqueur d'Harmonie](docs/images/harmony_dialog.png)

### Gestion des Marqueurs
- **Glisser :** Vous pouvez **cliquer et faire glisser** n'importe quelle poignée de marqueur sur la timeline pour affiner sa position.
- **Superpositions :** Lorsqu'un marqueur de rythme et un marqueur d'harmonie occupent le même espace, ils sont affichés à mi-hauteur (Harmonie en haut, Rythme en bas) afin que vous puissiez toujours interagir avec les deux.
- **Boucles :** Utilisez le bouton de boucle dans la barre de lecture pour basculer entre les marqueurs ou la piste entière.

---

## 🎤 Transcription des Paroles

Wavoscope dispose d'une piste de paroles interactive qui permet une transcription et un alignement à haute vitesse.

![Transcription des Paroles](docs/images/lyrics_track.png)

### Flux de Travail de Transcription
1. **Afficher la Piste :** Cliquez sur le bouton "Paroles" dans l'en-tête de la forme d'onde pour afficher la piste de transcription.
2. **Ajouter & Taper :** Appuyez sur `L` ou faites un **clic simple** sur un espace vide de la piste de paroles pour ajouter un mot.
3. **Saisie Rapide :** Pendant que vous tapez dans une boîte de paroles, appuyez sur **Espace** ou **Tiret (`-`)**. Cela va automatiquement :
    - Valider le mot actuel.
    - Créer une nouvelle boîte de paroles immédiatement après (à la position actuelle de lecture ou à la fin de la précédente).
    - Déplacer le focus vers la nouvelle boîte pour que vous puissiez continuer à taper sans arrêter la musique.
4. **Navigation :** Utilisez `Maj + Gauche/Droite` pour sauter entre les éléments de paroles. C'est parfait pour vérifier le timing.

### Édition & Redimensionnement
- **Déplacement :** **Faites glisser** le centre (80%) d'une boîte de paroles pour la déplacer.
- **Timing :** **Faites glisser** les bords (seuil de 10%) d'une boîte de paroles pour ajuster son début ou sa fin.
- **Précision :** Utilisez les **touches fléchées** lorsqu'une parole est sélectionnée pour la décaler de 0,1s. Utilisez les flèches **Haut/Bas** pour ajuster la durée.
- **Formatage :** Les boîtes de paroles s'estompent et masquent le texte automatiquement lorsqu'elles deviennent trop petites à de faibles niveaux de zoom, gardant l'interface propre.

---

## ⚙️ Paramètres & Personnalisation

![Dialogue de Paramètres](docs/images/settings_dialog.png)

Accédez aux paramètres via l'icône d'engrenage dans la barre de lecture :
- **Touches Piano Visibles :** Ajustez le nombre de touches affichées dans le piano roll du spectre.
- **Volume du Clic :** Contrôlez le volume des subdivisions du métronome.

### Thèmes
Wavoscope est entièrement personnalisable via des thèmes. Choisissez le look qui convient à votre environnement :
- **Cosmic :** Violets profonds et accents nébuleux.
- **Dark :** Mode sombre classique, reposant pour les yeux.
- **Doll :** Roses énergiques et tons ludiques.
- **Hacker :** Vert terminal rétro sur fond noir.
- **Light :** Look professionnel propre et haute luminosité.
- **Neon :** Bleus électriques et vibrations à haut contraste.
- **OLED :** Fond noir pur pour un contraste maximal.
- **Retrowave :** Esthétique synthwave des années 80.
- **Toy :** Couleurs primaires vives.
- **Warm :** Tons terreux et confortables pour les longues sessions.


---

## 🌍 Localisation

Wavoscope prend en charge plusieurs langues. Vous pouvez changer la langue dans l'onglet **Paramètres > Global**.

### Traductions Personnalisées
Wavoscope est conçu pour être géré par la communauté. Vous pouvez ajouter ou modifier des traductions en éditant les fichiers JSON dans le répertoire `resources/locales`.
- Pour ajouter une nouvelle langue, créez un nouveau fichier JSON (ex: `fr.json`) et ajoutez un champ `"meta": { "name": "Français" }`.
- L'application détectera et listera automatiquement tout fichier de traduction valide dans le menu des paramètres.

---

## ⌨️ Commandes Complètes

### Raccourcis Clavier
| Action | Touche |
| :--- | :--- |
| **Lecture / Pause** | `Espace` |
| **Saut Avant/Arrière** | `Gauche` / `Droite` |
| **Augmenter/Diminuer Vitesse** | `Haut` / `Bas` |
| **Ajouter Marqueur Rythme** | `B` |
| **Ajouter Marqueur Harmonie** | `H` |
| **Ajouter/Valider Paroles** | `L` |
| **Diviser & Avancer Paroles**| `Espace` / `-` (Dans l'entrée) |
| **Changer Mode de Boucle** | `Tab` |
| **Désélectionner Tout** | `Maj + L` |
| **Naviguer entre Paroles** | `Maj + Gauche/Droite` |
| **Supprimer l'Élément** | `Suppr` / `Retour Arrière` |
| **Ouvrir un Fichier** | `Ctrl + O` |
| **Enregistrer le Projet** | `Ctrl + S` |

### Interactions Souris
| Zone | Action | Interaction |
| :--- | :--- | :--- |
| **Timeline** | Ajouter Marqueur Rythme | `Clic Gauche` |
| **Timeline** | Placement Auto du Marqueur de Rythme | `Maj + Clic Gauche` |
| **Timeline** | Ajouter Marqueur Harmonie | `Clic Droit` |
| **Timeline** | Déplacer Marqueur | `Glisser Gauche` |
| **Timeline** | Écouter Accord | `Maintenir Clic Gauche` sur Harmonie |
| **Timeline** | Faire Défiler Vue | `Molette Souris` |
| **Forme d'Onde** | Déplacer Lecture | `Clic Gauche` |
| **Forme d'Onde** | Panoramique Vue | `Glisser Gauche` |
| **Forme d'Onde** | Zoom | `Molette Souris` |
| **Spectre** | Jouer Note Sinusoïdale | `Clic / Glisser Gauche` |
| **Spectre** | Activer/Désactiver Coupure | `Clic Droit` poignée |
| **Spectre** | Placer Coupure | `Clic Droit` n'importe où |
| **Spectre** | Ajuster Coupure | `Glisser Gauche` poignée |
