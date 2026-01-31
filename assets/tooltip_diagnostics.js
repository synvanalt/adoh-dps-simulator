/**
 * Tooltip Diagnostics Tool
 * This script monitors tooltip creation and identifies what's causing page stuttering
 */

(function() {
    'use strict';

    let tooltipCount = 0;
    let lastScrollHeight = document.documentElement.scrollHeight;
    let lastBodyHeight = document.body.scrollHeight;

    // Monitor for new tooltip elements being added
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    // Check if it's a tooltip
                    if (node.getAttribute && node.getAttribute('role') === 'tooltip') {
                        tooltipCount++;

                        const newScrollHeight = document.documentElement.scrollHeight;
                        const newBodyHeight = document.body.scrollHeight;

                        console.group(`🔍 Tooltip #${tooltipCount} Added`);
                        console.log('Tooltip element:', node);
                        console.log('Tooltip classes:', node.className);
                        console.log('Tooltip styles:', window.getComputedStyle(node));
                        console.log('Position:', window.getComputedStyle(node).position);
                        console.log('Z-index:', window.getComputedStyle(node).zIndex);
                        console.log('Top:', window.getComputedStyle(node).top);
                        console.log('Bottom:', window.getComputedStyle(node).bottom);
                        console.log('Transform:', window.getComputedStyle(node).transform);

                        // Check if page height changed
                        const heightChanged = (newScrollHeight !== lastScrollHeight) || (newBodyHeight !== lastBodyHeight);
                        if (heightChanged) {
                            console.warn('⚠️ PAGE HEIGHT CHANGED!');
                            console.log(`Document scrollHeight: ${lastScrollHeight} → ${newScrollHeight} (Δ${newScrollHeight - lastScrollHeight}px)`);
                            console.log(`Body scrollHeight: ${lastBodyHeight} → ${newBodyHeight} (Δ${newBodyHeight - lastBodyHeight}px)`);
                        } else {
                            console.log('✅ Page height unchanged');
                        }

                        // Check parent element
                        console.log('Parent element:', node.parentElement);
                        console.log('Parent position:', node.parentElement ? window.getComputedStyle(node.parentElement).position : 'N/A');

                        // Check if it's in a portal
                        const isInBody = node.parentElement === document.body;
                        console.log('Directly in <body>?', isInBody);

                        lastScrollHeight = newScrollHeight;
                        lastBodyHeight = newBodyHeight;

                        console.groupEnd();

                        // Monitor when tooltip is removed
                        const removalObserver = new MutationObserver((removeMutations) => {
                            removeMutations.forEach((removeMutation) => {
                                removeMutation.removedNodes.forEach((removedNode) => {
                                    if (removedNode === node) {
                                        console.log(`🗑️ Tooltip #${tooltipCount} Removed`);

                                        const afterRemoveScrollHeight = document.documentElement.scrollHeight;
                                        const afterRemoveBodyHeight = document.body.scrollHeight;

                                        if (afterRemoveScrollHeight !== newScrollHeight || afterRemoveBodyHeight !== newBodyHeight) {
                                            console.warn('⚠️ PAGE HEIGHT CHANGED ON REMOVAL!');
                                            console.log(`Document scrollHeight: ${newScrollHeight} → ${afterRemoveScrollHeight}`);
                                            console.log(`Body scrollHeight: ${newBodyHeight} → ${afterRemoveBodyHeight}`);
                                        }

                                        removalObserver.disconnect();
                                    }
                                });
                            });
                        });

                        if (node.parentElement) {
                            removalObserver.observe(node.parentElement, { childList: true });
                        }
                    }
                }
            });
        });
    });

    // Start observing
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    console.log('🔍 Tooltip diagnostics active. Hover over elements with tooltips to see detailed logs.');

    // Also monitor scroll events
    let scrollEventCount = 0;
    window.addEventListener('scroll', () => {
        scrollEventCount++;
        console.log(`📜 Scroll event #${scrollEventCount} - scrollTop: ${window.pageYOffset}`);
    }, { passive: true });

    // Monitor repaints (if supported)
    if (window.performance && window.performance.getEntriesByType) {
        setInterval(() => {
            const paintEntries = window.performance.getEntriesByType('paint');
            if (paintEntries.length > 0) {
                console.log('🎨 Recent paint events:', paintEntries);
            }
        }, 2000);
    }

})();