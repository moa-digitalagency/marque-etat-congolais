# Logo Generator - Quick Start Guide

## Démarrage Rapide (60 secondes)

### 1. Ouvrir Terminal
```bash
cd /Users/moadigitalagency/marque-etat-congolais
```

### 2. Lancer l'Application
```bash
./run.sh
```

Vous verrez:
```
🚀 Starting Logo Generator WebApp...
 * Running on http://127.0.0.1:5000
```

### 3. Ouvrir dans le Navigateur
```
http://localhost:5000
```

### 4. Se Connecter
**Email**: admin@rdc.gov  
**Password**: Admin123!

## Fonctionnalités Principales

### Générer un Logo
1. Cliquer sur "Générer" dans le menu
2. Sélectionner un template (Ambassade RDC, Ministère Standard, etc.)
3. Entrer le nom de l'institution
4. Cliquer "Générer"
5. Télécharger PNG ou JPG

### Créer un Compte
1. Cliquer "S'inscrire" sur la page de login
2. Entrer email et mot de passe
3. Choisir la langue (Français, Lingala, Swahili)
4. Créer le compte

### Partager un Logo
1. Générer un logo
2. Cliquer "Partager"
3. Copier le lien public
4. Partager avec d'autres

### Admin Panel
1. Se connecter avec admin@rdc.gov
2. Aller à /admin
3. Gérer les templates et utilisateurs

## Templates Disponibles

1. **Ambassade RDC** - Pour ambassades à l'étranger
2. **Ministère Standard** - Pour ministères
3. **Institution Autonome** - Pour institutions autonomes
4. **Établissement Public** - Pour établissements publics

## URLs Importantes

| URL | Description | Accès |
|-----|-------------|--------|
| http://localhost:5000 | Page d'accueil | Public (redirect login) |
| /auth/login | Connexion | Public |
| /auth/register | Enregistrement | Public |
| /dashboard | Tableau de bord | Utilisateur connecté |
| /generate | Générateur de logo | Utilisateur connecté |
| /admin | Panel administration | Admin uniquement |

## Arrêter l'Application

Dans le terminal où l'app s'exécute:
```bash
CTRL + C
```

## Redémarrer PostgreSQL (si besoin)

```bash
# Arrêter
brew services stop postgresql@16

# Redémarrer
brew services start postgresql@16

# Vérifier
brew services list | grep postgresql
```

## Accéder à la Base de Données

```bash
psql -U logo_user -d logo_generator_db
```

Commandes utiles:
```sql
-- Voir les utilisateurs
SELECT email, role FROM "user";

-- Voir les templates
SELECT name, institution_type FROM template;

-- Voir les logos générés
SELECT institution_name, created_at FROM logo_generation;
```

## Créer un Nouvel Admin

```bash
cd /Users/moadigitalagency/marque-etat-congolais
source venv/bin/activate
export LC_ALL=en_US.UTF-8 && export LANG=en_US.UTF-8 && export PYTHONIOENCODING=utf-8

python << 'PYTHON'
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    user = User(
        email="newadmin@rdc.gov",
        full_name="New Admin",
        role="admin",
        language="fr",
        is_active=True
    )
    user.set_password("YourPassword123!")
    db.session.add(user)
    db.session.commit()
    print("Admin créé: newadmin@rdc.gov")
PYTHON
```

## Dépannage

### L'app ne démarre pas
1. Vérifier PostgreSQL: `brew services list | grep postgresql`
2. Relancer PostgreSQL: `brew services restart postgresql@16`
3. Vérifier le port: `lsof -i :5000`

### Erreur de base de données
```bash
# Tester la connexion
psql -U logo_user -d logo_generator_db -c "SELECT 1;"
```

### Pages blanches ou erreur 500
1. Vérifier les logs dans le terminal
2. Vérifier que Flask-WTF est chargé
3. Vérifier les variables d'environnement

### Problème de caractères accentués
Toujours lancer avec:
```bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8
./run.sh
```

## Informations Techniques

- **Framework**: Flask 3.0.0
- **Base de données**: PostgreSQL 16.13
- **ORM**: SQLAlchemy 2.0.48
- **Python**: 3.13
- **Port**: 5000 (localhost)
- **Mode**: Développement (debug activé)

## Support Multilingue

L'interface supporte:
- Français (fr) - Défaut
- Lingala
- Swahili

Sélectionner lors de l'enregistrement

## Fichiers Importants

- `main.py` - Point d'entrée de l'application
- `app.py` - Configuration Flask
- `.env` - Variables d'environnement
- `run.sh` - Script de démarrage
- `init_db.py` - Script d'initialisation DB
- `models/` - Modèles de données
- `routes/` - Endpoints API
- `templates/` - Templates HTML
- `statics/` - Ressources statiques

## Support

Pour les problèmes:
1. Vérifier VERIFICATION_CHECKLIST.md
2. Vérifier DEPLOYMENT_SUMMARY.md
3. Vérifier les logs du terminal
4. Vérifier la base de données

---

**Prêt à générer des logos? Lancez: `./run.sh`**

