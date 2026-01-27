/**
 * Sticky Bottom Bar for Configuration Tab
 * Shows Reset and Simulate buttons at the bottom when:
 * 1. User is in Configuration tab
 * 2. User has NOT scrolled to the bottom of the page
 */

(function() {
    'use strict';

    let currentState = 'hidden';
    let wasAtBottom = false;
    let scrollRAF = null;

    function updateStickyBarVisibility() {
        const stickyBar = document.getElementById('sticky-bottom-bar');
        if (!stickyBar) return;

        // Check if configuration tab is active
        const activeTab = document.querySelector('.tab-pane.active');
        const isConfigTab = activeTab && activeTab.id && activeTab.id.includes('configuration');

        let shouldShow = false;

        if (isConfigTab) {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = document.documentElement.clientHeight;

            // Use hysteresis: different thresholds for hiding vs showing
            // This prevents flickering when hovering near the threshold
            const hideThreshold = 150;  // Hide when within 150px of bottom
            const showThreshold = 200;  // Show when more than 200px from bottom

            const distanceFromBottom = scrollHeight - (scrollTop + clientHeight);

            if (wasAtBottom) {
                // Currently hidden - need to scroll further up to show
                shouldShow = distanceFromBottom > showThreshold;
            } else {
                // Currently visible - hide only when very close to bottom
                shouldShow = distanceFromBottom > hideThreshold;
            }

            wasAtBottom = !shouldShow;
        } else {
            // Not on config tab
            wasAtBottom = false;
        }

        // Simple state machine - only animate if state actually changes
        if (shouldShow && currentState !== 'visible') {
            currentState = 'visible';
            stickyBar.classList.remove('hide');
            stickyBar.classList.add('show');
        } else if (!shouldShow && currentState !== 'hidden') {
            currentState = 'hidden';
            stickyBar.classList.remove('show');
            stickyBar.classList.add('hide');
        }
    }

    // Throttled scroll handler using requestAnimationFrame
    function onScroll() {
        if (scrollRAF) return;
        scrollRAF = requestAnimationFrame(() => {
            updateStickyBarVisibility();
            scrollRAF = null;
        });
    }

    // Listen to scroll events
    window.addEventListener('scroll', onScroll, { passive: true });

    // Listen to tab clicks for tab switching
    function initTabListeners() {
        const selectors = [
            '[data-rb-event-key]',
            '.nav-link',
            '[role="tab"]',
            '#tabs .nav-link'
        ];

        selectors.forEach(selector => {
            const tabButtons = document.querySelectorAll(selector);
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    // Small delay to let tab switch complete
                    setTimeout(updateStickyBarVisibility, 100);
                });
            });
        });
    }

    // Initialize
    function init() {
        const stickyBar = document.getElementById('sticky-bottom-bar');
        if (stickyBar) {
            stickyBar.classList.add('hide');
            initTabListeners();
            setTimeout(updateStickyBarVisibility, 100);
        } else {
            // Retry if element not found yet
            setTimeout(init, 100);
        }
    }

    // Start initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();