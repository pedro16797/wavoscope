# Transcription et Alignement des Paroles

Wavoscope propose une piste dédiée aux paroles pour la transcription interactive, l'alignement au mot près et l'exportation MusicXML. Cette fonctionnalité est conçue pour une saisie rapide et un ajustement précis du timing.

## Concepts Fondamentaux

### La Piste de Paroles
La piste de paroles est une piste spécialisée basée sur canvas située au-dessus de la forme d'onde principale. Elle affiche les éléments de paroles sous forme de boîtes éditables.
- **Visibilité :** Activez la piste à l'aide du bouton "Paroles" dans l'en-tête de la forme d'onde.
- **Échelle :** La hauteur de la piste est fixe (32px), mais son contenu s'adapte au zoom et au défilement globaux.
- **Sélection :** Une seule parole peut être sélectionnée à la fois. La sélection d'une parole la met en surbrillance et active des raccourcis clavier spécifiques.

### Flux de Travail : "Taper-Diviser-Avancer"
La méthode la plus efficace pour transcrire une chanson est de suivre ce flux de travail :
1.  **Démarrage :** Appuyez sur `V` ou cliquez sur un espace vide pour créer la première parole à la position actuelle de lecture.
2.  **Saisie :** Tapez le premier mot.
3.  **Division :** Appuyez sur `Espace` (pour les nouveaux mots) ou `-` (pour les syllabes au sein d'un mot). Cela valide le texte actuel et crée immédiatement une nouvelle boîte de paroles.
    - **Différenciation visuelle :** Les mots divisés par des traits d'union (syllabes) sont visuellement reliés par une ligne horizontale dans la timeline. Le trait d'union lui-même est stocké dans les données mais masqué dans l'interface utilisateur lorsqu'il n'est pas en cours d'édition, offrant un aspect épuré.
4.  **Répétition :** Le focus est automatiquement transféré à la nouvelle boîte, vous permettant de continuer la transcription pendant que la musique joue.
5.  **Validation :** Appuyez sur `Entrée` ou cliquez ailleurs pour terminer l'édition.

## Interactions et Raccourcis

### Contrôle à la Souris
- **Clic simple (espace vide) :** Ajoute une nouvelle parole à ce timestamp et passe en mode édition.
- **Clic gauche (boîte existante) :** Sélectionne la parole.
- **Clic simple (boîte sélectionnée) :** Désélectionne la parole.
- **Glisser (centre 80%) :** Déplace l'élément de parole le long de la timeline.
- **Glisser (bords 10%) :** Redimensionne la parole. Glisser le bord gauche ajuste le début ; glisser le bord droit ajuste la durée.
- **Double-clic :** Entre en mode édition pour la parole cliquée.
- **Clic sur le fond :** Désélectionne la parole actuelle.

### Raccourcis Clavier

| Touche | Action | Contexte |
|-------|--------|----------|
| `V` | Ajouter / Valider et Avancer | Global |
| `Maj + V` | Tout désélectionner | Global |
| `Tab` | Changer mode de boucle | Global |
| `Entrée` | Démarrer/Terminer édition | Sélectionné |
| `Échap` | Annuler édition / Désélectionner | Sélectionné |
| `Flèches / `A` / `D` / `W` / `S` (Gauche/Droite)` | Ajuster position (0.1s) | Sélectionné (Hors édition) |
| `Flèches / `A` / `D` / `W` / `S` (Haut/Bas)` | Ajuster durée (0.1s) | Sélectionné (Hors édition) |
| `Maj + Flèches / `A` / `D` / `W` / `S`` | Naviguer entre paroles | Global / Sélectionné |
| `Espace / -` | Valider et générer suivant | En édition |

## Implémentation Technique

### Frontend
- **`LyricsTimeline.tsx`** : Utilise un système de gestion d'état basé sur des références pour gérer les interactions haute fréquence (glisser) localement avant de valider sur le backend. Utilise un `ResizeObserver` pour un rendu canvas réactif.
- **Gestion d'état** : Intégrée dans `projectSlice.ts`. Les opérations CRUD sont optimisées pour mettre à jour l'état local directement à partir des réponses du backend, minimisant les allers-retours réseau.
- **Visualisation** : Dispose d'un moteur de rendu dynamique qui gère la troncature du texte et l'estompement pour les petits éléments.

### Backend
- **Structure de données** : Les paroles sont stockées sous forme d'une liste ordonnée d'objets `{text, timestamp, duration}` dans le fichier `.oscope`.
- **Moteur de boucle** : Le `LoopingEngine` prend en charge un mode `lyric`, qui définit automatiquement la plage de boucle sur la parole actuellement sélectionnée.
- **Export MusicXML** : `session/export.py` divise les mesures en segments à chaque limite de paroles et d'harmonie. Cela garantit que les balises `<lyric>` sont parfaitement alignées avec la structure rythmique dans la partition exportée.

## Conseils d'Alignement
- **Zoom élevé :** Pour un alignement au mot près, zoomez jusqu'à ce que vous puissiez voir clairement les transitoires dans la forme d'onde.
- **Boucles :** Utilisez le mode de boucle `lyric` (basculez avec `Tab`) pour répéter le mot actuel tout en ajustant ses points de début et de fin.
- **Métronome :** Gardez les clics de subdivision activés pour vous assurer que vos paroles s'alignent avec les marqueurs de battement sous-jacents (Marqueurs de Rythme).
