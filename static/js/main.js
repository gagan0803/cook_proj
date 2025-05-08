document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }
    
    // Filter toggle in recipe search
    const filterToggle = document.getElementById('filter-toggle');
    const filterForm = document.getElementById('filter-form');
    
    if (filterToggle && filterForm) {
        filterToggle.addEventListener('click', function() {
            filterForm.classList.toggle('d-none');
            filterToggle.textContent = filterForm.classList.contains('d-none') 
                ? 'Show Filters' 
                : 'Hide Filters';
        });
    }
    
    // Category filter in inventory
    const categoryFilters = document.querySelectorAll('.category-filter');
    const inventoryItems = document.querySelectorAll('.inventory-item');
    
    if (categoryFilters.length > 0 && inventoryItems.length > 0) {
        categoryFilters.forEach(filter => {
            filter.addEventListener('click', function() {
                // Remove active class from all filters
                categoryFilters.forEach(f => f.classList.remove('active'));
                
                // Add active class to current filter
                this.classList.add('active');
                
                const category = this.dataset.category;
                
                // Show/hide inventory items based on category
                inventoryItems.forEach(item => {
                    if (category === 'all' || item.dataset.category === category) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-warning)');
    
    if (alerts.length > 0) {
        setTimeout(function() {
            alerts.forEach(alert => {
                // Create a fadeout effect
                alert.style.transition = 'opacity 0.5s';
                alert.style.opacity = '0';
                
                // Remove the alert after fadeout
                setTimeout(function() {
                    alert.remove();
                }, 500);
            });
        }, 5000);
    }
});
