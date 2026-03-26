# Logo Generator WebApp - Design Document

**Date**: 2026-03-26
**Version**: 1.0
**Status**: Approved

---

## 📋 Vue d'ensemble

Webapp Flask pour générer des **logos officiels** de toutes les institutions gouvernementales de la RDC selon la charte graphique officielle (février 2022).

**Utilisateurs finaux**:
- **Utilisateurs publics**: Créent/téléchargent/partagent logos (compte requis)
- **Administrateurs**: Gèrent templates et voient statistiques

**Capacités**:
- Génération PNG transparent + JPG fond blanc
- Historique complet des générations par utilisateur
- Partage via liens publics (accès sans login)
- Templates prédéfinis (Ambassade, Ministère, etc.)
- Support multi-langue (FR, Lingala, Swahili)

---

## 🏗️ Architecture

### Approche Choisie: Monolithe Flask Classique

**Justification**:
- MVP simple (pas de microservices nécessaires)
- Équipe solo/petite
- Peut être refactorisé plus tard en Blueprints modulaires

### Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **Framework** | Flask 3.0+ |
| **ORM** | SQLAlchemy 2.0+ |
| **BD** | PostgreSQL 14+ |
| **Image Processing** | Pillow (PIL) 10.0+ |
| **Frontend** | HTML/Jinja2 + Tailwind CSS + JS vanilla |
| **Design System** | Couleurs/fonts RDC (design-system-marque-etat-congolais) |
| **Auth** | Flask-Login + bcrypt |
| **I18n** | JSON files (fr.json, lingala.json, swahili.json) |

---

## 📁 Structure des Dossiers

```
logo-generator-app/
│
├── algorithms/              # Algorithmes métier
│   └── text_splitter.py     # split_unit_name() logic
│
├── config/                  # Configuration
│   ├── __init__.py
│   ├── settings.py          # Config app (DB, SECRET_KEY, etc.)
│   └── constants.py         # Constantes (tailles, spacing, etc.)
│
├── docs/                    # Documentation
│   ├── SETUP.md
│   ├── API.md
│   └── specs/
│       └── 2026-03-26-logo-generator-design.md
│
├── lang/                    # Traductions
│   ├── fr.json              # Français
│   ├── lingala.json         # Lingala
│   └── swahili.json         # Swahili
│
├── models/                  # SQLAlchemy Models
│   ├── __init__.py
│   ├── user.py              # User, Role
│   ├── template.py          # Template
│   ├── logo.py              # LogoGeneration
│   └── shared_link.py       # SharedLink
│
├── routes/                  # Flask Blueprints
│   ├── __init__.py
│   ├── auth.py              # /auth/* routes
│   ├── public.py            # /generate, /share/{token}
│   ├── dashboard.py         # /dashboard, /history
│   ├── api.py               # /api/* (JSON endpoints)
│   └── admin.py             # /admin/* (templates, stats)
│
├── scripts/                 # Utilitaires CLI
│   ├── __init__.py
│   └── seed_templates.py    # Pré-créer templates
│
├── security/                # Sécurité
│   ├── __init__.py
│   └── decorators.py        # @login_required, @admin_required
│
├── services/                # Logique métier
│   ├── __init__.py
│   ├── logo_generator.py    # Service Pillow (genération)
│   ├── auth_service.py      # Hashing, verification
│   ├── template_service.py  # CRUD templates
│   ├── share_service.py     # Liens publics
│   └── i18n_service.py      # Traductions
│
├── statics/                 # Assets
│   ├── css/
│   │   ├── tokens.css       # (copié du design-system)
│   │   ├── components.css   # (copié du design-system)
│   │   └── logo-gen.css     # Custom styles
│   ├── js/
│   │   ├── logo-generator.js
│   │   └── share.js
│   ├── img/
│   ├── uploads/logos/       # PNG/JPG générés
│   └── logo_assets/ → /Users/moadigitalagency/marque-etat-congolais/logo_assets
│
├── templates/               # Jinja2
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── public/
│   │   ├── generate.html
│   │   └── share.html
│   ├── dashboard/
│   │   ├── history.html
│   │   └── download.html
│   └── admin/
│       ├── templates.html
│       ├── users.html
│       └── stats.html
│
├── utils/                   # Utilitaires
│   ├── __init__.py
│   ├── file_helpers.py
│   ├── validators.py
│   └── decorators.py
│
├── app.py                   # Point d'entrée Flask
├── init_db.py               # Initialisation BD + fixtures
├── requirements.txt         # Dépendances
├── .env.example
├── wsgi.py                  # Production (gunicorn)
└── docker-compose.yml
```

---

## 🗄️ Modèles de Base de Données

### **User**
```sql
CREATE TABLE user (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  role ENUM('user', 'admin') DEFAULT 'user',
  language VARCHAR(20) DEFAULT 'fr',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  INDEX(email)
);
```

### **Template**
```sql
CREATE TABLE template (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  institution_type VARCHAR(100),
  created_by_admin INTEGER REFERENCES user(id),
  params JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE
);
```

### **LogoGeneration**
```sql
CREATE TABLE logo_generation (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
  template_id INTEGER NOT NULL REFERENCES template(id),
  institution_name VARCHAR(255) NOT NULL,
  language VARCHAR(20) DEFAULT 'fr',
  file_path_png VARCHAR(500),
  file_path_jpg VARCHAR(500),
  preview_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  INDEX(user_id, created_at DESC)
);
```

### **SharedLink**
```sql
CREATE TABLE shared_link (
  id SERIAL PRIMARY KEY,
  logo_id INTEGER NOT NULL REFERENCES logo_generation(id) ON DELETE CASCADE,
  token_public VARCHAR(255) UNIQUE NOT NULL,
  created_by INTEGER REFERENCES user(id),
  expires_at TIMESTAMP NULL,
  view_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(token_public)
);
```

---

## 🛣️ Routes & Flows

### **Authentication Routes**
```
GET  /auth/login           → Formulaire login
POST /auth/login           → Traite login
GET  /auth/register        → Formulaire registration
POST /auth/register        → Crée user
GET  /auth/logout          → Détruit session
GET  /auth/profile         → Profil user
POST /auth/profile         → MAJ profil
```

### **Public Routes**
```
GET  /generate             → Form + template selector + live preview
POST /api/generate         → Génère image (AJAX)
POST /api/download         → Télécharge PNG/JPG
GET  /share/{token}        → Affichage public (pas login requis)
POST /api/share            → Crée SharedLink
```

### **Dashboard Routes**
```
GET  /dashboard            → Home
GET  /dashboard/history    → Historique logos (pagination)
GET  /dashboard/history/{id} → Détail logo
DELETE /dashboard/{id}     → Supprime logo
```

### **Admin Routes**
```
GET  /admin/templates      → List templates
POST /admin/templates      → Create template
PUT  /admin/templates/{id} → Modify template
DELETE /admin/templates/{id} → Delete template
GET  /admin/stats          → Dashboard stats
GET  /admin/users          → Gestion users
```

### **API Endpoints (JSON)**
```
GET  /api/templates        → List templates
POST /api/generate         → Generate logo image
POST /api/download         → Download PNG/JPG
POST /api/share            → Create share link
GET  /api/logos            → List user's logos
```

---

## 🎨 Frontend Architecture

### **Base Template (base.html)**
- Navbar avec branding RDC
- Auth links (login/register/profile)
- Flash messages (erreurs/succès)
- Footer
- Design-system colors (rdc-bleu, rdc-rouge, etc.)

### **Page Génération (generate.html)**
- **Gauche (66%)**: Preview canvas (logo généré)
- **Droite (33%)**: Formulaire
  - Template selector (dropdown)
  - Institution name input + text preview (split en lignes)
  - Language selector (FR/Lingala/Swahili)
  - Bouton "Générer"
  - Download buttons (PNG/JPG) + Share button

### **Dashboard (history.html)**
- Grille de logos générés par l'user
- Recherche + filtre
- Boutons download/share pour chaque logo
- Pagination

### **Admin (templates.html)**
- CRUD templates (prédéfinis)
- Paramètres modifiables: armoiries_height, font_size, spacing, etc.
- Statistiques (logos générés, institutions populaires, etc.)

---

## 🔐 Sécurité

### **Authentication**
- Flask-Login + sessions
- Passwords hashés (bcrypt)
- @login_required + @admin_required decorators

### **Authorization**
- Public users → can generate, download, share
- Admin users → can manage templates, view stats
- Shared links → public access (no login required)

### **File Handling**
- Images sauvegardées dans `uploads/logos/`
- Noms fichiers sécurisés (UUID + timestamp)
- Validation taille/format fichier

### **CSRF Protection**
- {{ csrf_token() }} dans toutes les forms

---

## 🎯 Flux Utilisateur Principal

```
1. USER SIGNUP
   Register → email/password → DB user(role='user')

2. USER LOGIN
   Login → session créée

3. GÉNÉRATION LOGO
   GET /generate
   → Affiche form + live preview
   → User choisit template + saisit nom institution
   → POST /api/generate
   → Backend: LogoGeneratorService.generate_logo()
   → Sauve PNG + JPG, retourne preview_url
   → JS affiche preview + download buttons

4. TÉLÉCHARGEMENT
   Click "Download PNG" → POST /api/download
   → File téléchargé

5. PARTAGE PUBLIC
   Click "Share" → POST /api/share
   → Token créé, lien /share/{token} généré
   → URL copiée clipboard
   → Quelqu'un accède lien → affiche logo (pas login requis)

6. ADMIN TEMPLATES
   Admin → /admin/templates
   → Voir/modifier params pour templates
   → Affecte tous les logos futurs
```

---

## 📊 Modèles de Données Détaillés

### **Template Params (JSON)**
```json
{
  "armoiries_height": 624,
  "spacing": 85,
  "text_spacing": 80,
  "font_size": 105,
  "line_spacing": 110,
  "text_color": [0, 0, 0, 255]
}
```

### **LogoGeneration Response (API)**
```json
{
  "id": 123,
  "institution_name": "Ambassade de la RDC en France",
  "template": { "id": 1, "name": "Ambassade RDC" },
  "preview_url": "/uploads/logos/123_preview.png",
  "png_url": "/uploads/logos/123.png",
  "jpg_url": "/uploads/logos/123.jpg",
  "created_at": "2026-03-26T10:30:00Z"
}
```

---

## 🌍 Multi-Langue Support

### **Structure i18n**
```
lang/
  ├── fr.json          # Français
  ├── lingala.json     # Lingala
  └── swahili.json     # Swahili
```

### **Usage en Templates**
```html
<button>{{ _('common.generate') }}</button>
```

### **User Language**
- Défaut: Français (fr)
- Configurable dans profil utilisateur
- Affecte texte de l'UI seulement
- Nom institution gardé tel que saisi

---

## 🧪 Cas de Test Critiques

### **Test 1: Génération Simple**
- Input: "Ambassade"
- Output: Logo 1 ligne + PNG + JPG ✓

### **Test 2: Nom Long**
- Input: "Ambassade de la République Démocratique du Congo en France"
- Output: Logo 5 lignes (splitted) + PNG + JPG ✓

### **Test 3: Partage Public**
- Generate logo → Create share link → Access without login ✓

### **Test 4: Admin Templates**
- Modify template params → Re-generate logo → see new params applied ✓

### **Test 5: Multi-Langue**
- User sélectionne Lingala → interface change de langue ✓

---

## 📈 Performance & Scalabilité

- **Logo generation**: < 200ms (Pillow fast)
- **Caching**: Pas nécessaire (génération rapide)
- **Uploads**: Limités à 5MB par fichier
- **DB indexes**: user_id, email, logo creation_date

---

## 🚀 Déploiement

### **Production**
- Gunicorn + WSGI
- Docker container
- PostgreSQL managed
- Static files (CSS/JS) servies par CDN ou nginx

### **Environment Variables**
```
DATABASE_URL=postgresql://user:pass@localhost/logo_db
SECRET_KEY=xxxxx
FLASK_ENV=production
```

---

## ✅ Checklist de Validation

- [ ] Tables BD créées (init_db.py)
- [ ] Models Flask définis
- [ ] Routes authentification fonctionnelles
- [ ] Service LogoGeneratorService implémenté
- [ ] Routes API generate/download/share testées
- [ ] Frontend generate.html + dashboard.html
- [ ] JS text-splitting algorithm
- [ ] Admin templates CRUD
- [ ] Multi-langue (3 langues)
- [ ] Shared links publics
- [ ] Design-system colors intégrés
- [ ] Tests unitaires services
- [ ] Tests intégration routes
- [ ] Performance < 500ms

---

**Approuvé par**: Utilisateur
**Prêt pour**: Implementation Planning
