/**
 * Sticky Bottom Bar for Configuration Tab
 * Shows Reset and Simulate buttons at the bottom when:
 * 1. User is in Configuration tab
 * 2. User has NOT scrolled to the bottom of the page
 */

(function() {
    'use strict';

    let debounceTimer;
    let scrollTicking = false;
    let currentState = null; // Track current state: null, 'showing', 'hiding', 'visible', 'hidden'
    let wasAtBottom = false; // Track previous bottom state for hysteresis

    function updateStickyBarVisibility() {
        const stickyBar = document.getElementById('sticky-bottom-bar');
        if (!stickyBar) return;

        // Check if configuration tab is active
        const activeTab = document.querySelector('.tab-pane.active');
        const isConfigTab = activeTab && activeTab.id && activeTab.id.includes('configuration');

        // Determine desired state
        let shouldShow = false;

        if (isConfigTab) {
            // Check scroll position
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
            wasAtBottom = false;
        }

        // Handle state transitions
        if (shouldShow) {
            // Want to show the bar
            if (currentState === 'visible' || currentState === 'showing') {
                // Already visible or showing, do nothing
                return;
            }

            if (currentState === 'hiding') {
                // Currently hiding, don't interrupt - wait for animation to finish
                return;
            }

            // Show the bar
            currentState = 'showing';
            stickyBar.style.display = 'flex';
            stickyBar.classList.remove('hide');
            // Trigger reflow to ensure animation plays
            stickyBar.offsetHeight;
            stickyBar.classList.add('show');

            // Mark as visible after animation completes
            setTimeout(() => {
                if (currentState === 'showing') {
                    currentState = 'visible';
                }
            }, 300);

        } else {
            // Want to hide the bar
            if (currentState === 'hidden' || currentState === 'hiding') {
                // Already hidden or hiding, do nothing
                return;
            }

            if (currentState === 'showing') {
                // Currently showing, don't interrupt - wait for animation to finish
                return;
            }

            if (currentState === 'visible' && stickyBar.classList.contains('show')) {
                // Hide the bar
                currentState = 'hiding';
                stickyBar.classList.remove('show');
                stickyBar.classList.add('hide');

                setTimeout(() => {
                    if (currentState === 'hiding') {
                        stickyBar.style.display = 'none';
                        stickyBar.classList.remove('hide');
                        currentState = 'hidden';
                    }
                }, 300);
            }
        }
    }

    function debouncedUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateStickyBarVisibility, 50);
    }

    // Throttled scroll handler using requestAnimationFrame
    function onScroll() {
        if (!scrollTicking) {
            window.requestAnimationFrame(() => {
                updateStickyBarVisibility();
                scrollTicking = false;
            });
            scrollTicking = true;
        }
    }

    // Update on scroll with throttling
    window.addEventListener('scroll', onScroll, { passive: true });

    // Update on tab change with debouncing (using MutationObserver)
    const observer = new MutationObserver(debouncedUpdate);

    // Wait for DOM to be ready
    function initObserver() {
        const tabsContainer = document.getElementById('tabs');
        if (tabsContainer) {
            observer.observe(tabsContainer, {
                attributes: true,
                subtree: true,
                attributeFilter: ['class']
            });
            // Initial update with a small delay to ensure DOM is fully ready
            setTimeout(updateStickyBarVisibility, 100);
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