/**
 * Signature Verifier - Main JavaScript
 * Handles form validation, file uploads, and UI interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initTooltips();
    
    // Setup file upload previews and validation
    setupFileUploads();
    
    // Handle form submissions
    setupFormHandlers();
    
    // Auto-dismiss flash messages
    autoDismissAlerts();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup file upload previews and validation
 */
function setupFileUploads() {
    document.querySelectorAll('input[type="file"]').forEach(input => {
        const container = input.closest('.file-upload') || input.parentElement;
        const preview = container.querySelector('.file-preview') || createPreviewElement(container);
        
        input.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                updateFilePreview(this, preview);
                validateFileType(this, preview);
            } else {
                resetPreview(preview);
            }
        });
        
        // Add drag and drop if parent has drop-area class
        if (container.classList.contains('drop-area')) {
            setupDragAndDrop(container, input, preview);
        }
    });
}

/**
 * Create a preview element if one doesn't exist
 */
function createPreviewElement(container) {
    const preview = document.createElement('div');
    preview.className = 'file-preview mt-2';
    container.appendChild(preview);
    return preview;
}

/**
 * Update file preview display
 */
function updateFilePreview(input, preview) {
    preview.textContent = input.files[0].name;
    preview.classList.add('has-file');
    preview.classList.remove('has-error');
}

/**
 * Validate file type based on input requirements
 */
function validateFileType(input, preview) {
    if (input.accept && input.files.length > 0) {
        const validTypes = input.accept.split(',').map(type => type.trim());
        const fileExtension = input.files[0].name.split('.').pop().toLowerCase();
        
        if (!validTypes.some(type => type.endsWith(fileExtension))) {
            preview.classList.remove('has-file');
            preview.classList.add('has-error');
            preview.textContent = `Please upload a ${validTypes.join(' or ')} file`;
        }
    }
}

/**
 * Reset file preview
 */
function resetPreview(preview) {
    preview.textContent = 'No file selected';
    preview.classList.remove('has-file', 'has-error');
}

/**
 * Setup drag and drop functionality
 */
function setupDragAndDrop(container, input, preview) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, unhighlight, false);
    });

    container.addEventListener('drop', handleDrop, false);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        container.classList.add('highlight');
    }

    function unhighlight() {
        container.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }
}

/**
 * Setup form submission handlers
 */
function setupFormHandlers() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Disable button and show spinner if available
                submitBtn.disabled = true;
                const spinner = submitBtn.querySelector('.spinner-border');
                if (spinner) {
                    spinner.classList.remove('d-none');
                }
                
                // Update button text if it contains a loading text data attribute
                const loadingText = submitBtn.dataset.loadingText;
                if (loadingText) {
                    submitBtn.innerHTML = loadingText;
                }
            }
        });
    });
}

/**
 * Auto-dismiss alert messages after 5 seconds
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
}

/**
 * Animation for verification result icons
 */
function animateVerificationResult() {
    const verificationIcon = document.querySelector('.verification-icon');
    if (verificationIcon) {
        verificationIcon.style.transform = 'scale(1.1)';
        setTimeout(() => {
            verificationIcon.style.transform = 'scale(1)';
        }, 200);
    }
}

// Run animations when page loads
window.addEventListener('load', animateVerificationResult);