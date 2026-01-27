/**
 * Sticky Bottom Bar for Configuration Tab
 * Shows Reset and Simulate buttons at the bottom when:
 * 1. User is in Configuration tab
 * 2. User has NOT scrolled to the bottom of the page
 */

(function() {
    'use strict';

    function updateStickyBarVisibility() {
        const stickyBar = document.getElementById('sticky-bottom-bar');
        if (!stickyBar) return;

        // Check if we're on the configuration tab
        const configTab = document.querySelector('[data-value="configuration"].active');
        const isConfigTab = configTab !== null;

        if (!isConfigTab) {
            stickyBar.style.display = 'none';
            return;
        }

        // Check scroll position
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;

        // Show bar if NOT at bottom (with 150px threshold to account for button area)
        const isAtBottom = (scrollTop + clientHeight) >= (scrollHeight - 150);

        if (isAtBottom) {
            stickyBar.style.display = 'none';
        } else {
            stickyBar.style.display = 'flex';
        }
    }

    // Update on scroll
    window.addEventListener('scroll', updateStickyBarVisibility);

    // Update on tab change (using MutationObserver)
    const observer = new MutationObserver(updateStickyBarVisibility);

    // Wait for DOM to be ready
    function initObserver() {
        const tabsContainer = document.getElementById('tabs');
        if (tabsContainer) {
            observer.observe(tabsContainer, {
                attributes: true,
                subtree: true,
                attributeFilter: ['class', 'data-value']
            });
            // Initial update
            updateStickyBarVisibility();
        } else {
            // Retry after a short delay
            setTimeout(initObserver, 100);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initObserver);
    } else {
        initObserver();
    }
})();

