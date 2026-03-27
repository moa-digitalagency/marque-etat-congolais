# Admin Panel Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance the admin user management panel with delete functionality, password changes, ministry field, user stats page, and dashboard statistics.

**Architecture:** Add ministry field to User model, create user profile stats page, add delete endpoint, enhance edit modal for password changes, and add stats blocks to admin dashboard.

**Tech Stack:** Flask, SQLAlchemy, Jinja2, CSS design system

---

## File Structure

**Files to create:**
- `templates/admin/user_profile.html` - User stats page with logo history
- `templates/admin/user_stats.html` - Reusable stats block template

**Files to modify:**
- `models/user.py` - Add ministry field
- `templates/admin/users.html` - Add delete button, stats blocks, view profile link, password change field
- `routes/admin.py` - Add delete route, user profile route, password change route
- `routes/api.py` - Add delete and password change endpoints

---

## Task 1: Add Ministry Field to User Model

**Files:**
- Modify: `models/user.py`

- [ ] **Step 1: Add ministry column to User model**

Add after `language` field:
```python
ministry = db.Column(db.String(255), nullable=True)  # Ministry/department name
```

- [ ] **Step 2: Create database migration (if using migrations)**

If using Flask-Migrate:
```bash
flask db migrate -m "add ministry field to user"
flask db upgrade
```

If not using migrations, manually add column to database:
```sql
ALTER TABLE user ADD COLUMN ministry VARCHAR(255);
```

- [ ] **Step 3: Update AuthService to include ministry**

Modify `services/auth_service.py` register_user():
```python
user = User(
    email=email,
    full_name=full_name,
    language=language,
    role=role,
    ministry=None  # Can be set later
)
```

- [ ] **Step 4: Commit**

```bash
git add models/user.py
git commit -m "feat: add ministry field to user model"
```

---

## Task 2: Update Edit User Modal - Add Password Change

**Files:**
- Modify: `templates/admin/users.html`
- Modify: `routes/api.py`

- [ ] **Step 1: Update edit modal in users.html**

Find the edit modal and add password section. Replace the form content with:

```html
<form id="editUserForm" style="display: flex; flex-direction: column; gap: var(--space-4);">
  <input type="hidden" id="userId" name="user_id">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

  <div>
    <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Email</label>
    <input type="text" id="userEmail" readonly style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); background-color: var(--bg-subtle); color: var(--text-secondary);">
  </div>

  <div>
    <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Nom Complet</label>
    <input type="text" id="userFullName" style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); width: 100%;">
  </div>

  <div>
    <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Ministère</label>
    <input type="text" id="userMinistry" style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); width: 100%;">
  </div>

  <div style="border-top: 1px solid var(--border-soft); padding-top: var(--space-4);">
    <h4 style="margin-bottom: var(--space-4);">Changer le Mot de Passe (Optionnel)</h4>

    <div>
      <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Nouveau Mot de Passe</label>
      <input type="password" id="userNewPassword" placeholder="Laisser vide pour ne pas changer" style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); width: 100%;">
    </div>

    <div>
      <label style="display: block; margin-bottom: var(--space-2); font-weight: 500;">Confirmer le Mot de Passe</label>
      <input type="password" id="userNewPasswordConfirm" placeholder="Confirmer le nouveau mot de passe" style="padding: var(--space-3); border: 1px solid var(--border-soft); border-radius: var(--radius-sm); width: 100%;">
    </div>
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
```

- [ ] **Step 2: Update openUserModal JavaScript**

Replace the openUserModal function:
```javascript
function openUserModal(userId, email, fullName, ministry, role, isActive) {
  document.getElementById('userId').value = userId;
  document.getElementById('userEmail').value = email;
  document.getElementById('userFullName').value = fullName;
  document.getElementById('userMinistry').value = ministry;
  document.getElementById('userRole').value = role;
  document.getElementById('userActive').checked = isActive;
  document.getElementById('userNewPassword').value = '';
  document.getElementById('userNewPasswordConfirm').value = '';
  document.getElementById('editUserModal').style.display = 'flex';
}
```

- [ ] **Step 3: Update form submission**

Replace the form submit handler:
```javascript
document.getElementById('editUserForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const userId = document.getElementById('userId').value;
  const fullName = document.getElementById('userFullName').value;
  const ministry = document.getElementById('userMinistry').value;
  const role = document.getElementById('userRole').value;
  const isActive = document.getElementById('userActive').checked;
  const newPassword = document.getElementById('userNewPassword').value;
  const newPasswordConfirm = document.getElementById('userNewPasswordConfirm').value;

  // Validate password if provided
  if (newPassword && newPassword !== newPasswordConfirm) {
    alert('Les mots de passe ne correspondent pas');
    return;
  }

  if (newPassword && newPassword.length < 6) {
    alert('Le mot de passe doit contenir au moins 6 caractères');
    return;
  }

  const data = {
    role: role,
    is_active: isActive,
    full_name: fullName,
    ministry: ministry
  };

  if (newPassword) {
    data.password = newPassword;
  }

  const response = await fetch(`/api/admin/users/${userId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
    },
    body: JSON.stringify(data)
  });

  if (response.ok) {
    location.reload();
  } else {
    const error = await response.json();
    alert('Erreur: ' + (error.error || 'Erreur lors de la modification'));
  }
});
```

- [ ] **Step 4: Update table row to include ministry and call openUserModal correctly**

Replace the table row for each user:
```html
<tr style="border-bottom: 1px solid var(--border-soft);">
  <td style="padding: var(--space-4); color: var(--text-primary);">{{ user.email }}</td>
  <td style="padding: var(--space-4); color: var(--text-primary);">{{ user.full_name or 'N/A' }}</td>
  <td style="padding: var(--space-4); color: var(--text-primary);">{{ user.ministry or 'N/A' }}</td>
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
  <td style="padding: var(--space-4); display: flex; gap: var(--space-2);">
    <button onclick="openUserModal({{ user.id }}, '{{ user.email }}', '{{ user.full_name or '' }}', '{{ user.ministry or '' }}', '{{ user.role }}', {{ user.is_active|lower }})" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm);">Modifier</button>
    <a href="{{ url_for('admin.user_profile', user_id=user.id) }}" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm); text-decoration: none;">Profil</a>
    <button onclick="deleteUser({{ user.id }})" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm); color: var(--color-error); border-color: var(--color-error);">Supprimer</button>
  </td>
</tr>
```

- [ ] **Step 5: Add deleteUser function**

Add before closing script tag:
```javascript
function deleteUser(userId) {
  if (confirm('Êtes-vous certain de vouloir supprimer cet utilisateur? Cette action est irréversible.')) {
    fetch(`/api/admin/users/${userId}/delete`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
      }
    })
    .then(response => {
      if (response.ok) {
        location.reload();
      } else {
        alert('Erreur lors de la suppression');
      }
    });
  }
}
```

- [ ] **Step 6: Update table headers**

Add ministry column header:
```html
<th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Ministère</th>
```

- [ ] **Step 7: Commit**

```bash
git add templates/admin/users.html
git commit -m "feat: add password change, ministry field, delete button to edit modal"
```

---

## Task 3: Add User Profile Stats Page

**Files:**
- Create: `templates/admin/user_profile.html`
- Modify: `routes/admin.py`

- [ ] **Step 1: Create user_profile.html template**

Create `templates/admin/user_profile.html`:
```html
{% extends "base.html" %}

{% block title %}Profil Utilisateur - {{ user.full_name or user.email }}{% endblock %}

{% block content %}
<div style="max-width: 1400px; margin: 0 auto; padding: var(--space-8) var(--space-4);">
  <!-- Header -->
  <div style="margin-bottom: var(--space-8);">
    <a href="{{ url_for('admin.users') }}" style="color: var(--primary); text-decoration: none; margin-bottom: var(--space-4); display: inline-block;">← Retour</a>
    <h1 style="color: var(--text-primary); margin-bottom: var(--space-2);">{{ user.full_name or user.email }}</h1>
    <p style="color: var(--text-secondary); margin-bottom: 0;">{{ user.email }}</p>
  </div>

  <!-- User Info Section -->
  <div class="card" style="margin-bottom: var(--space-8); padding: var(--space-8);">
    <h2 style="margin-bottom: var(--space-6);">Informations du Compte</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-6);">
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Email</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ user.email }}</p>
      </div>
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Rôle</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ 'Admin' if user.role == 'admin' else 'Utilisateur' }}</p>
      </div>
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Statut</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ 'Actif' if user.is_active else 'Inactif' }}</p>
      </div>
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Ministère</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ user.ministry or 'N/A' }}</p>
      </div>
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Créé le</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ user.created_at.strftime('%d %b %Y %H:%M') }}</p>
      </div>
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-2);">Mis à jour le</p>
        <p style="font-size: var(--text-lg); font-weight: 600; margin-bottom: 0;">{{ user.updated_at.strftime('%d %b %Y %H:%M') }}</p>
      </div>
    </div>
  </div>

  <!-- Stats Section -->
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-6); margin-bottom: var(--space-8);">
    <!-- Total Logos -->
    <div class="card" style="border-left: 4px solid var(--primary); padding: var(--space-8);">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
          <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Logos Générés</p>
          <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ total_logos }}</p>
        </div>
        <div style="background-color: var(--primary-light); padding: var(--space-4); border-radius: var(--radius-lg);">
          <svg style="width: 32px; height: 32px; color: var(--primary);" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- Logos This Month -->
    <div class="card" style="border-left: 4px solid var(--rdc-rouge); padding: var(--space-8);">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
          <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Ce Mois</p>
          <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ logos_this_month }}</p>
        </div>
        <div style="background-color: rgba(230, 30, 30, 0.1); padding: var(--space-4); border-radius: var(--radius-lg);">
          <svg style="width: 32px; height: 32px; color: var(--rdc-rouge);" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v2h16V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h12a1 1 0 100-2H6z" clip-rule="evenodd"></path>
          </svg>
        </div>
      </div>
    </div>

    <!-- Last Logo -->
    <div class="card" style="border-left: 4px solid var(--color-success); padding: var(--space-8);">
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
          <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Dernier Logo</p>
          <p style="font-size: var(--text-lg); font-weight: 600; color: var(--text-primary); margin-bottom: 0;">{{ last_logo_date or 'N/A' }}</p>
        </div>
        <div style="background-color: rgba(34, 197, 94, 0.1); padding: var(--space-4); border-radius: var(--radius-lg);">
          <svg style="width: 32px; height: 32px; color: var(--color-success);" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5.5 13a3.5 3.5 0 01-.369-6.98 4 4 0 117.753-1.3A4.5 4.5 0 1113.5 13H11V9.413l1.293 1.293a1 1 0 001.414-1.414l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13H5.5z"></path>
          </svg>
        </div>
      </div>
    </div>
  </div>

  <!-- Recent Logos -->
  {% if recent_logos %}
  <div class="card">
    <h2 style="margin-bottom: var(--space-6);">Logos Récents</h2>
    <div style="overflow-x: auto;">
      <table style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: var(--bg-subtle); border-bottom: 1px solid var(--border-soft);">
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Institution</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Modèle</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Créé le</th>
            <th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Action</th>
          </tr>
        </thead>
        <tbody>
          {% for logo in recent_logos %}
          <tr style="border-bottom: 1px solid var(--border-soft);">
            <td style="padding: var(--space-4); color: var(--text-primary);">{{ logo.institution_name }}</td>
            <td style="padding: var(--space-4); color: var(--text-primary);">{{ logo.template.name if logo.template else 'N/A' }}</td>
            <td style="padding: var(--space-4); color: var(--text-secondary); font-size: var(--text-sm);">{{ logo.created_at.strftime('%d %b %Y') }}</td>
            <td style="padding: var(--space-4);">
              <a href="{{ url_for('dashboard.logo_detail', logo_id=logo.id) }}" class="btn btn-outline" style="padding: var(--space-2) var(--space-3); font-size: var(--text-sm); text-decoration: none;">Voir</a>
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
  {% else %}
  <div class="card">
    <p style="color: var(--text-secondary); text-align: center; padding: var(--space-8);">Aucun logo généré</p>
  </div>
  {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 2: Add user_profile route to routes/admin.py**

Add:
```python
from datetime import datetime, timedelta

@admin_bp.route('/users/<int:user_id>/profile')
@admin_required
def user_profile(user_id):
    """Display user profile and statistics"""
    user = User.query.get_or_404(user_id)

    # Get stats
    total_logos = LogoGeneration.query.filter_by(user_id=user_id).count()

    # Logos this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logos_this_month = LogoGeneration.query.filter(
        LogoGeneration.user_id == user_id,
        LogoGeneration.created_at >= first_day_of_month
    ).count()

    # Recent logos
    recent_logos = LogoGeneration.query.filter_by(user_id=user_id).order_by(
        LogoGeneration.created_at.desc()
    ).limit(10).all()

    # Last logo date
    last_logo = LogoGeneration.query.filter_by(user_id=user_id).order_by(
        LogoGeneration.created_at.desc()
    ).first()
    last_logo_date = last_logo.created_at.strftime('%d %b %Y') if last_logo else None

    return render_template('admin/user_profile.html',
        user=user,
        total_logos=total_logos,
        logos_this_month=logos_this_month,
        last_logo_date=last_logo_date,
        recent_logos=recent_logos
    )
```

- [ ] **Step 3: Add imports to routes/admin.py**

Add:
```python
from models.logo import LogoGeneration
from datetime import datetime, timedelta
```

- [ ] **Step 4: Commit**

```bash
git add templates/admin/user_profile.html routes/admin.py
git commit -m "feat: add user profile stats page with logo history"
```

---

## Task 4: Add Delete and Password Change API Endpoints

**Files:**
- Modify: `routes/api.py`

- [ ] **Step 1: Add delete user endpoint**

Add to routes/api.py:
```python
@api_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    user = User.query.get_or_404(user_id)

    # Prevent deleting yourself
    if user.id == current_user.id:
        return jsonify({'error': 'Vous ne pouvez pas supprimer votre propre compte'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'success': 'Utilisateur supprimé'})
```

- [ ] **Step 2: Update user endpoint to support password and ministry**

Modify the existing update_user endpoint:
```python
@api_bp.route('/admin/users/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Update role
    if 'role' in data:
        if data['role'] not in ['user', 'admin']:
            return jsonify({'error': 'Rôle invalide'}), 400
        user.role = data['role']

    # Update active status
    if 'is_active' in data:
        user.is_active = data['is_active']

    # Update full name
    if 'full_name' in data:
        user.full_name = data['full_name']

    # Update ministry
    if 'ministry' in data:
        user.ministry = data['ministry']

    # Update password if provided
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
        user.set_password(data['password'])

    db.session.commit()

    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'is_active': user.is_active,
        'full_name': user.full_name,
        'ministry': user.ministry
    })
```

- [ ] **Step 3: Commit**

```bash
git add routes/api.py
git commit -m "feat: add delete user and password change API endpoints"
```

---

## Task 5: Add Stats Blocks to Admin Users Page

**Files:**
- Modify: `templates/admin/users.html`
- Modify: `routes/admin.py`

- [ ] **Step 1: Add stats calculation to users route**

Modify the users route in routes/admin.py:
```python
@admin_bp.route('/users', methods=['GET'])
@admin_required
def users():
    """Display user management page"""
    all_users = User.query.order_by(User.created_at.desc()).all()

    # Calculate stats
    total_users = len(all_users)
    admin_count = sum(1 for u in all_users if u.role == 'admin')
    user_count = total_users - admin_count
    active_users = sum(1 for u in all_users if u.is_active)
    inactive_users = total_users - active_users

    return render_template('admin/users.html',
        users=all_users,
        current_user=current_user,
        total_users=total_users,
        admin_count=admin_count,
        user_count=user_count,
        active_users=active_users,
        inactive_users=inactive_users
    )
```

- [ ] **Step 2: Add stats blocks to top of users.html**

Add after the header and before the users table:

```html
<!-- Stats Section -->
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--space-6); margin-bottom: var(--space-8);">
  <!-- Total Users Card -->
  <div class="card" style="border-left: 4px solid var(--primary);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Total Utilisateurs</p>
        <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ total_users }}</p>
      </div>
      <div style="background-color: var(--primary-light); padding: var(--space-4); border-radius: var(--radius-lg);">
        <svg style="width: 32px; height: 32px; color: var(--primary);" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM9 12a6 6 0 11-12 0 6 6 0 0112 0z"></path>
        </svg>
      </div>
    </div>
  </div>

  <!-- Admin Count Card -->
  <div class="card" style="border-left: 4px solid var(--primary);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Administrateurs</p>
        <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ admin_count }}</p>
      </div>
      <div style="background-color: var(--primary-light); padding: var(--space-4); border-radius: var(--radius-lg);">
        <svg style="width: 32px; height: 32px; color: var(--primary);" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z"></path>
        </svg>
      </div>
    </div>
  </div>

  <!-- Regular Users Card -->
  <div class="card" style="border-left: 4px solid var(--rdc-rouge);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Utilisateurs</p>
        <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ user_count }}</p>
      </div>
      <div style="background-color: rgba(230, 30, 30, 0.1); padding: var(--space-4); border-radius: var(--radius-lg);">
        <svg style="width: 32px; height: 32px; color: var(--rdc-rouge);" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10.5 1.5H3.75A2.25 2.25 0 001.5 3.75v12.5A2.25 2.25 0 003.75 18.5h12.5a2.25 2.25 0 002.25-2.25V9.5"></path>
        </svg>
      </div>
    </div>
  </div>

  <!-- Active Users Card -->
  <div class="card" style="border-left: 4px solid var(--color-success);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <div>
        <p style="color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; margin-bottom: var(--space-2);">Actifs</p>
        <p style="font-size: var(--text-4xl); font-weight: 700; color: var(--text-primary); margin-bottom: 0;">{{ active_users }}</p>
      </div>
      <div style="background-color: rgba(34, 197, 94, 0.1); padding: var(--space-4); border-radius: var(--radius-lg);">
        <svg style="width: 32px; height: 32px; color: var(--color-success);" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-2.77 3.066 3.066 0 00-3.58 3.03A6.124 6.124 0 001.5 12.9A6.124 6.124 0 006.9 17.5a6.124 6.124 0 006.9-4.6 3.066 3.066 0 003.03-3.58 3.066 3.066 0 00-2.77-1.745 2.756 2.756 0 00-5.528.584c0 .649-.364 1.21-.9 1.49a2.5 2.5 0 11-7.93-3.346 5.025 5.025 0 01-1.1-5.02z" clip-rule="evenodd"></path>
        </svg>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Update table header to include Ministry**

Add this header column in the table:
```html
<th style="padding: var(--space-4); text-align: left; font-weight: 600; color: var(--text-secondary);">Ministère</th>
```

- [ ] **Step 4: Commit**

```bash
git add templates/admin/users.html routes/admin.py
git commit -m "feat: add stats blocks to admin users page"
```

---

## Task 6: Test All New Features

- [ ] **Step 1: Test ministry field display**

1. Go to /admin/users
2. Verify ministry column shows (should be empty for existing users)
3. Edit a user and add ministry name
4. Verify it's saved and displayed

- [ ] **Step 2: Test password change**

1. Click Modifier on a user
2. Enter new password and confirm
3. Click Enregistrer
4. Try logging in with new password (if it's your account)

- [ ] **Step 3: Test user profile view**

1. Click Profil button on any user
2. Verify stats show (total logos, this month, last logo)
3. Verify recent logos table displays
4. Click "Voir" to navigate to logo detail

- [ ] **Step 4: Test delete user**

1. Click Supprimer on a test user
2. Confirm deletion
3. User should disappear from list

- [ ] **Step 5: Test stats blocks**

1. Go to /admin/users
2. Verify stats blocks show:
   - Total Users
   - Admins count
   - Regular Users count
   - Active Users count
3. Numbers should match the user list

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "test: verify all new admin panel features"
```

---

## Summary

**New Features Added:**
- ✅ Ministry field to user model
- ✅ Delete user functionality with confirmation
- ✅ Password change in edit modal
- ✅ Full name and ministry editing
- ✅ User profile stats page with logo history
- ✅ Stats blocks on admin users page
- ✅ View Profile button for each user

**Files Modified/Created:**
- models/user.py
- templates/admin/users.html
- templates/admin/user_profile.html
- routes/admin.py
- routes/api.py

**Security Considerations:**
- Delete prevention for self
- CSRF protection on delete
- Password minimum length validation
- Role-based access control maintained
