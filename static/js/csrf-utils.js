/**
 * CSRF Token Utility Module
 * Provides functions to extract CSRF token from DOM and add it to fetch request headers
 */

(function() {
  'use strict';

  /**
   * Extract CSRF token from DOM
   * Looks for input[name="csrf_token"] in the page
   * @returns {string} CSRF token or empty string if not found
   */
  function getCsrfToken() {
    const token = document.querySelector('input[name="csrf_token"]')?.value;
    return token || '';
  }

  /**
   * Get headers object with CSRF token and optionally JSON content type
   * @param {boolean} includeJson - Whether to include Content-Type: application/json header
   * @returns {object} Headers object ready for fetch API
   */
  function getFetchHeaders(includeJson = true) {
    const headers = {
      'X-CSRFToken': getCsrfToken()
    };
    if (includeJson) {
      headers['Content-Type'] = 'application/json';
    }
    return headers;
  }

  // Export functions to global scope for use in templates
  window.getCsrfToken = getCsrfToken;
  window.getFetchHeaders = getFetchHeaders;

})();
