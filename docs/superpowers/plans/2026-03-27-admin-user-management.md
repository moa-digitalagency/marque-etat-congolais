# Admin User Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable admin users to create new admin accounts and manage user roles and statuses from a dedicated admin panel.

**Architecture:** Create an admin-only section in the application with routes for viewing users, creating new accounts, and managing roles. Protect all admin routes with role-based access control. Implement both page-based and API-based operations for flexibility.

**Tech Stack:** Flask, SQLAlchemy, Jinja2 templates, CSS design system

---

## File Structure

**Files to create:**
- `templates/admin/users.html` - Admin user management page
- `templates/admin/create_user.html` - Form for creating new admin users

**Files to modify:**
- `routes/admin.py` - Add admin routes (currently empty)
- `routes/api.py` - Add API endpoints for user management
- `services/auth_service.py` - Add user management methods
- `templates/base.html` - Add admin navigation link
- `templates/dashboard/home.html` - Add admin quick link (if space permits)

**Security:**
- All admin routes check `current_user.role == 'admin'`
- CSRF protection on all forms
- Rate limiting on user creation (future enhancement)

---

## Task 1: Create Admin User List Page

**Files:**
- Create: `templates/admin/users.html`
- Modify: `routes/admin.py` - Add GET route for user list

- [ ] **Step 1: Add route to display admin users page**

Modify `routes/admin.py`:
```python
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates')

def admin_required(f):
    """Decorator to require admin role"""
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def users():
    """Display user management page"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users, current_user=current_user)
```

- [ ] **Step 2: Create admin/users.html template**

Create `templates/admin/users.html`:
```html
{% extends "base.html" %}

{% block title %}Gestion des Utilisateurs - Admin{% endblock %}

{% block content %}
<div style="max-width: 1400px; margin: 0 auto; padding: var(--space-8) var(--space-4);">
  <!-- Page Header -->
  <div style="margin-bottom: var(--space-8); display: flex; justify-content: space-between; align-items: center;">
    <div>
      <h1 style="color: var(--text-primary); margin-bottom: var(--space-2);">Gestion des Utilisateurs</h1>
      <p style="color: var(--text-secondary); margin-bottom: 0;">Créez et gérez les comptes utilisateurs</p>
    </div>
    <a href="{{ url_for('admin.create_user') }}" class="btn btn-primary" style="white-space: nowrap;">
      + Créer un Utilisateur
    </a>
  </div>

  <!-- Users Table -->
  <div class="card" style="overflow: hidden;">
    <div style="overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: var(--bg-subtle); border-bottom: 1px solid var(--border-soft);">
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Email</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Nom Complet</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Rôle</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Statut</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Créé le</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Actions</th>
          </tr>
        </thead>
        <tbody>
          {% for user in users %}
          <tr style="border-bottom: 1px solid var(--border-soft); hover_background: var(--bg-subtle);">
            <td style="padding: var(--space-4); color: var(--text-primary);">{{ user.email }}</td>
            <td style="padding: var(--space-4); color: var(--text-primary);">{{ user.full_name or 'N/A' }}</td>
            <td style="padding: var(--space-4);">
              <span style="display: inline-block; padding: var(--space-2) var(--space-3); border-radius: var(--radius-sm); font-size: var(--text-sm); font-weight: 500; {% if user.role == 'admin' %}background-color: rgba(30, 58, 138, 0.1); color: var(--primary);{% else %}background-color: rgba(107, 114, 128, 0.1); color: #6b7280;{% endif %}">
                {{ 'Admin' if user.role == 'admin' else 'Utilisateur' }}
              </span>
            </td>
            <td style="padding: var(--space-4);">
              <span style="display: inline-block; padding: var(--space-2) var(--space-3); border-radius: var(--radius-sm); font-size: var(--text-sm); font-weight: 500; {% if user.is_active %}background-color: rgba(34, 197, 94, 0.1); color: var(--color-success);{% else %}background-color: rgba(239, 68, 68, 0.1); color: var(--color-error);{% endif %}">
                {{ 'Actif' if user.is_active else 'Inactif' }}
              </span>
            </td>
            <td style="padding: var(--space-4); color: var(--text-secondary); font-size: var(--text-sm);">{{ user.created_at.strftime('%d %b %Y') }}</td>
            <td style="padding: var(--space-4);">
              <button onclick="openUserModal({{ user.id }}, '{{ user.email }}', '{{ user.role }}', {{ user.is_active|lower }})" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm);">
                Modifier
              </button>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>

    {% if not users %}
    <div style="padding: var(--space-8); text-align: center; color: var(--text-secondary);">
      <p>Aucun utilisateur trouvé</p>
    </div>
    {% endif %}
  </div>
</div>

<!-- Edit User Modal -->
<div id="editUserModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 1000; align-items: center; justify-content: center;">
  <div class="card" style="width: 90%; max-width: 500px; padding: var(--space-8);">
    <h2 style="margin-bottom: var(--space-6);">Modifier l'Utilisateur</h2>

    <form id="editUserForm" style="display: flex; flex-direction: column; gap: var(--space-4);">
      <input type="hidden" id="userId" name="user_id">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

      <div>
        <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Email</label>
        <input type="text" id="userEmail" readonly style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); background-color: var(--bg-subtle); color: var(--text-secondary);">
      </div>

      <div>
        <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Rôle</label>
        <select id="userRole" name="role" style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); width: 100%;">
          <option value="user">Utilisateur</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <div>
        <label style="display: flex; align-items: center; gap: var(--space-2); font-weight: 500;">
          <input type="checkbox" id="userActive" name="is_active" style="width: 18px; height: 18px;">
          <span>Compte actif</span>
        </label>
      </div>

      <div style="display: flex; gap: var(--space-4); margin-top: var(--space-4);">
        <button type="button" onclick="closeEditUserModal()" class="btn btn-outline" style="flex: 1;">Annuler</button>
        <button type="submit" class="btn btn-primary" style="flex: 1;">Enregistrer</button>
      </div>
    </form>
  </div>
</div>

<script>
function openUserModal(userId, email, role, isActive) {
  document.getElementById('userId').value = userId;
  document.getElementById('userEmail').value = email;
  document.getElementById('userRole').value = role;
  document.getElementById('userActive').checked = isActive;
  document.getElementById('editUserModal').style.display = 'flex';
}

function closeEditUserModal() {
  document.getElementById('editUserModal').style.display = 'none';
}

document.getElementById('editUserForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const userId = document.getElementById('userId').value;
  const role = document.getElementById('userRole').value;
  const isActive = document.getElementById('userActive').checked;

  const response = await fetch(`/api/admin/users/${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
    },
    body: JSON.stringify({
      role: role,
      is_active: isActive
    })
  });

  if (response.ok) {
    location.reload();
  } else {
    alert('Erreur lors de la modification de l\'utilisateur');
  }
});

// Close modal on background click
document.getElementById('editUserModal').addEventListener('click', function(e) {
  if (e.target === this) closeEditUserModal();
});
</script>

<style>
table tr:hover {
  background-color: var(--bg-subtle);
}
</style>
{% endblock %}
```

- [ ] **Step 3: Register admin blueprint in app**

Modify `app.py` (or main Flask app initialization file):
```python
from routes.admin import admin_bp

app.register_blueprint(admin_bp)
```

- [ ] **Step 4: Test the page loads**

Navigate to `/admin/users` in browser after logging in as admin.
Expected: See page with list of users (if any exist) and "Create User" button visible.

- [ ] **Step 5: Commit**

```bash
git add templates/admin/users.html routes/admin.py
git commit -m "feat: add admin user management page with user list"
```

---

## Task 2: Create User Creation Page and Form

**Files:**
- Create: `templates/admin/create_user.html`
- Modify: `routes/admin.py` - Add GET/POST route for user creation

- [ ] **Step 1: Add route for creating user**

Modify `routes/admin.py`:
```python
from services.auth_service import AuthService

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'user')
        language = request.form.get('language', 'fr')

        # Validation
        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return redirect(url_for('admin.create_user'))

        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'error')
            return redirect(url_for('admin.create_user'))

        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return redirect(url_for('admin.create_user'))

        if role not in ['user', 'admin']:
            flash('Rôle invalide', 'error')
            return redirect(url_for('admin.create_user'))

        try:
            user = AuthService.register_user(
                email=email,
                password=password,
                full_name=full_name,
                language=language,
                role=role
            )
            flash(f'Utilisateur {email} créé avec succès', 'success')
            return redirect(url_for('admin.users'))
        except ValueError as e:
            flash(str(e), 'error')

    return render_template('admin/create_user.html')
```

- [ ] **Step 2: Create create_user.html template**

Create `templates/admin/create_user.html`:
```html
{% extends "base.html" %}

{% block title %}Créer un Utilisateur - Admin{% endblock %}

{% block content %}
<div style="max-width: 600px; margin: 0 auto; padding: var(--space-8) var(--space-4);">
  <!-- Page Header -->
  <div style="margin-bottom: var(--space-8);">
    <a href="{{ url_for('admin.users') }}" style="color: var(--primary); text-decoration: none; margin-bottom: var(--space-4); display: inline-block;">← Retour</a>
    <h1 style="color: var(--text-primary); margin-bottom: var(--space-2);">Créer un Utilisateur</h1>
    <p style="color: var(--text-secondary); margin-bottom: 0;">Ajoutez un nouveau compte utilisateur ou administrateur</p>
  </div>

  <!-- Flash Messages -->
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
      <div style="margin-bottom: var(--space-4); padding: var(--space-4); border-radius: var(--radius-lg); {% if category == 'error' %}background-color: rgba(239, 68, 68, 0.1); color: var(--color-error); border-left: 4px solid var(--color-error);{% else %}background-color: rgba(34, 197, 94, 0.1); color: var(--color-success); border-left: 4px solid var(--color-success);{% endif %}">
        {{ message }}
      </div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <!-- Form -->
  <div class="card">
    <form method="POST" style="display: flex; flex-direction: column; gap: var(--space-6);">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

      <!-- Email -->
      <div>
        <label for="email" class="form-label">
          Email <span style="color: var(--rdc-rouge);">*</span>
        </label>
        <input type="email" id="email" name="email" required class="input" style="width: 100%;" placeholder="utilisateur@example.com">
        <p class="form-hint">L'adresse email doit être unique</p>
      </div>

      <!-- Full Name -->
      <div>
        <label for="full_name" class="form-label">Nom Complet</label>
        <input type="text" id="full_name" name="full_name" class="input" style="width: 100%;" placeholder="Jean Dupont">
        <p class="form-hint">Facultatif - Sera affiché dans l'interface</p>
      </div>

      <!-- Password -->
      <div>
        <label for="password" class="form-label">
          Mot de Passe <span style="color: var(--rdc-rouge);">*</span>
        </label>
        <input type="password" id="password" name="password" required minlength="6" class="input" style="width: 100%;" placeholder="Minimum 6 caractères">
        <p class="form-hint">Minimum 6 caractères</p>
      </div>

      <!-- Confirm Password -->
      <div>
        <label for="password_confirm" class="form-label">
          Confirmer le Mot de Passe <span style="color: var(--rdc-rouge);">*</span>
        </label>
        <input type="password" id="password_confirm" name="password_confirm" required minlength="6" class="input" style="width: 100%;" placeholder="Répétez le mot de passe">
      </div>

      <!-- Role -->
      <div>
        <label for="role" class="form-label">Rôle</label>
        <select id="role" name="role" class="input select" style="width: 100%;">
          <option value="user">Utilisateur Standard</option>
          <option value="admin">Administrateur</option>
        </select>
        <p class="form-hint">Les administrateurs peuvent gérer les utilisateurs et les logos</p>
      </div>

      <!-- Language -->
      <div>
        <label for="language" class="form-label">Langue Préférée</label>
        <select id="language" name="language" class="input select" style="width: 100%;">
          <option value="fr">🇨🇩 Français</option>
          <option value="lingala">🗣️ Lingala</option>
          <option value="swahili">🗣️ Swahili</option>
        </select>
      </div>

      <!-- Buttons -->
      <div style="display: flex; gap: var(--space-4); margin-top: var(--space-6);">
        <a href="{{ url_for('admin.users') }}" class="btn btn-outline" style="flex: 1; text-align: center; text-decoration: none;">Annuler</a>
        <button type="submit" class="btn btn-primary" style="flex: 1;">Créer l'Utilisateur</button>
      </div>
    </form>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 2b: Update AuthService to support role parameter**

Modify `services/auth_service.py`:
```python
@staticmethod
def register_user(email, password, full_name=None, language='fr', role='user'):
    """Register a new user"""
    from models.user import User

    if User.query.filter_by(email=email).first():
        raise ValueError('Email déjà utilisé')

    user = User(email=email, full_name=full_name, language=language, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
```

- [ ] **Step 3: Add import statement at top of admin.py**

```python
from flask import request
```

- [ ] **Step 4: Test user creation**

1. Navigate to `/admin/users/create`
2. Fill in form with test data
3. Submit form
Expected: User created, redirected to users list, success message shown

- [ ] **Step 5: Commit**

```bash
git add templates/admin/create_user.html routes/admin.py services/auth_service.py
git commit -m "feat: add user creation form for admins"
```

---

## Task 3: Add User Update API Endpoint

**Files:**
- Modify: `routes/api.py` - Add endpoint for updating user role/status

- [ ] **Step 1: Add admin user update endpoint**

Modify `routes/api.py` (add new route):
```python
from flask import request, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.database import db

@api_bp.route('/admin/users/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user role and status (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'role' in data:
        if data['role'] not in ['user', 'admin']:
            return jsonify({'error': 'Rôle invalide'}), 400
        user.role = data['role']

    if 'is_active' in data:
        user.is_active = data['is_active']

    db.session.commit()

    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'is_active': user.is_active
    })
```

- [ ] **Step 2: Test the API endpoint**

Using browser dev tools or curl:
```bash
curl -X POST http://localhost:5000/api/admin/users/1 \
  -H "Content-Type: application/json" \
  -d '{"role": "admin", "is_active": true}'
```

Expected: Returns JSON with updated user data, HTTP 200

- [ ] **Step 3: Commit**

```bash
git add routes/api.py
git commit -m "feat: add API endpoint for updating user role and status"
```

---

## Task 4: Add Admin Link to Navigation

**Files:**
- Modify: `templates/base.html` - Add admin link to sidebar/header

- [ ] **Step 1: Find user profile section in base.html**

Search for the user profile button section that was added previously.

- [ ] **Step 2: Add admin link before logout**

In the user profile dropdown menu (before logout), add:
```html
{% if current_user.role == 'admin' %}
<a href="{{ url_for('admin.users') }}" style="display: block; padding: var(--space-3); color: var(--primary); text-decoration: none; border-bottom: 1px solid var(--border-soft);">
  <svg style="width: 16px; height: 16px; display: inline; margin-right: var(--space-2);" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10.5 1.5H3.75A2.25 2.25 0 001.5 3.75v12.5A2.25 2.25 0 003.75 18.5h12.5a2.25 2.25 0 002.25-2.25V9.5M6.5 6.5h7M6.5 10h7M6.5 13.5h4"></path>
  </svg>
  Gestion Utilisateurs
</a>
{% endif %}
```

- [ ] **Step 2: Test navigation link**

1. Log in as admin
2. Click profile button
3. Expected: "Gestion Utilisateurs" link visible
4. Click it
5. Expected: Redirected to admin users page

- [ ] **Step 3: Commit**

```bash
git add templates/base.html
git commit -m "feat: add admin navigation link to user profile menu"
```

---

## Task 5: Add Validation and Error Handling

**Files:**
- Modify: `services/auth_service.py` - Add better validation
- Modify: `routes/admin.py` - Add flash messages for errors

- [ ] **Step 1: Update register_user validation**

In `services/auth_service.py`:
```python
@staticmethod
def register_user(email, password, full_name=None, language='fr', role='user'):
    """Register a new user with validation"""
    from models.user import User
    import re

    # Email validation
    if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        raise ValueError('Email invalide')

    if User.query.filter_by(email=email).first():
        raise ValueError(f'Un utilisateur avec l\'email {email} existe déjà')

    if not password or len(password) < 6:
        raise ValueError('Le mot de passe doit contenir au moins 6 caractères')

    if role not in ['user', 'admin']:
        raise ValueError('Rôle invalide')

    if language not in ['fr', 'lingala', 'swahili']:
        raise ValueError('Langue non supportée')

    user = User(email=email, full_name=full_name, language=language, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
```

- [ ] **Step 2: Test validation**

1. Try to create user with invalid email
2. Try with duplicate email
3. Try with short password
Expected: Appropriate error messages shown, user not created

- [ ] **Step 3: Commit**

```bash
git add services/auth_service.py
git commit -m "refactor: improve user creation validation and error messages"
```

---

## Task 6: Test Admin Panel End-to-End

**Files:**
- All files created/modified in previous tasks

- [ ] **Step 1: Create test admin account (if needed)**

If no admin account exists, create one via database or registration endpoint.

- [ ] **Step 2: Log in as admin**

1. Go to login page
2. Enter admin credentials
3. Expected: Logged in, redirected to dashboard

- [ ] **Step 3: Access admin panel**

1. Click profile menu
2. Click "Gestion Utilisateurs"
3. Expected: Admin users page loads with user list table

- [ ] **Step 4: Create new admin user**

1. Click "+ Créer un Utilisateur"
2. Fill in form with new admin user data
3. Select "Administrateur" role
4. Submit
Expected: User created, redirected to users list, success message shown

- [ ] **Step 5: Modify user role**

1. On users list, click "Modifier" on a user
2. Change role to "Admin"
3. Click "Enregistrer"
Expected: User updated, page reloads, new role visible in table

- [ ] **Step 6: Deactivate user**

1. Click "Modifier" on a user
2. Uncheck "Compte actif"
3. Click "Enregistrer"
Expected: User status changes to "Inactif" in table

- [ ] **Step 7: Test access control**

1. Log out
2. Log in as regular user
3. Try to navigate to `/admin/users`
Expected: Redirected to dashboard (access denied)

- [ ] **Step 8: Commit final testing**

```bash
git add -A
git commit -m "test: verify admin user management end-to-end"
```

---

## Summary

**Features Implemented:**
- ✅ Admin-only user management page with list of all users
- ✅ Create new user form with role selection (user or admin)
- ✅ Edit user modal for changing roles and active status
- ✅ API endpoint for user updates
- ✅ Navigation link in user profile menu
- ✅ Input validation and error handling
- ✅ CSRF protection on all forms
- ✅ Role-based access control (@admin_required decorator)

**Security Considerations:**
- All routes protected with @admin_required decorator
- CSRF tokens on all forms
- Input validation on all fields
- Role validation (only 'user' or 'admin' allowed)
- Email uniqueness enforced

**Files Modified/Created:**
- `templates/admin/users.html` (NEW)
- `templates/admin/create_user.html` (NEW)
- `routes/admin.py` (MODIFIED - filled from empty)
- `routes/api.py` (MODIFIED - added endpoint)
- `services/auth_service.py` (MODIFIED - added role param, validation)
- `templates/base.html` (MODIFIED - added admin link)

---

**Plan complete and saved.** Ready for implementation!

Two execution options available:

**1. Subagent-Driven (recommended)** - Fresh subagent per task with reviews
**2. Inline Execution** - Execute tasks in this session with checkpoints

Which approach would you prefer?
