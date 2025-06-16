// Main JavaScript file for the Dynamic Content Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Enhanced form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time character count for textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        if (textarea.id === 'content') {
            addCharacterCounter(textarea);
        }
    });
    
    // Auto-save draft functionality (simulate with localStorage)
    const contentForm = document.querySelector('form[action*="create_content"], form[action*="edit_content"]');
    if (contentForm) {
        setupAutoSave(contentForm);
    }
    
    // Enhanced search functionality
    setupAdvancedSearch();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
});

function addCharacterCounter(textarea) {
    const maxLength = 10000;
    const counter = document.createElement('div');
    counter.className = 'text-muted small mt-1';
    counter.innerHTML = `<i class="fas fa-info-circle me-1"></i><span id="char-count">0</span>/${maxLength} characters`;
    
    textarea.parentNode.appendChild(counter);
    
    const updateCounter = function() {
        const current = textarea.value.length;
        const countSpan = document.getElementById('char-count');
        countSpan.textContent = current;
        
        if (current > maxLength * 0.9) {
            counter.classList.add('text-warning');
            counter.classList.remove('text-muted');
        } else if (current > maxLength * 0.95) {
            counter.classList.add('text-danger');
            counter.classList.remove('text-warning', 'text-muted');
        } else {
            counter.classList.add('text-muted');
            counter.classList.remove('text-warning', 'text-danger');
        }
    };
    
    textarea.addEventListener('input', updateCounter);
    updateCounter(); // Initial count
}

function setupAutoSave(form) {
    const inputs = form.querySelectorAll('input, textarea, select');
    const saveKey = 'content_draft_' + (window.location.pathname.includes('edit') ? 
        window.location.pathname.split('/').pop() : 'new');
    
    // Load saved draft
    const savedDraft = localStorage.getItem(saveKey);
    if (savedDraft && !window.location.pathname.includes('edit')) {
        const draftData = JSON.parse(savedDraft);
        if (confirm('A saved draft was found. Would you like to restore it?')) {
            Object.keys(draftData).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = draftData[key];
                }
            });
        }
    }
    
    // Auto-save every 30 seconds
    setInterval(function() {
        const formData = {};
        inputs.forEach(input => {
            if (input.name && input.value) {
                formData[input.name] = input.value;
            }
        });
        localStorage.setItem(saveKey, JSON.stringify(formData));
    }, 30000);
    
    // Clear draft on successful submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(saveKey);
    });
}

function setupAdvancedSearch() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(function() {
            // Could implement live search here
            console.log('Search query:', searchInput.value);
        }, 300);
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + N: New content
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            window.location.href = '/create';
        }
        
        // Ctrl/Cmd + S: Save form (if on create/edit page)
        if ((event.ctrlKey || event.metaKey) && event.key === 's') {
            const submitButton = document.querySelector('input[type="submit"], button[type="submit"]');
            if (submitButton) {
                event.preventDefault();
                submitButton.click();
            }
        }
        
        // Escape: Close modals
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Export functions for use in other scripts
window.ContentManager = {
    showNotification,
    formatDateTime,
    truncateText
};
