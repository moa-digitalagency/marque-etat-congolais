/**
 * Clipboard Utility Module
 * Provides functions to copy text to clipboard with modern Clipboard API and fallback
 */

(function() {
  'use strict';

  /**
   * Copy text to clipboard with fallback support
   * Uses modern Clipboard API with fallback to textarea selection method
   * @param {string} text - Text to copy to clipboard
   * @param {HTMLElement|null} feedbackElement - Optional element to show copy feedback message
   * @returns {Promise} Promise that resolves when copy is complete
   */
  async function copyToClipboard(text, feedbackElement = null) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        // Modern Clipboard API
        await navigator.clipboard.writeText(text);
      } else {
        // Fallback for older browsers
        fallbackCopy(text);
      }

      if (feedbackElement) {
        showCopyFeedback(feedbackElement);
      }
    } catch (err) {
      console.error('Clipboard copy failed:', err);
      // Use fallback if modern API fails
      fallbackCopy(text);
      if (feedbackElement) {
        showCopyFeedback(feedbackElement);
      }
    }
  }

  /**
   * Fallback copy method using textarea selection (for older browsers)
   * @param {string} text - Text to copy to clipboard
   */
  function fallbackCopy(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    textArea.style.pointerEvents = 'none';
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
    } catch (err) {
      console.error('Fallback copy failed:', err);
    }
    document.body.removeChild(textArea);
  }

  /**
   * Show copy success feedback message
   * Displays message for 2-3 seconds then hides it
   * @param {HTMLElement} element - Element containing the feedback message
   */
  function showCopyFeedback(element) {
    if (element) {
      element.textContent = 'Copié !';
      element.classList.remove('hidden');
      setTimeout(() => {
        element.textContent = 'Copier le lien';
        element.classList.add('hidden');
      }, 2000);
    }
  }

  // Export functions to global scope for use in templates
  // Only export copyToClipboard, fallbackCopy is internal
  window.copyToClipboard = copyToClipboard;
  window.showCopyFeedback = showCopyFeedback;

})();
