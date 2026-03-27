/**
 * Modal Utility Module
 * Provides reusable functions for opening/closing modals
 */

(function() {
  'use strict';

  /**
   * Open a modal by ID
   * Removes the 'hidden' class to display the modal
   * @param {string} modalId - ID of the modal element to open
   */
  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('hidden');
    }
  }

  /**
   * Close a modal by ID
   * Adds the 'hidden' class to hide the modal
   * @param {string} modalId - ID of the modal element to close
   */
  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  /**
   * Close all modals currently visible
   * Finds all elements with 'hidden' class that are modals and hides them
   */
  function closeAllModals() {
    const modals = document.querySelectorAll('[id$="-modal"]');
    modals.forEach(modal => {
      modal.classList.add('hidden');
    });
  }

  /**
   * Setup modal overlay click handler (close on overlay click)
   * Attaches event listener to close modal when clicking outside modal content
   * @param {string} modalId - ID of the modal to setup
   */
  function setupModalOverlayClose(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    // Only add listener if not already present
    if (modal.dataset.overlayListenerAdded) return;

    modal.addEventListener('click', (e) => {
      // Close only if clicking directly on the overlay (not on modal content)
      if (e.target === modal) {
        closeModal(modalId);
      }
    });

    modal.dataset.overlayListenerAdded = 'true';
  }

  /**
   * Setup all modals for overlay click closing
   */
  function setupAllModals() {
    const modals = document.querySelectorAll('[id$="-modal"]');
    modals.forEach(modal => {
      setupModalOverlayClose(modal.id);
    });
  }

  // Initialize all modals when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAllModals);
  } else {
    setupAllModals();
  }

  // Export functions to global scope for use in templates
  window.openModal = openModal;
  window.closeModal = closeModal;
  window.closeAllModals = closeAllModals;
  window.setupModalOverlayClose = setupModalOverlayClose;

})();
