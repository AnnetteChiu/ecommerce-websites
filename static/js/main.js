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
    
    // Shopping cart shortcuts and quick actions
    setupCartShortcuts();
    
    // Initialize floating cart
    setupFloatingCart();
    
    // Initialize price comparison tooltips
    setupPriceComparison();
    
    // Responsive interactions
    setupResponsiveInteractions();
    
    // Mobile optimization
    setupMobileOptimizations();
    
    // Touch device enhancements
    setupTouchEnhancements();
    
    // Initialize micro-interactions and animations
    initializeMicroInteractions();
    
    // Setup scroll-based animations
    setupScrollAnimations();
    
    // Initialize interactive elements
    initializeInteractiveElements();
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

// Enhanced File Upload Functionality
function setupDragDropUpload() {
    const uploadZone = document.querySelector('.file-upload-zone');
    const fileInput = document.getElementById('fileInput');
    const filePreviewArea = document.getElementById('filePreviewArea');
    const fileList = document.getElementById('fileList');
    
    if (!uploadZone || !fileInput) return;
    
    // Drag and drop events
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#007bff';
        uploadZone.style.backgroundColor = '#f8f9fa';
    });
    
    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#dee2e6';
        uploadZone.style.backgroundColor = 'transparent';
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#dee2e6';
        uploadZone.style.backgroundColor = 'transparent';
        
        const files = e.dataTransfer.files;
        handleFileSelection(files);
    });
    
    // Click to upload
    uploadZone.addEventListener('click', (e) => {
        if (e.target && e.target.type !== 'file') {
            fileInput.click();
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files);
    });
    
    function handleFileSelection(files) {
        if (files.length === 0) return;
        
        // Update file input
        const dt = new DataTransfer();
        Array.from(files).forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
        
        displayFilePreview(files);
        validateFiles(files);
    }
    
    function displayFilePreview(files) {
        fileList.innerHTML = '';
        
        if (files.length > 0) {
            filePreviewArea.style.display = 'block';
            
            Array.from(files).forEach((file, index) => {
                const fileItem = createFilePreviewItem(file, index);
                fileList.appendChild(fileItem);
            });
        } else {
            filePreviewArea.style.display = 'none';
        }
    }
    
    function createFilePreviewItem(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        const fileInfo = document.createElement('div');
        fileInfo.className = 'd-flex align-items-center';
        
        const icon = getFileIcon(file.type, file.name);
        const fileName = document.createElement('span');
        fileName.textContent = file.name;
        fileName.className = 'me-2';
        
        const fileSize = document.createElement('small');
        fileSize.textContent = formatFileSize(file.size);
        fileSize.className = 'text-muted';
        
        fileInfo.appendChild(icon);
        fileInfo.appendChild(fileName);
        fileInfo.appendChild(fileSize);
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.onclick = () => removeFile(index);
        
        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);
        
        return fileItem;
    }
    
    function removeFile(index) {
        const dt = new DataTransfer();
        const files = Array.from(fileInput.files);
        
        files.forEach((file, i) => {
            if (i !== index) dt.items.add(file);
        });
        
        fileInput.files = dt.files;
        displayFilePreview(fileInput.files);
    }
    
    function getFileIcon(mimeType, fileName) {
        const icon = document.createElement('i');
        icon.className = 'fas fa-lg text-primary me-2';
        
        const extension = fileName.split('.').pop().toLowerCase();
        
        if (mimeType.startsWith('image/')) {
            icon.className += ' fa-image';
        } else if (mimeType.startsWith('video/')) {
            icon.className += ' fa-video';
        } else if (mimeType.startsWith('audio/')) {
            icon.className += ' fa-music';
        } else if (['pdf'].includes(extension)) {
            icon.className += ' fa-file-pdf';
        } else if (['doc', 'docx'].includes(extension)) {
            icon.className += ' fa-file-word';
        } else if (['xls', 'xlsx'].includes(extension)) {
            icon.className += ' fa-file-excel';
        } else if (['ppt', 'pptx'].includes(extension)) {
            icon.className += ' fa-file-powerpoint';
        } else if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension)) {
            icon.className += ' fa-file-archive';
        } else if (['txt', 'rtf'].includes(extension)) {
            icon.className += ' fa-file-alt';
        } else {
            icon.className += ' fa-file';
        }
        
        return icon;
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    function validateFiles(files) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = [
            // Images
            'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/svg+xml',
            // Documents
            'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'application/rtf', 'application/vnd.oasis.opendocument.text',
            'text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            // Video
            'video/mp4', 'video/webm', 'video/avi', 'video/quicktime', 'video/x-ms-wmv', 'video/x-flv',
            // Audio
            'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/aac', 'audio/mp4',
            // Archives
            'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
            'application/x-tar', 'application/gzip'
        ];
        
        Array.from(files).forEach(file => {
            if (file.size > maxSize) {
                showNotification(`File "${file.name}" is too large. Maximum size is 100MB.`, 'warning');
            }
        });
    }
}

// ===== MICRO-INTERACTIONS AND DELIGHTFUL UI ANIMATIONS =====

function initializeMicroInteractions() {
    // Add icon bounce effect to buttons with icons
    const iconButtons = document.querySelectorAll('.btn i');
    iconButtons.forEach(button => {
        button.parentElement.classList.add('icon-bounce');
    });
    
    // Initialize loading states for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.textContent;
                submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Submitting<span class="loading-dots"></span>';
                submitBtn.disabled = true;
                
                // Re-enable after a reasonable time if not redirected
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.innerHTML = originalText;
                        submitBtn.disabled = false;
                    }
                }, 5000);
            }
        });
    });
    
    // Add success animation to successful actions
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        alert.classList.add('success-bounce');
    });
    
    // Add pulse effect to new content
    const newContent = document.querySelectorAll('[data-new="true"]');
    newContent.forEach(element => {
        element.classList.add('pulse-new');
    });
    
    // Enhance search input with micro-interactions
    const searchInputs = document.querySelectorAll('input[name="search"]');
    searchInputs.forEach(input => {
        input.parentElement.classList.add('search-input');
    });
    
    // Add stagger animation to content grids
    const contentGrids = document.querySelectorAll('.row');
    contentGrids.forEach(grid => {
        if (grid.querySelectorAll('.card').length > 1) {
            grid.classList.add('content-grid');
        }
    });
}

function setupScrollAnimations() {
    // Intersection Observer for reveal animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for scroll-based animations
    const animatedElements = document.querySelectorAll('.card, .alert, .btn-primary');
    animatedElements.forEach(el => {
        el.classList.add('reveal-on-scroll');
        observer.observe(el);
    });
    
    // Parallax effect for background elements
    window.addEventListener('scroll', throttle(() => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.parallax || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }, 16));
}

function initializeInteractiveElements() {
    // Enhanced button interactions
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        // Add ripple effect on click
        button.addEventListener('click', function(e) {
            createRippleEffect(e, this);
        });
        
        // Add subtle hover animations
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Enhanced card interactions
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.zIndex = '10';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.zIndex = '';
        });
    });
    
    // Interactive badges
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.addEventListener('click', function() {
            this.classList.add('success-bounce');
            setTimeout(() => {
                this.classList.remove('success-bounce');
            }, 800);
        });
    });
    
    // Enhanced form interactions
    const formControls = document.querySelectorAll('.form-control, .form-select');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('form-focus');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('form-focus');
        });
        
        // Add floating label effect
        control.addEventListener('input', function() {
            if (this.value.length > 0) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
    
    // Progressive enhancement for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const files = this.files;
            if (files.length > 0) {
                showFileUploadFeedback(files);
            }
        });
    });
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Add loading states to navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (this.href && !this.href.includes('#')) {
                this.innerHTML += ' <span class="loading-spinner ms-2"></span>';
            }
        });
    });
}

function createRippleEffect(event, element) {
    const circle = document.createElement('span');
    const diameter = Math.max(element.clientWidth, element.clientHeight);
    const radius = diameter / 2;
    
    const rect = element.getBoundingClientRect();
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - rect.left - radius}px`;
    circle.style.top = `${event.clientY - rect.top - radius}px`;
    circle.classList.add('ripple');
    
    // Add ripple styles
    circle.style.position = 'absolute';
    circle.style.borderRadius = '50%';
    circle.style.background = 'rgba(255, 255, 255, 0.3)';
    circle.style.transform = 'scale(0)';
    circle.style.animation = 'ripple-animation 0.6s linear';
    circle.style.pointerEvents = 'none';
    
    const rippleKeyframes = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = rippleKeyframes;
        document.head.appendChild(style);
    }
    
    const ripple = element.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    element.appendChild(circle);
    
    setTimeout(() => {
        circle.remove();
    }, 600);
}

function showFileUploadFeedback(files) {
    // Create temporary feedback element
    const feedback = document.createElement('div');
    feedback.className = 'alert alert-success fade-in mt-2';
    feedback.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${files.length} file${files.length > 1 ? 's' : ''} selected successfully!
    `;
    
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput && fileInput.parentElement) {
        fileInput.parentElement.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }
}

function throttle(func, delay) {
    let timeoutId;
    let lastExecTime = 0;
    return function (...args) {
        const currentTime = Date.now();
        
        if (currentTime - lastExecTime > delay) {
            func.apply(this, args);
            lastExecTime = currentTime;
        } else {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(this, args);
                lastExecTime = Date.now();
            }, delay - (currentTime - lastExecTime));
        }
    };
}

// Enhanced notification system
function showNotification(message, type = 'info', duration = 4000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease-out;
    `;
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 300);
    }, duration);
    
    return notification;
}

function getIconForType(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'primary': 'star'
    };
    return icons[type] || 'info-circle';
}

// Enhanced loading states
function showLoadingState(element, text = 'Loading') {
    if (element) {
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = `
            <span class="loading-spinner me-2"></span>
            ${text}<span class="loading-dots"></span>
        `;
        element.disabled = true;
    }
}

function hideLoadingState(element) {
    if (element && element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
        delete element.dataset.originalContent;
    }
}

// Page transition effects
function initializePageTransitions() {
    // Fade in content on page load
    document.body.style.opacity = '0';
    window.addEventListener('load', () => {
        document.body.style.transition = 'opacity 0.3s ease-in';
        document.body.style.opacity = '1';
    });
    
    // Smooth page transitions for navigation
    const pageLinks = document.querySelectorAll('a:not([href^="#"]):not([href^="mailto"]):not([href^="tel"])');
    pageLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.hostname === window.location.hostname) {
                e.preventDefault();
                document.body.style.transition = 'opacity 0.2s ease-out';
                document.body.style.opacity = '0';
                
                setTimeout(() => {
                    window.location.href = this.href;
                }, 200);
            }
        });
    });
}

// Initialize page transitions
initializePageTransitions();

// Shopping Cart Shortcuts and Quick Actions
function setupCartShortcuts() {
    // Cart count update functionality
    updateCartCount();
    
    // Quick add to cart with keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Shift + C for cart
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            window.location.href = '/cart';
        }
        
        // Ctrl/Cmd + Shift + S for shop
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
            e.preventDefault();
            window.location.href = '/shop';
        }
    });
    
    // Quick add to cart buttons enhancement
    const addToCartButtons = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartButtons.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            quickAddToCart(form);
        });
    });
    
    // Cart item quick actions
    setupCartItemActions();
    
    // Mini cart preview on hover
    setupMiniCartPreview();
}

function updateCartCount() {
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            const cartBadge = document.getElementById('cart-count');
            if (cartBadge) {
                cartBadge.textContent = data.count || 0;
                cartBadge.style.display = data.count > 0 ? 'inline' : 'none';
            }
        })
        .catch(error => {
            console.log('Cart count update temporarily unavailable');
        });
}

function quickAddToCart(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        showLoadingState(submitBtn, 'Adding');
    }
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item added to cart!', 'success', 2000);
            updateCartCount();
            
            // Add visual feedback
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                submitBtn.classList.add('btn-success');
                setTimeout(() => {
                    hideLoadingState(submitBtn);
                    submitBtn.classList.remove('btn-success');
                }, 1500);
            }
        } else {
            showNotification(data.message || 'Error adding item', 'danger');
            if (submitBtn) hideLoadingState(submitBtn);
        }
    })
    .catch(error => {
        showNotification('Unable to add item to cart', 'warning');
        if (submitBtn) hideLoadingState(submitBtn);
    });
}

function setupCartItemActions() {
    // Quick quantity update
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        let updateTimeout;
        input.addEventListener('input', function() {
            clearTimeout(updateTimeout);
            updateTimeout = setTimeout(() => {
                quickUpdateQuantity(this);
            }, 1000);
        });
        
        // Keyboard shortcuts for quantity
        input.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.value = parseInt(this.value || 0) + 1;
                quickUpdateQuantity(this);
            } else if (e.key === 'ArrowDown' && parseInt(this.value) > 1) {
                e.preventDefault();
                this.value = parseInt(this.value) - 1;
                quickUpdateQuantity(this);
            }
        });
    });
    
    // Quick remove buttons
    const removeButtons = document.querySelectorAll('a[href*="remove_from_cart"]');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            quickRemoveItem(this.href);
        });
    });
}

function quickUpdateQuantity(input) {
    const form = input.closest('form');
    if (!form) return;
    
    const formData = new FormData(form);
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount();
            // Update total if visible
            const totalElement = document.querySelector('.cart-total');
            if (totalElement && data.new_total) {
                totalElement.textContent = '$' + data.new_total.toFixed(2);
            }
        }
    })
    .catch(error => {
        console.log('Quantity update temporarily unavailable');
    });
}

function quickRemoveItem(removeUrl) {
    if (confirm('Remove this item from cart?')) {
        fetch(removeUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Item removed from cart', 'info');
                updateCartCount();
                // Remove the item row
                const itemRow = document.querySelector(`[data-item-id="${data.item_id}"]`);
                if (itemRow) {
                    itemRow.style.transition = 'opacity 0.3s ease';
                    itemRow.style.opacity = '0';
                    setTimeout(() => itemRow.remove(), 300);
                }
            }
        })
        .catch(error => {
            showNotification('Unable to remove item', 'warning');
        });
    }
}

function setupMiniCartPreview() {
    const cartLink = document.getElementById('cart-shortcut');
    if (!cartLink) return;
    
    let previewTimeout;
    let miniCart = null;
    
    cartLink.addEventListener('mouseenter', function() {
        previewTimeout = setTimeout(() => {
            showMiniCartPreview();
        }, 500);
    });
    
    cartLink.addEventListener('mouseleave', function() {
        clearTimeout(previewTimeout);
        setTimeout(() => {
            if (miniCart && !miniCart.matches(':hover')) {
                hideMiniCartPreview();
            }
        }, 200);
    });
}

function showMiniCartPreview() {
    fetch('/api/cart/preview')
        .then(response => response.json())
        .then(data => {
            createMiniCartPreview(data);
        })
        .catch(error => {
            console.log('Cart preview temporarily unavailable');
        });
}

function createMiniCartPreview(cartData) {
    // Remove existing preview
    const existing = document.querySelector('.mini-cart-preview');
    if (existing) existing.remove();
    
    const preview = document.createElement('div');
    preview.className = 'mini-cart-preview position-absolute bg-white border rounded shadow-lg';
    preview.style.cssText = `
        top: 100%;
        right: 0;
        min-width: 300px;
        max-width: 400px;
        z-index: 1050;
        padding: 1rem;
        margin-top: 0.5rem;
    `;
    
    if (cartData.items && cartData.items.length > 0) {
        preview.innerHTML = `
            <h6 class="mb-3">Cart Items (${cartData.items.length})</h6>
            ${cartData.items.slice(0, 3).map(item => `
                <div class="d-flex align-items-center mb-2">
                    <img src="${item.image_url || '/static/placeholder.png'}" 
                         class="rounded me-2" style="width: 40px; height: 40px; object-fit: cover;">
                    <div class="flex-grow-1">
                        <small class="fw-semibold">${item.name}</small>
                        <div class="text-muted small">$${item.price} x ${item.quantity}</div>
                    </div>
                </div>
            `).join('')}
            ${cartData.items.length > 3 ? `<small class="text-muted">...and ${cartData.items.length - 3} more items</small>` : ''}
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <strong>Total: $${cartData.total}</strong>
                <a href="/cart" class="btn btn-primary btn-sm">View Cart</a>
            </div>
        `;
    } else {
        preview.innerHTML = `
            <div class="text-center py-3">
                <i class="fas fa-shopping-cart fa-2x text-muted mb-2"></i>
                <p class="text-muted mb-0">Your cart is empty</p>
                <a href="/shop" class="btn btn-outline-primary btn-sm mt-2">Start Shopping</a>
            </div>
        `;
    }
    
    const cartLink = document.getElementById('cart-shortcut');
    if (cartLink) {
        const container = cartLink.closest('.dropdown') || cartLink.parentElement;
        container.style.position = 'relative';
        container.appendChild(preview);
        
        // Add hover behavior to preview
        preview.addEventListener('mouseleave', function() {
            setTimeout(() => hideMiniCartPreview(), 200);
        });
    }
}

function hideMiniCartPreview() {
    const preview = document.querySelector('.mini-cart-preview');
    if (preview) {
        preview.style.transition = 'opacity 0.2s ease';
        preview.style.opacity = '0';
        setTimeout(() => preview.remove(), 200);
    }
}

// Floating Cart (漂浮購物車) Functionality
function setupFloatingCart() {
    const floatingCart = document.getElementById('floatingCart');
    const floatingCartMini = document.getElementById('floatingCartMini');
    const floatingCartBadge = document.getElementById('floatingCartBadge');
    
    if (!floatingCart) return;
    
    // Update floating cart display
    updateFloatingCartDisplay();
    
    // Click to toggle mini cart
    floatingCart.addEventListener('click', function() {
        toggleFloatingCartMini();
    });
    
    // Close mini cart when clicking outside
    document.addEventListener('click', function(e) {
        if (!floatingCart.contains(e.target) && !floatingCartMini.contains(e.target)) {
            hideFloatingCartMini();
        }
    });
    
    // Auto-hide mini cart after 10 seconds of no interaction
    let autoHideTimeout;
    floatingCartMini.addEventListener('mouseenter', function() {
        clearTimeout(autoHideTimeout);
    });
    
    floatingCartMini.addEventListener('mouseleave', function() {
        autoHideTimeout = setTimeout(() => {
            hideFloatingCartMini();
        }, 10000);
    });
}

function updateFloatingCartDisplay() {
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('floatingCartBadge');
            if (badge) {
                badge.textContent = data.count || 0;
                badge.style.display = data.count > 0 ? 'flex' : 'none';
            }
            loadFloatingCartItems();
        })
        .catch(error => {
            console.log('Cart count update temporarily unavailable');
        });
}

function loadFloatingCartItems() {
    fetch('/api/cart/preview')
        .then(response => response.json())
        .then(data => {
            updateFloatingCartContent(data);
        })
        .catch(error => {
            console.log('Cart preview temporarily unavailable');
        });
}

function updateFloatingCartContent(cartData) {
    const cartBody = document.getElementById('floatingCartBody');
    const cartTotal = document.getElementById('floatingCartTotal');
    
    if (!cartBody || !cartTotal) return;
    
    if (cartData.items && cartData.items.length > 0) {
        // Display cart items
        cartBody.innerHTML = cartData.items.map(item => `
            <div class="floating-cart-item">
                <img src="${item.image_url || '/static/uploads/placeholder.png'}" 
                     class="floating-cart-item-image" 
                     alt="${item.name}">
                <div class="floating-cart-item-info">
                    <div class="floating-cart-item-name">${item.name}</div>
                    <div class="floating-cart-item-price">$${parseFloat(item.price).toFixed(2)} × ${item.quantity}</div>
                </div>
            </div>
        `).join('');
        
        cartTotal.textContent = `$${parseFloat(cartData.total || 0).toFixed(2)}`;
    } else {
        // Empty cart state
        cartBody.innerHTML = `
            <div class="floating-cart-empty">
                <i class="fas fa-shopping-cart"></i>
                <p>Your cart is empty</p>
            </div>
        `;
        cartTotal.textContent = '$0.00';
    }
}

function toggleFloatingCartMini() {
    const miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        if (miniCart.classList.contains('show')) {
            hideFloatingCartMini();
        } else {
            showFloatingCartMini();
        }
    }
}

function showFloatingCartMini() {
    const miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        miniCart.classList.add('show');
        loadFloatingCartItems(); // Refresh cart contents
    }
}

function hideFloatingCartMini() {
    const miniCart = document.getElementById('floatingCartMini');
    if (miniCart) {
        miniCart.classList.remove('show');
    }
}

function createAddToCartAnimation(startElement) {
    const floatingCart = document.getElementById('floatingCart');
    if (!startElement || !floatingCart) return;
    
    const startRect = startElement.getBoundingClientRect();
    const endRect = floatingCart.getBoundingClientRect();
    
    const animation = document.createElement('div');
    animation.className = 'add-to-cart-animation';
    animation.style.left = startRect.left + (startRect.width / 2) - 15 + 'px';
    animation.style.top = startRect.top + (startRect.height / 2) - 15 + 'px';
    
    document.body.appendChild(animation);
    
    // Animate to floating cart
    const deltaX = endRect.left - startRect.left;
    const deltaY = endRect.top - startRect.top;
    
    animation.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    animation.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(0.5)`;
    animation.style.opacity = '0';
    
    setTimeout(() => {
        animation.remove();
        // Pulse the floating cart
        floatingCart.style.animation = 'pulse-badge 0.6s ease';
        setTimeout(() => {
            floatingCart.style.animation = '';
        }, 600);
    }, 800);
}

// Enhanced quick add to cart with animation
function quickAddToCartWithAnimation(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (submitBtn) {
        showLoadingState(submitBtn, 'Adding');
    }
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Item added to cart!', 'success', 2000);
            updateFloatingCartDisplay();
            createAddToCartAnimation(submitBtn);
            
            // Add visual feedback
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                submitBtn.classList.add('btn-success');
                setTimeout(() => {
                    hideLoadingState(submitBtn);
                    submitBtn.classList.remove('btn-success');
                }, 1500);
            }
        } else {
            showNotification(data.message || 'Error adding item', 'danger');
            if (submitBtn) hideLoadingState(submitBtn);
        }
    })
    .catch(error => {
        showNotification('Unable to add item to cart', 'warning');
        if (submitBtn) hideLoadingState(submitBtn);
    });
}

// Override the original quickAddToCart function
function quickAddToCart(form) {
    quickAddToCartWithAnimation(form);
}

// Price Comparison Tooltips
function setupPriceComparison() {
    // Find all price elements and add comparison functionality
    const priceElements = document.querySelectorAll('.product-price, .price, [data-price]');
    
    priceElements.forEach(priceElement => {
        const price = extractPrice(priceElement);
        if (price > 0) {
            setupPriceTooltip(priceElement, price);
        }
    });
}

function extractPrice(element) {
    // Extract price from various formats
    const text = element.textContent || element.dataset.price || '';
    const match = text.match(/\$?([0-9,]+\.?[0-9]*)/);
    return match ? parseFloat(match[1].replace(',', '')) : 0;
}

function setupPriceTooltip(priceElement, price) {
    // Skip if already has tooltip
    if (priceElement.querySelector('.price-tooltip')) return;
    
    // Wrap price in comparison container
    const wrapper = document.createElement('span');
    wrapper.className = 'price-comparison';
    priceElement.parentNode.insertBefore(wrapper, priceElement);
    wrapper.appendChild(priceElement);
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'price-tooltip';
    tooltip.innerHTML = `
        <div class="price-loading">
            Loading price insights...
        </div>
    `;
    wrapper.appendChild(tooltip);
    
    // Load price comparison data on hover
    let dataLoaded = false;
    wrapper.addEventListener('mouseenter', function() {
        if (!dataLoaded) {
            loadPriceComparisonData(price, tooltip);
            dataLoaded = true;
        }
    });
}

function loadPriceComparisonData(currentPrice, tooltip) {
    // Get product category and context
    const productCard = tooltip.closest('.card, .product-card, .content-card');
    const category = getProductCategory(productCard);
    
    fetch('/api/price-comparison', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({
            price: currentPrice,
            category: category
        })
    })
    .then(response => response.json())
    .then(data => {
        updatePriceTooltip(tooltip, currentPrice, data);
    })
    .catch(error => {
        tooltip.innerHTML = `
            <div class="price-tooltip-header">
                <h6 class="price-tooltip-title">📊 Price Analysis</h6>
            </div>
            <div class="price-insights">
                Price comparison temporarily unavailable
            </div>
        `;
    });
}

function updatePriceTooltip(tooltip, currentPrice, data) {
    const trendClass = data.trend === 'up' ? 'trend-up' : 
                      data.trend === 'down' ? 'trend-down' : 'trend-neutral';
    const trendIcon = data.trend === 'up' ? '↗️' : 
                     data.trend === 'down' ? '↘️' : '➡️';
    
    tooltip.innerHTML = `
        <div class="price-tooltip-header">
            <h6 class="price-tooltip-title">📊 Price Analysis</h6>
            ${getPriceBadge(data.value_rating)}
        </div>
        
        <div class="price-comparison-grid">
            <div class="price-stat">
                <div class="price-stat-label">Category Avg</div>
                <div class="price-stat-value">$${data.category_average.toFixed(2)}</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Market Range</div>
                <div class="price-stat-value">$${data.min_price.toFixed(2)} - $${data.max_price.toFixed(2)}</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Percentile</div>
                <div class="price-stat-value">${data.percentile}th</div>
            </div>
            <div class="price-stat">
                <div class="price-stat-label">Similar Items</div>
                <div class="price-stat-value">${data.similar_count}</div>
            </div>
        </div>
        
        <div class="price-trend ${trendClass}">
            <span class="trend-arrow">${trendIcon}</span>
            <span>${data.trend_text}</span>
        </div>
        
        <div class="price-insights">
            ${data.insights}
        </div>
    `;
}

function getPriceBadge(rating) {
    const badges = {
        'excellent': '<span class="price-badge badge-good-deal">Great Deal</span>',
        'good': '<span class="price-badge badge-good-deal">Good Value</span>',
        'average': '<span class="price-badge badge-average">Fair Price</span>',
        'premium': '<span class="price-badge badge-premium">Premium</span>',
        'high': '<span class="price-badge badge-high">High Price</span>'
    };
    return badges[rating] || '';
}

function getProductCategory(productCard) {
    if (!productCard) return 'general';
    
    // Try to extract category from various sources
    const categoryElement = productCard.querySelector('.category, .product-category, [data-category]');
    if (categoryElement) {
        return categoryElement.textContent.trim().toLowerCase() || categoryElement.dataset.category;
    }
    
    // Check product title for category hints
    const titleElement = productCard.querySelector('.card-title, .product-title, h3, h4, h5');
    if (titleElement) {
        const title = titleElement.textContent.toLowerCase();
        if (title.includes('shirt') || title.includes('blouse')) return 'shirts';
        if (title.includes('pant') || title.includes('chino')) return 'pants';
        if (title.includes('jacket') || title.includes('blazer')) return 'jackets';
        if (title.includes('shoe') || title.includes('loafer')) return 'shoes';
        if (title.includes('dress')) return 'dresses';
        if (title.includes('accessory')) return 'accessories';
    }
    
    return 'general';
}

// Enhanced price display with comparison indicators
function enhancePriceDisplays() {
    const priceElements = document.querySelectorAll('.product-price, .price');
    
    priceElements.forEach(element => {
        // Add visual enhancement to show it's interactive
        element.style.borderBottom = '1px dotted #007bff';
        element.style.cursor = 'help';
        element.title = 'Hover for price comparison';
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupDragDropUpload();
    enhancePriceDisplays();
});

// Responsive interactions
function setupResponsiveInteractions() {
    // Adaptive content display based on screen size
    function handleResponsiveContent() {
        const isMobile = window.innerWidth < 768;
        const cards = document.querySelectorAll('.content-card');
        
        cards.forEach(card => {
            const content = card.querySelector('.card-text');
            if (content && isMobile) {
                // Truncate content on mobile
                const originalText = content.textContent;
                if (originalText.length > 100) {
                    content.textContent = originalText.substring(0, 100) + '...';
                }
            }
        });
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(handleResponsiveContent, 100);
    });
    
    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(handleResponsiveContent, 250);
    });
    
    handleResponsiveContent();
}

// Mobile-specific optimizations
function setupMobileOptimizations() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        // Prevent zoom on form focus for iOS
        const formInputs = document.querySelectorAll('input, select, textarea');
        formInputs.forEach(input => {
            if (input.style.fontSize === '' || parseFloat(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
        
        // Add mobile-specific classes
        document.body.classList.add('mobile-device');
        
        // Optimize image loading
        const images = document.querySelectorAll('img[data-src]');
        if (images.length > 0) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        }
    }
}

// Touch device enhancements
function setupTouchEnhancements() {
    const supportsTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (supportsTouch) {
        document.body.classList.add('touch-device');
        
        // Enhanced touch feedback for buttons
        const touchElements = document.querySelectorAll('.btn, .card, .nav-link');
        touchElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.classList.remove('touch-active');
                }, 150);
            });
            
            element.addEventListener('touchcancel', function() {
                this.classList.remove('touch-active');
            });
        });
        
        // Swipe gesture support for cards
        let startX, startY, distX, distY;
        const threshold = 100;
        
        const swipeableCards = document.querySelectorAll('.content-card');
        swipeableCards.forEach(card => {
            card.addEventListener('touchstart', function(e) {
                const touch = e.changedTouches[0];
                startX = touch.pageX;
                startY = touch.pageY;
            }, { passive: true });
            
            card.addEventListener('touchend', function(e) {
                const touch = e.changedTouches[0];
                distX = touch.pageX - startX;
                distY = touch.pageY - startY;
                
                if (Math.abs(distX) > threshold && Math.abs(distY) < threshold) {
                    if (distX < 0) {
                        // Swipe left - quick view
                        const viewLink = this.querySelector('a[href*="view_content"]');
                        if (viewLink) {
                            window.location.href = viewLink.href;
                        }
                    }
                }
            }, { passive: true });
        });
    }
}

// Responsive navigation enhancements
function setupResponsiveNavigation() {
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbar.contains(e.target) && navbarCollapse.classList.contains('show')) {
                navbarToggler.click();
            }
        });
        
        // Close mobile menu when clicking nav link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                    setTimeout(() => navbarToggler.click(), 100);
                }
            });
        });
    }
}

// Initialize responsive features
document.addEventListener('DOMContentLoaded', function() {
    setupResponsiveNavigation();
});

// AI Relevance Score Functions
function loadAIRelevanceScores() {
    const contentCards = document.querySelectorAll('[data-content-id]');
    if (contentCards.length === 0) return;
    
    const contentIds = Array.from(contentCards).map(card => 
        parseInt(card.getAttribute('data-content-id'))
    ).filter(id => !isNaN(id));
    
    if (contentIds.length === 0) return;
    
    // Batch request for relevance scores
    fetch('/api/content/batch-relevance-scores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content_ids: contentIds
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.results) {
            displayRelevanceScores(data.results);
        }
    })
    .catch(error => {
        console.log('AI scoring temporarily unavailable');
    });
}

function displayRelevanceScores(scores) {
    Object.entries(scores).forEach(([contentId, analysis]) => {
        const card = document.querySelector(`[data-content-id="${contentId}"]`);
        if (!card || !analysis.overall_score) return;
        
        const score = analysis.overall_score;
        const scoreElement = createScoreBadge(score);
        
        // Find the best position to insert the score badge
        const cardHeader = card.querySelector('.card-header');
        const cardBody = card.querySelector('.card-body');
        const targetElement = cardHeader || cardBody;
        
        if (targetElement) {
            // Remove existing score if present
            const existingScore = card.querySelector('.ai-relevance-score');
            if (existingScore) {
                existingScore.remove();
            }
            
            // Add new score badge
            targetElement.style.position = 'relative';
            targetElement.appendChild(scoreElement);
        }
    });
}

function createScoreBadge(score) {
    const badge = document.createElement('div');
    badge.className = 'ai-relevance-score';
    badge.style.cssText = `
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        z-index: 10;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    `;
    
    // Set color based on score
    let bgColor;
    if (score >= 8) {
        bgColor = 'linear-gradient(135deg, #28a745, #20c997)';
    } else if (score >= 6) {
        bgColor = 'linear-gradient(135deg, #17a2b8, #007bff)';
    } else if (score >= 4) {
        bgColor = 'linear-gradient(135deg, #ffc107, #fd7e14)';
    } else {
        bgColor = 'linear-gradient(135deg, #dc3545, #e83e8c)';
    }
    
    badge.style.background = bgColor;
    badge.textContent = score.toFixed(1);
    
    // Add hover effect
    badge.addEventListener('mouseenter', function() {
        this.style.transform = 'scale(1.1)';
        this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.25)';
    });
    
    badge.addEventListener('mouseleave', function() {
        this.style.transform = 'scale(1)';
        this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
    });
    
    // Add tooltip
    badge.title = `AI Relevance Score: ${score.toFixed(1)}/10`;
    
    return badge;
}

function initializeAIScoring() {
    // Load scores on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAIRelevanceScores);
    } else {
        loadAIRelevanceScores();
    }
    
    // Reload scores when new content is dynamically added
    const observer = new MutationObserver(function(mutations) {
        let shouldReload = false;
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.hasAttribute && node.hasAttribute('data-content-id')) {
                        shouldReload = true;
                    }
                });
            }
        });
        
        if (shouldReload) {
            setTimeout(loadAIRelevanceScores, 500);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Real-time AI Score Updates
function refreshAIScore(contentId) {
    fetch(`/api/content/${contentId}/relevance-score`)
        .then(response => response.json())
        .then(data => {
            if (data.overall_score) {
                const scores = {};
                scores[contentId] = data;
                displayRelevanceScores(scores);
            }
        })
        .catch(error => {
            console.log('Could not refresh AI score');
        });
}

// Enhanced content card interactions with AI features
function enhanceContentCardsWithAI() {
    const contentCards = document.querySelectorAll('.content-card, .card');
    
    contentCards.forEach(card => {
        const contentId = card.getAttribute('data-content-id');
        if (!contentId) return;
        
        // Add AI analysis quick access
        const cardFooter = card.querySelector('.card-footer');
        if (cardFooter) {
            const aiButton = document.createElement('button');
            aiButton.className = 'btn btn-sm btn-outline-info me-2';
            aiButton.innerHTML = '<i class="fas fa-brain me-1"></i>AI';
            aiButton.title = 'View AI Analysis';
            aiButton.onclick = () => {
                window.location.href = `/content/${contentId}/ai-analysis`;
            };
            
            const buttonGroup = cardFooter.querySelector('.btn-group, .d-flex');
            if (buttonGroup) {
                buttonGroup.insertBefore(aiButton, buttonGroup.firstChild);
            }
        }
    });
}

// Initialize AI features
document.addEventListener('DOMContentLoaded', function() {
    initializeAIScoring();
    enhanceContentCardsWithAI();
});

// Export functions for use in other scripts
window.ContentManager = {
    showNotification,
    formatDateTime,
    truncateText,
    setupDragDropUpload,
    setupResponsiveInteractions,
    setupMobileOptimizations,
    setupTouchEnhancements,
    loadAIRelevanceScores,
    refreshAIScore,
    initializeAIScoring
};
