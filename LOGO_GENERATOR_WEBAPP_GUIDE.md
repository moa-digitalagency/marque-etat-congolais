# Logo Generator WebApp - Specification Complète

## 📋 Vue d'ensemble

Cette documentation détaille **toutes les caractéristiques** nécessaires pour reproduire la fonctionnalité de génération du logo officiel congolais comme une **application web indépendante**.

**Cas d'usage**: Permettre aux unités consulaires de générer des logos officiels conformes à la Charte Graphique du Gouvernement RDC (février 2022).

---

## 🎨 Caractéristiques Principales

### 1. **Composition du Logo**

Structure horizontale (gauche à droite):
```
[Armoiries RDC] ← 85px → [Ligne d'État] ← 80px → [Nom Unité (MAJUSCULES)]
```

**Dimensions Finales:**
- Format: PNG transparent ou JPG fond blanc
- Hauteur maximale: 624px (fixée pour armoiries)
- Largeur: Dynamique selon le texte
- DPI: 96 (standard web)

### 2. **Composants Visuels**

#### a) **Armoiries (Emblème RDC)**
- Fichier: `armoiries.png` (transparent)
- Hauteur fixée: **624px**
- Largeur: Recalculée automatiquement selon aspect ratio
- Format: RGBA PNG
- Source: Charte Graphique RDC

#### b) **Ligne d'État**
- Fichier: `ligne_etat.png` (transparent)
- Hauteur: Auto (aspect ratio conservé)
- Largeur: Auto
- Format: RGBA PNG
- Rôle: Séparation verticale entre armoiries et texte

#### c) **Texte (Nom de l'Unité)**
- **Police:** Cooper Hewitt Bold (`CooperHewitt-Bold.otf`)
- **Taille:** 105px
- **Couleur:** Noir RGBA `(0, 0, 0, 255)`
- **Transformation:** MAJUSCULES
- **Interligne:** 110px (fixe entre lignes)
- **Alignement:** Vertical centered

### 3. **Algorithme de Découpe du Texte**

Le nom de l'unité est fractionné en lignes selon ces règles:

```
Règle 1: Première ligne = premier mot uniquement
Règle 2: Lignes suivantes = max 3 mots par ligne
Règle 3: Maximum 5 lignes total
Règle 4: Tout en MAJUSCULES

Exemple:
Input:  "Ambassade de la RDC en France"
Output:
  1. AMBASSADE
  2. DE LA RDC
  3. EN FRANCE
```

**Cas Limites:**
- Nom vide = Erreur `ValueError`
- Nom très long (>15 mots) = Tronqué à 5 lignes
- Mots individuels très longs (>50 caractères) = Peut dépasser largeur canvas

---

## 🛠️ Architecture Technique

### Backend (Python/Flask)

#### **Service: `LogoGeneratorService`**

**Fichier:** `services/logo_generator.py`

**Fonction Principale:** `generate_logo()`

```python
def generate_logo(
    unit_nom: str,
    armoiries_path: str,
    ligne_etat_path: str,
    font_path: str,
    armoiries_height: int = 624,
    spacing: int = 85,
    text_spacing: int = 80,
    font_size: int = 105,
    line_spacing: int = 110,
    text_color: tuple = (0, 0, 0, 255)
) -> BytesIO:
```

**Paramètres Configurables:**
| Paramètre | Valeur Défaut | Plage | Description |
|-----------|---------------|-------|-------------|
| `armoiries_height` | 624 | 400-900 | Hauteur des armoiries en pixels |
| `spacing` | 85 | 20-200 | Gap entre armoiries et ligne_etat |
| `text_spacing` | 80 | 20-200 | Gap entre ligne_etat et texte |
| `font_size` | 105 | 60-200 | Taille du texte en pixels |
| `line_spacing` | 110 | 80-150 | Interligne (espacement vertical) |
| `text_color` | (0,0,0,255) | RGB/RGBA | Couleur du texte (noir par défaut) |

**Retour:** `BytesIO` contenant PNG 32-bit RGBA

**Dépendances:**
- `PIL (Pillow)` - Image processing
- `os` - File operations
- `io.BytesIO` - In-memory file handling

#### **Sous-fonctions Utilitaires**

1. **`split_unit_name(nom: str, max_lines: int = 5) -> list`**
   - Split le nom selon les règles énoncées
   - Retourne liste de lignes (MAJUSCULES)

2. **`calculate_text_dimensions(lines: list, font) -> tuple`**
   - Calcule largeur max et hauteur totale du texte
   - Retourne: `(max_width, total_height, line_heights)`
   - Utilise `ImageDraw.textbbox()` pour précision

3. **`save_logo_to_file(buf: BytesIO, output_path: str) -> str`**
   - Sauvegarde le BytesIO sur disque
   - Crée répertoire s'il n'existe pas
   - Retourne le chemin du fichier sauvegardé

#### **Routes Flask**

**1. GET `/generate-logo`** - Page du générateur
```
Authentification: @login_required, @admin_required
Rendu: Template HTML avec formulaire et preview
Contexte: { unit: UniteConsulaire, unit.nom, unit.type, unit.ville }
```

**2. GET `/generate-logo/image`** - Endpoint de génération
```
Authentification: @login_required, @admin_required
Réponse: blob PNG image/png
Headers:
  - Content-Type: image/png
  - Content-Length: {size}
Erreurs:
  - 403: Pas d'unité assignée
  - 404: Unité non trouvée
  - 500: Fichiers assets manquants
```

**3. POST `/generate-logo/download`** - Téléchargement
```
Authentification: @login_required, @admin_required
Paramètres: format (png|jpg)
Réponse: Fichier téléchargeable
Naming: {unit_nom_safe}_{timestamp}.{ext}
Conversion JPG: PNG RGBA → JPG RGB (fond blanc #FFFFFF)
```

---

## 📁 Structure des Fichiers Assets

```
/static/
├── logo_assets/
│   ├── armoiries.png           # Emblème RDC (624px height)
│   ├── ligne_etat.png          # Séparateur vertical
│   └── Charte Graphique du...  # PDF de référence
│
├── font/
│   └── CooperHewitt-Bold.otf   # Police officielle
│
└── css/
    └── logo-generator.css      # Styles (optionnel)
```

**Files Critiques:**
- `armoiries.png` - **OBLIGATOIRE** (emblème RDC)
- `ligne_etat.png` - **OBLIGATOIRE** (barre verticale)
- `CooperHewitt-Bold.otf` - **OBLIGATOIRE** (police exacte)

**Spécifications des Images:**
- Format: PNG avec canal alpha (RGBA)
- Compression: Lossless PNG
- Dimensions originales: Consulter charte graphique RDC
- Couleur: Officielle selon charte gouvernementale

---

## 🎭 Interface Utilisateur (Frontend)

### **Template Admin:** `templates/admin/generate_logo.html`

**Sections:**
1. **Intro Card** - Référence à la Charte Graphique
2. **Preview Panel** (66%) - Affichage du logo généré
3. **Sidebar** (33%) - Contrôles et informations

**Fonctionnalités JavaScript:**

```javascript
// Splitting algorithm client-side
function splitUnitName(nom) {
  // Mirroir de split_unit_name Python
  // Retourne array de lignes
}

// Text preview update
function updateTextPreview() {
  // Affiche comment le nom sera disposé
}

// Logo generation
function generateLogo() {
  // Fetch GET /generate-logo/image
  // Display blob as <img src={ObjectURL}>
}

// Form submissions pour PNG/JPG
// POST /generate-logo/download avec format=png|jpg
```

**Interactions Utilisateur:**
1. Page charge → `generateLogo()` exécuté
2. Preview s'affiche automatiquement
3. Boutons "PNG" et "JPG" déclenchent téléchargement
4. Erreurs affichées inline en rouge

### **Template Agent:** `templates/agent/logo_officiel.html`

Identique à admin mais avec:
- Route différente: `agent.agent_generate_logo_image`
- Même UI/UX que admin
- Authentification: `@agent_required` ou `@login_required`

---

## 🔧 Stack Technique Complète

### **Backend**
- **Framework:** Flask 3.0+
- **ORM:** SQLAlchemy
- **Image Processing:** Pillow (PIL) 10.0+
- **Font Loading:** ImageFont (inclus Pillow)
- **Python:** 3.11+

### **Frontend**
- **HTML:** Jinja2 templates
- **CSS:** Tailwind CSS (via design system)
- **Icons:** Lucide icons (data-lucide attributes)
- **JS:** Vanilla JavaScript (pas de framework)

### **Base de Données**
- **Modèle:** UniteConsulaire
- Colonnes requises: `id`, `nom`, `type`, `ville`, `pays`

### **Security**
- CSRF Protection: `{{ csrf_token() }}` dans forms
- Rate Limiting: Standard per-user
- File Validation: Vérification existence des assets
- Error Handling: try/except + logging

---

## 📊 Flux de Données Complet

```
USER REQUEST (GET /generate-logo)
    ↓
Flask Route Handler
    ↓
Check Authentication + Unit Access
    ↓
Query UniteConsulaire
    ↓
Render Template (admin/generate_logo.html)
    ↓ [Browser loads JavaScript]
    ↓
JS calls generateLogo() on DOMContentLoaded
    ↓ [AJAX Fetch]
    ↓
GET /generate-logo/image
    ↓
Backend: generate_logo() service
    ├─ Load armoiries.png
    ├─ Load ligne_etat.png
    ├─ Load CooperHewitt-Bold.otf
    ├─ Split unit name into lines
    ├─ Calculate dimensions
    ├─ Create transparent canvas
    ├─ Composite images + text
    └─ Return PNG BytesIO
    ↓
Response: image/png blob
    ↓
Browser: Display in <img>
    ↓
USER CLICK: PNG/JPG Download Button
    ↓
POST /generate-logo/download?format=png|jpg
    ↓
Backend: Re-generate + Convert format
    ├─ If JPG: Convert RGBA → RGB (white bg)
    └─ If PNG: Return as-is
    ↓
Response: Content-Disposition: attachment
    ↓
Browser: Download file
    └─ Naming: {unit_nom}_{timestamp}.{ext}
```

---

## ⚙️ Configuration & Paramètres

### **Chemins Fichiers**
```python
armoiries_path = os.path.join(current_app.static_folder, 'logo_assets', 'armoiries.png')
ligne_etat_path = os.path.join(current_app.static_folder, 'logo_assets', 'ligne_etat.png')
font_path = os.path.join(current_app.static_folder, 'font', 'CooperHewitt-Bold.otf')
```

### **Paramètres de Génération**
```python
armoiries_height = 624      # Taille fixe armoiries
spacing = 85                # Gap armoiries ↔ ligne_etat
text_spacing = 80           # Gap ligne_etat ↔ texte
font_size = 105             # Taille du texte
line_spacing = 110          # Interligne
text_color = (0, 0, 0, 255) # Noir RGBA
```

### **Format de Sortie**
```python
# PNG (par défaut)
canvas.save(buf, format='PNG')  # RGBA preserved

# JPG (conversion)
bg = Image.new('RGB', canvas.size, (255, 255, 255))  # White bg
bg.paste(canvas, mask=canvas.split()[3])             # Paste with alpha
bg.save(buf, format='JPEG', quality=95)              # High quality
```

---

## 🚀 Implémentation d'une WebApp Indépendante

### **Minimum Viable Product (MVP)**

Pour créer une webapp **standalone** :

**1. Backend (FastAPI/Flask)**
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from services.logo_generator import generate_logo
import os

app = FastAPI()

@app.get("/api/generate-logo")
async def generate_logo_api(unit_nom: str):
    try:
        logo = generate_logo(
            unit_nom=unit_nom,
            armoiries_path="assets/armoiries.png",
            ligne_etat_path="assets/ligne_etat.png",
            font_path="assets/font.otf"
        )
        return StreamingResponse(logo, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**2. Frontend (React/Vue/Svelte)**
```javascript
// Logo Generator Component
async function generateLogo(unitName) {
  const response = await fetch(`/api/generate-logo?unit_nom=${encodeURIComponent(unitName)}`);
  const blob = await response.blob();

  // Preview
  const img = document.createElement('img');
  img.src = URL.createObjectURL(blob);

  // Download
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `logo_${sanitize(unitName)}.png`;
  a.click();
}
```

**3. Docker Containerization**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16

# Copy assets & fonts
COPY static/logo_assets /app/assets
COPY static/font /app/fonts

# Install Python deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### **Fichiers à Copier/Adapter**

```
WebApp-LogoGenerator/
├── backend/
│   ├── services/
│   │   └── logo_generator.py     ← Copier tel quel
│   ├── main.py                    ← Créer route simple
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── js/
│   │   └── logo-generator.js      ← Adapter JS
│   └── css/
│       └── styles.css
│
├── assets/
│   ├── armoiries.png              ← Copier depuis ConsulConnect
│   ├── ligne_etat.png             ← Copier depuis ConsulConnect
│   └── font/
│       └── CooperHewitt-Bold.otf  ← Copier depuis ConsulConnect
│
└── docker-compose.yml
```

---

## 🔍 Cas de Test

### **Test 1: Nom Court**
```
Input: "Ambassade"
Expected Output: 1 ligne
[Armoiries] [Ligne] AMBASSADE
```

### **Test 2: Nom Long**
```
Input: "Ambassade de la République Démocratique du Congo en France"
Expected Output: 5 lignes
1. AMBASSADE
2. DE LA RÉPUBLIQUE
3. DÉMOCRATIQUE DU
4. CONGO EN FRANCE
[Si >5 lignes: tronquer]
```

### **Test 3: Format JPG**
```
Input: PNG RGBA (transparent)
Process: Convert to RGB avec fond blanc
Output: JPG 24-bit RGB #FFFFFF background
```

### **Test 4: Dimensions Dynamiques**
```
Input: Texte de longueurs différentes
Expected: Canvas redimensionné mais proportions conservées
- Armoiries: hauteur fixe (624px)
- Largeur: Minimale pour contenir le texte
```

### **Test 5: Erreurs**
```
- Unité not found → 404
- Assets manquants → 500 + logging
- Nom vide → ValueError
- Caractères spéciaux → Convertis MAJUSCULES puis affichés
```

---

## 📝 Format de Sortie

### **PNG**
- Format: PNG 32-bit RGBA
- Fond: Transparent
- Compression: Lossless
- Chemin: `uploads/unit_logos/logo_unit_{id}_{timestamp}.png`

### **JPG**
- Format: JPEG RGB
- Fond: Blanc (#FFFFFF)
- Qualité: 95%
- Chemin: `uploads/unit_logos/logo_unit_{id}_{timestamp}.jpg`

---

## 🎯 Points Clés d'Implémentation

1. **Pillow Image Library**: Toute la génération d'image via PIL/Pillow
2. **BytesIO Buffer**: Pas d'I/O disque sauf pour téléchargement utilisateur
3. **Aspect Ratio**: Conservé pour armoiries et ligne_etat
4. **Vertical Centering**: Y positions calculées pour tous les éléments
5. **Text Measurement**: `textbbox()` pour dimensions exactes
6. **RGBA Compositing**: Images avec canaux alpha correctement gérés
7. **Format Conversion**: PNG→JPG avec background blanc
8. **Error Handling**: Try/except + fichier manquant vérification
9. **Logging**: Erreurs loggées pour debug
10. **Caching**: Pas de cache (génération rapide, <100ms)

---

## 📚 Références

- **Charte Graphique RDC**: `static/logo_assets/Charte Graphique du Gouvernement de la RDC, Feb2022.pdf`
- **Pillow Documentation**: https://python-pillow.org/
- **ImageFont API**: https://pillow.readthedocs.io/en/stable/reference/ImageFont.html

---

## ✅ Checklist de Validation

- [ ] Assets (armoiries.png, ligne_etat.png, font) présents
- [ ] Routes Flask implémentées et testées
- [ ] JavaScript frontend fonctionne et génère preview
- [ ] Download PNG et JPG fonctionnels
- [ ] Noms longs sont correctement fractionés
- [ ] Images transparentes bien composées
- [ ] Erreurs gérées avec messages utilisateur
- [ ] Performance < 500ms par génération
- [ ] CSRF tokens présents dans forms
- [ ] Authentification requise sur routes
- [ ] Fichiers sauvegardés avec noms sécurisés
- [ ] Logging actif pour erreurs/succès

---

**Dernière modification:** 2026-03-26
**Version:** 1.0
**Statut:** Documentation complète de fonctionnalité opérationnelle
