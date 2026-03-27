/**
 * Logo Generator Page Module
 * Handles logo generation form submission, preview display, and download functionality
 */

(function() {
  'use strict';

  let currentLogoId = null;

  /**
   * Check form validity and enable/disable generate button
   * Button is enabled only when both template and institution name are provided
   */
  function checkFormValidity() {
    const templateId = document.getElementById('template_id')?.value;
    const institutionName = document.getElementById('institution_name')?.value.trim();
    const generateBtn = document.getElementById('generate-btn');

    if (generateBtn) {
      if (templateId && institutionName) {
        generateBtn.disabled = false;
      } else {
        generateBtn.disabled = true;
      }
    }
  }

  /**
   * Show or hide loading state in the form
   * @param {boolean} show - True to show loading, false to hide
   */
  function showLoading(show) {
    const indicator = document.getElementById('loading-indicator');
    const generateBtn = document.getElementById('generate-btn');
    const generateText = document.getElementById('generate-text');

    if (show) {
      if (indicator) indicator.classList.remove('hidden');
      if (generateBtn) {
        generateBtn.disabled = true;
      }
      if (generateText) {
        generateText.textContent = 'Génération...';
      }
    } else {
      if (indicator) indicator.classList.add('hidden');
      if (generateBtn) {
        generateBtn.disabled = false;
      }
      if (generateText) {
        generateText.textContent = 'Générer';
      }
    }
  }

  /**
   * Show preview image in preview container
   * @param {string} url - URL of the preview image
   */
  function showPreviewImage(url) {
    const img = document.getElementById('preview-image');
    const loading = document.getElementById('preview-loading');

    if (img) {
      img.src = url;
      img.classList.remove('hidden');
    }
    if (loading) {
      loading.classList.add('hidden');
    }
  }

  /**
   * Hide preview image and show loading state
   */
  function hidePreviewImage() {
    const img = document.getElementById('preview-image');
    const loading = document.getElementById('preview-loading');
    const error = document.getElementById('preview-error');

    if (img) img.classList.add('hidden');
    if (error) error.classList.add('hidden');
    if (loading) loading.classList.remove('hidden');
  }

  /**
   * Show error message in preview container
   * @param {string} message - Error message to display (in French)
   */
  function showError(message) {
    const error = document.getElementById('preview-error');
    const errorMsg = document.getElementById('error-message');
    const img = document.getElementById('preview-image');
    const loading = document.getElementById('preview-loading');

    if (error) error.classList.remove('hidden');
    if (img) img.classList.add('hidden');
    if (loading) loading.classList.add('hidden');
    if (errorMsg) errorMsg.textContent = message;
  }

  /**
   * Hide error message
   */
  function hideError() {
    const error = document.getElementById('preview-error');
    if (error) error.classList.add('hidden');
  }

  /**
   * Show download and share buttons section
   */
  function showDownloadButtons() {
    const section = document.getElementById('download-section');
    if (section) section.classList.remove('hidden');
  }

  /**
   * Hide download and share buttons section
   */
  function hideDownloadButtons() {
    const section = document.getElementById('download-section');
    if (section) section.classList.add('hidden');
  }

  /**
   * Download logo in specified format (PNG or JPG)
   * @param {string} format - File format: 'png' or 'jpg'
   */
  function downloadLogo(format) {
    if (!currentLogoId) {
      showError('Aucun logo à télécharger. Veuillez d\'abord générer un logo.');
      return;
    }

    if (format !== 'png' && format !== 'jpg') {
      console.error('Invalid format:', format);
      return;
    }

    // Build download URL with format as query parameter
    const downloadUrl = `/download/${currentLogoId}?format=${format}`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `logo_${currentLogoId}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Open share modal and create share link
   * Makes AJAX POST request to create share link
   */
  function shareLogo() {
    if (!currentLogoId) {
      showError('Aucun logo à partager. Veuillez d\'abord générer un logo.');
      return;
    }

    const modal = document.getElementById('share-modal');
    const loading = document.getElementById('share-loading');
    const content = document.getElementById('share-content');
    const error = document.getElementById('share-error');

    if (modal) modal.classList.remove('hidden');
    if (loading) loading.classList.remove('hidden');
    if (content) content.classList.add('hidden');
    if (error) error.classList.add('hidden');

    // Reset copy success message
    const copySuccess = document.getElementById('copy-success');
    if (copySuccess) copySuccess.classList.add('hidden');

    // Create share link via API
    fetch('/api/share', {
      method: 'POST',
      headers: getFetchHeaders(true),
      body: JSON.stringify({
        logo_id: currentLogoId
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
   * Copy share URL to clipboard and show feedback
   * Uses the utility function from clipboard-utils.js
   */
  function copyShareUrl() {
    const shareUrl = document.getElementById('share-url');
    if (!shareUrl) return;

    const text = shareUrl.value;
    const copySuccess = document.getElementById('copy-success');

    // Use the utility function from clipboard-utils.js
    copyToClipboard(text, copySuccess);
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
   * Handle form submission for logo generation
   * @param {Event} e - Form submit event
   */
  async function handleFormSubmit(e) {
    e.preventDefault();

    const templateId = document.getElementById('template_id')?.value;
    const institutionName = document.getElementById('institution_name')?.value.trim();
    const language = document.getElementById('language')?.value || 'fr';

    if (!templateId || !institutionName) {
      showError('Veuillez remplir tous les champs requis (modèle et nom de l\'institution)');
      return;
    }

    // Show loading state
    showLoading(true);
    hideDownloadButtons();
    hidePreviewImage();

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: getFetchHeaders(true),
        body: JSON.stringify({
          template_id: parseInt(templateId, 10),
          institution_name: institutionName,
          language: language
        })
      });

      const data = await response.json();

      if (response.ok && data.logo_id) {
        currentLogoId = data.logo_id;
        showPreviewImage(data.preview_url);
        showDownloadButtons();
        hideError();
      } else {
        const errorMessage = data.error || 'Erreur lors de la génération du logo. Veuillez réessayer.';
        showError(errorMessage);
      }
    } catch (error) {
      console.error('Generation error:', error);
      showError('Erreur réseau. Veuillez vérifier votre connexion et réessayer.');
    } finally {
      showLoading(false);
    }
  }

  /**
   * Initialize event listeners when DOM is ready
   */
  function initializeEventListeners() {
    const form = document.getElementById('generate-form');
    if (form) {
      form.addEventListener('submit', handleFormSubmit);
    }

    const templateSelect = document.getElementById('template_id');
    if (templateSelect) {
      templateSelect.addEventListener('change', checkFormValidity);
    }

    const institutionInput = document.getElementById('institution_name');
    if (institutionInput) {
      institutionInput.addEventListener('input', checkFormValidity);
    }

    const languageSelect = document.getElementById('language');
    if (languageSelect) {
      languageSelect.addEventListener('change', checkFormValidity);
    }

    const copyBtn = document.getElementById('copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', copyShareUrl);
    }

    const shareOpenBtn = document.getElementById('share-open-btn');
    if (shareOpenBtn) {
      shareOpenBtn.addEventListener('click', openShareURL);
    }

    // Initial form validity check
    checkFormValidity();
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
  window.checkFormValidity = checkFormValidity;
  window.downloadLogo = downloadLogo;
  window.shareLogo = shareLogo;
  window.closeShareModal = closeShareModal;
  window.openShareURL = openShareURL;
  window.copyShareUrl = copyShareUrl;

})();
