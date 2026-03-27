/**
 * Dashboard Page Module
 * Handles logo filtering, sharing, and deletion on the history/dashboard page
 */

(function() {
  'use strict';

  let currentShareLogoId = null;
  let currentDeleteLogoId = null;
  let currentDeleteLogoName = null;

  /**
   * Filter logos based on search text
   * Matches against the institution name stored in data-institution attribute
   */
  function filterLogos() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    const searchText = searchInput.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.logo-card');

    cards.forEach(card => {
      const institution = card.getAttribute('data-institution') || '';
      if (institution.includes(searchText)) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  }

  /**
   * Download logo in specified format
   * @param {number} logoId - ID of the logo to download
   * @param {string} format - File format: 'png' or 'jpg'
   */
  function downloadLogo(logoId, format) {
    if (!logoId) {
      console.error('No logo ID provided');
      return;
    }

    if (format !== 'png' && format !== 'jpg') {
      console.error('Invalid format:', format);
      return;
    }

    const downloadUrl = `/download/${logoId}/${format}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `logo_${logoId}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Open share modal for a specific logo
   * Creates share link via API
   * @param {number} logoId - ID of the logo to share
   */
  function shareLogo(logoId) {
    currentShareLogoId = logoId;
    const modal = document.getElementById('share-modal');
    const loading = document.getElementById('share-loading');
    const content = document.getElementById('share-content');
    const error = document.getElementById('share-error');

    if (modal) modal.classList.remove('hidden');
    if (loading) loading.classList.remove('hidden');
    if (content) content.classList.add('hidden');
    if (error) error.classList.add('hidden');

    const copySuccess = document.getElementById('copy-success');
    if (copySuccess) copySuccess.classList.add('hidden');

    // Create share link via API
    fetch('/api/share', {
      method: 'POST',
      headers: getFetchHeaders(true),
      body: JSON.stringify({
        logo_id: logoId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (loading) loading.classList.add('hidden');
      if (data.share_url) {
        const shareUrl = document.getElementById('share-url');
        if (shareUrl) shareUrl.value = data.share_url;
        if (content) content.classList.remove('hidden');
      } else {
        const errorMsg = document.getElementById('share-error-message');
        if (errorMsg) {
          errorMsg.textContent = data.error || 'Erreur lors de la création du lien de partage';
        }
        if (error) error.classList.remove('hidden');
      }
    })
    .catch(error => {
      console.error('Share API error:', error);
      if (loading) loading.classList.add('hidden');
      const errorMsg = document.getElementById('share-error-message');
      if (errorMsg) errorMsg.textContent = 'Erreur réseau. Veuillez réessayer.';
      if (error) error.classList.remove('hidden');
    });
  }

  /**
   * Close share modal
   */
  function closeShareModal() {
    const modal = document.getElementById('share-modal');
    if (modal) modal.classList.add('hidden');

    const copySuccess = document.getElementById('copy-success');
    if (copySuccess) copySuccess.classList.add('hidden');
  }

  /**
   * Copy share URL to clipboard
   * Uses the utility function from clipboard-utils.js
   */
  function copyToClipboard() {
    const shareUrl = document.getElementById('share-url');
    if (!shareUrl) return;

    const text = shareUrl.value;
    const copySuccess = document.getElementById('copy-success');

    // Use the utility function from clipboard-utils.js
    window.copyToClipboard(text, copySuccess);
  }

  /**
   * Open share URL in new window
   */
  function openShareURL() {
    const shareUrl = document.getElementById('share-url');
    if (shareUrl && shareUrl.value) {
      window.open(shareUrl.value, '_blank');
    }
  }

  /**
   * Show delete confirmation modal
   * @param {number} logoId - ID of the logo to delete
   * @param {string} institutionName - Name of the institution (for display in confirmation)
   */
  function deleteLogo(logoId, institutionName) {
    currentDeleteLogoId = logoId;
    currentDeleteLogoName = institutionName;
    const modal = document.getElementById('delete-modal');
    const message = document.getElementById('delete-message');

    if (message) {
      message.textContent = `Êtes-vous sûr de vouloir supprimer le logo de "${institutionName}"? Cette action ne peut pas être annulée.`;
    }
    if (modal) modal.classList.remove('hidden');
  }

  /**
   * Close delete confirmation modal
   */
  function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.add('hidden');
    currentDeleteLogoId = null;
    currentDeleteLogoName = null;
  }

  /**
   * Show styled error notification
   * @param {string} message - Error message to display
   */
  function showDeleteError(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
  }

  /**
   * Confirm and execute logo deletion
   * Makes DELETE request to API
   */
  function confirmDelete() {
    if (!currentDeleteLogoId) return;

    const button = document.getElementById('confirm-delete-btn');
    if (button) {
      button.disabled = true;
      button.textContent = 'Suppression en cours...';
    }

    fetch(`/api/dashboard/${currentDeleteLogoId}`, {
      method: 'DELETE',
      headers: getFetchHeaders(true)
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Remove the logo card from DOM with animation
        const cards = document.querySelectorAll('.logo-card');
        cards.forEach(card => {
          const cardText = card.textContent;
          if (cardText.includes(currentDeleteLogoName)) {
            // Fade out animation
            card.style.transition = 'opacity 0.3s ease-in-out';
            card.style.opacity = '0';
            setTimeout(() => {
              card.remove();
            }, 300);
          }
        });

        closeDeleteModal();

        // Show success message
        const message = document.createElement('div');
        message.className = 'flash-success';
        message.textContent = 'Logo supprimé avec succès.';
        const container = document.querySelector('main > div > div');
        if (container) {
          container.insertBefore(message, container.firstChild);
          setTimeout(() => message.remove(), 3000);
        }
      } else {
        const errorMsg = data.error || 'Impossible de supprimer le logo';
        showDeleteError('Erreur: ' + errorMsg);
        if (button) {
          button.disabled = false;
          button.textContent = 'Supprimer';
        }
      }
    })
    .catch(error => {
      console.error('Delete error:', error);
      showDeleteError('Erreur réseau lors de la suppression. Veuillez réessayer.');
      if (button) {
        button.disabled = false;
        button.textContent = 'Supprimer';
      }
    });
  }

  /**
   * Initialize event listeners when DOM is ready
   */
  function initializeEventListeners() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      // Use 'input' event (modern standard), not 'keyup' to avoid duplicate filtering
      searchInput.addEventListener('input', filterLogos);
    }
  }

  /**
   * Initialize the page when DOM is ready
   */
  function init() {
    initializeEventListeners();
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export functions to global scope for use in templates
  window.filterLogos = filterLogos;
  window.downloadLogo = downloadLogo;
  window.shareLogo = shareLogo;
  window.closeShareModal = closeShareModal;
  window.copyToClipboard = copyToClipboard;
  window.openShareURL = openShareURL;
  window.deleteLogo = deleteLogo;
  window.closeDeleteModal = closeDeleteModal;
  window.confirmDelete = confirmDelete;

})();
