# Logo Generator WebApp - RDC

> Application web pour la génération et la gestion de logos officiels des institutions de la République Démocratique du Congo

## Status: ✅ DÉPLOYÉ

L'application est complètement déployée et prête pour les tests.

---

## Démarrage Rapide

### 1. Lancer l'application
```bash
cd /Users/moadigitalagency/marque-etat-congolais
./run.sh
```

### 2. Ouvrir dans le navigateur
```
http://localhost:5000
```

### 3. Se connecter
- Email: `admin@rdc.gov`
- Password: `Admin123!`

---

## Documentation

### Pour les Développeurs
- **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage en 60 secondes
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)** - Résumé du déploiement

### Pour les Testeurs/QA
- **[VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md)** - Checklist complète
- **[DEPLOYMENT_REPORT.md](DEPLOYMENT_REPORT.md)** - Rapport final

---

## Fonctionnalités Principales

### Génération de Logos
- Selection de template (4 modèles disponibles)
- Saisie du nom de l'institution
- Prévisualisation en temps réel
- Téléchargement PNG/JPG

### Gestion Utilisateur
- Inscription/Connexion
- Support multilingue (FR, Lingala, Swahili)
- Dashboard personnalisé
- Historique des logos

### Partage
- Génération de liens publics partageables
- Accès sans authentification
- Compteur de vues

### Administration
- Gestion des templates
- Gestion des utilisateurs
- Statistiques d'utilisation

---

## Templates Disponibles

1. **Ambassade RDC** - Pour ambassades à l'étranger
2. **Ministère Standard** - Pour ministères
3. **Institution Autonome** - Pour institutions autonomes
4. **Établissement Public** - Pour établissements publics

---

## Architecture Technique

### Stack Technologique
- **Backend**: Flask 3.0.0
- **Base de Données**: PostgreSQL 16.13
- **ORM**: SQLAlchemy 2.0.48
- **Authentification**: Flask-Login + bcrypt
- **Protection CSRF**: Flask-WTF
- **Python**: 3.13

### Structure du Projet
```
.
├── main.py              # Point d'entrée
├── app.py              # Configuration Flask
├── init_db.py          # Initialisation base de données
├── models/             # Modèles SQLAlchemy
├── routes/             # Blueprints/endpoints
├── templates/          # Templates HTML
├── static/             # Ressources statiques
├── config/             # Configuration
├── services/           # Services métier
├── algorithms/         # Algorithmes
└── .env               # Variables d'environnement
```

---

## Configuration

### Fichiers Clés
- `.env` - Variables d'environnement
- `config/settings.py` - Configuration Flask
- `init_db.py` - Seed de la base de données

### Variables d'Environnement
```bash
# Database
DATABASE_URL=postgresql://logo_user:logo_password123@localhost/logo_generator_db

# Flask
FLASK_APP=main.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production-12345678

# Admin
ADMIN_EMAIL=admin@rdc.gov
ADMIN_PASSWORD=Admin123!
ADMIN_FULL_NAME=Administrator RDC

# Upload
UPLOAD_FOLDER=/Users/moadigitalagency/marque-etat-congolais/statics/uploads/logos
MAX_CONTENT_LENGTH=5242880
```

---

## API Endpoints

### Authentification
- `GET/POST /auth/login` - Connexion
- `GET/POST /auth/register` - Enregistrement
- `GET /auth/logout` - Déconnexion

### Public
- `GET /` - Redirection vers login
- `GET /share/<token>` - Accès logo partagé

### Utilisateur (authentifié)
- `GET /dashboard` - Tableau de bord
- `GET /generate` - Générateur de logo
- `POST /api/generate` - AJAX génération
- `GET /download/<id>/<format>` - Téléchargement

### Admin
- `GET /admin` - Panel admin
- `GET/POST /admin/templates` - Gestion templates
- `GET/POST /admin/users` - Gestion utilisateurs

---

## Credentials par Défaut

### Admin
- **Email**: admin@rdc.gov
- **Password**: Admin123!
- **Rôle**: admin

### Nouveau Compte
1. Aller à `/auth/register`
2. Créer un compte utilisateur
3. Se connecter avec les nouvelles credentials

---

## Commandes Utiles

### Lancer l'application
```bash
./run.sh
```

### Arrêter l'application
```bash
CTRL + C
```

### Gérer PostgreSQL
```bash
# Démarrer
brew services start postgresql@16

# Arrêter
brew services stop postgresql@16

# Redémarrer
brew services restart postgresql@16

# Statut
brew services list | grep postgresql
```

### Accéder à la base de données
```bash
psql -U logo_user -d logo_generator_db
```

### Réinitialiser la base de données
```bash
source venv/bin/activate
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8
python init_db.py
```

---

## Dépannage

### Application ne démarre pas
1. Vérifier PostgreSQL: `brew services list | grep postgresql`
2. Relancer PostgreSQL: `brew services restart postgresql@16`
3. Vérifier le port: `lsof -i :5000`

### Erreur de connexion base de données
```bash
psql -U logo_user -d logo_generator_db -c "SELECT 1;"
```

### Erreurs d'encodage (caractères accentués)
```bash
# S'assurer que l'environnement est configuré
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export PYTHONIOENCODING=utf-8
./run.sh
```

### Port 5000 déjà utilisé
```bash
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

## Tests

### Tester la génération de logo
1. Se connecter
2. Aller à `/generate`
3. Sélectionner un template
4. Entrer le nom de l'institution
5. Cliquer "Générer"
6. Télécharger le logo

### Tester le partage
1. Générer un logo
2. Cliquer "Partager"
3. Copier le lien
4. Ouvrir dans un navigateur privé
5. Vérifier l'accès sans authentification

### Tester l'admin panel
1. Se connecter avec admin@rdc.gov
2. Aller à `/admin`
3. Naviguer les sections (Templates, Users)

---

## Fichiers de Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Ce fichier - Overview général |
| [QUICKSTART.md](QUICKSTART.md) | Démarrage rapide (60 sec) |
| [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) | Résumé du déploiement |
| [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) | Checklist complète |
| [DEPLOYMENT_REPORT.md](DEPLOYMENT_REPORT.md) | Rapport final détaillé |

---

## Support et Contribution

### Signaler un Bug
1. Vérifier la documentation
2. Consulter VERIFICATION_CHECKLIST.md
3. Vérifier les logs
4. Redémarrer PostgreSQL

### Ajouter une Fonctionnalité
1. Créer une branche
2. Développer et tester
3. Documenter
4. Créer un PR

---

## Notes Importantes

### Sécurité
- SECRET_KEY est pour développement uniquement - À CHANGER EN PRODUCTION
- Passwords sont hachés avec bcrypt
- CSRF protection est activée
- Sessions sont HttpOnly + SameSite=Lax

### Performance
- Mode debug est activé (À désactiver en production)
- Base de données echo est activé (À désactiver en production)
- Pas de cache - À implémenter en production

### Compatibilité
- macOS 22.6.0 ou supérieur
- PostgreSQL 16.13 recommandé
- Python 3.13+ requis
- Support multilingue: FR, Lingala, Swahili

---

## Informations de Contact

- **Équipe**: Moa Digital Agency
- **Localisation**: RDC
- **Projet**: Marque de l'État Congolais

---

## Licence

Copyright RDC - Tous droits réservés

---

## Historique des Déploiements

| Date | Version | Status | Notes |
|------|---------|--------|-------|
| 27-03-2026 | 1.0 | ✅ Déployé | Déploiement initial complet |

---

**Dernière mise à jour**: 27 Mars 2026  
**Version**: 1.0  
**Status**: ✅ Prêt pour tests

---

**Pour démarrer**: `./run.sh` puis `http://localhost:5000`

