document.addEventListener('DOMContentLoaded', function() {
    const ingredientNameInput = document.getElementById('ingredient_name');
    const categorySelect = document.getElementById('category');
    const unitSelect = document.getElementById('unit');
    
    if (ingredientNameInput) {
        // Auto-suggestion for ingredient names
        let currentFocus = -1;
        
        // Create auto-suggest container
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container';
        suggestionsContainer.style.display = 'none';
        ingredientNameInput.parentNode.appendChild(suggestionsContainer);
        
        // Function to fetch suggestions
        const fetchSuggestions = async (query) => {
            try {
                const response = await fetch(`/inventory/suggestions?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Network error');
                return await response.json();
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                return [];
            }
        };
        
        // Function to fetch ingredient metadata (unit, category)
        const fetchIngredientInfo = async (name) => {
            try {
                const response = await fetch(`/inventory/ingredient-info?name=${encodeURIComponent(name)}`);
                if (!response.ok) throw new Error('Network error');
                return await response.json();
            } catch (error) {
                console.error('Error fetching ingredient info:', error);
                return {};
            }
        };
        
        // Function to display suggestions
        const displaySuggestions = (suggestions) => {
            // Clear previous suggestions
            suggestionsContainer.innerHTML = '';
            
            if (suggestions.length === 0) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            // Add suggestions to container
            suggestions.forEach((suggestion, index) => {
                const suggestionItem = document.createElement('div');
                suggestionItem.className = 'suggestion-item';
                suggestionItem.textContent = suggestion;
                suggestionItem.setAttribute('data-value', suggestion);
                
                // Add event listener to suggestion item
                suggestionItem.addEventListener('click', async function() {
                    ingredientNameInput.value = this.getAttribute('data-value');
                    suggestionsContainer.style.display = 'none';
                    currentFocus = -1;
                    
                    // Fetch unit and category information
                    const info = await fetchIngredientInfo(ingredientNameInput.value);
                    
                    // Set unit and category if available
                    if (info.unit) {
                        Array.from(unitSelect.options).forEach(option => {
                            if (option.value === info.unit) {
                                unitSelect.value = info.unit;
                            }
                        });
                    }
                    
                    if (info.category) {
                        Array.from(categorySelect.options).forEach(option => {
                            if (option.value === info.category) {
                                categorySelect.value = info.category;
                            }
                        });
                    }
                });
                
                suggestionsContainer.appendChild(suggestionItem);
            });
            
            // Show suggestions container
            suggestionsContainer.style.display = 'block';
        };
        
        // Debounce function to limit API calls
        const debounce = (func, delay) => {
            let timeout;
            return function() {
                const context = this;
                const args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(context, args), delay);
            };
        };
        
        // Event listener for input changes
        ingredientNameInput.addEventListener('input', debounce(async function() {
            const query = this.value.trim();
            
            if (query.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            const suggestions = await fetchSuggestions(query);
            displaySuggestions(suggestions);
        }, 300));
        
        // Key navigation for suggestions
        ingredientNameInput.addEventListener('keydown', function(e) {
            const suggestions = suggestionsContainer.getElementsByClassName('suggestion-item');
            
            if (suggestions.length === 0) return;
            
            // Arrow down
            if (e.keyCode === 40) {
                currentFocus++;
                if (currentFocus >= suggestions.length) currentFocus = 0;
                setActiveSuggestion(suggestions);
            }
            // Arrow up
            else if (e.keyCode === 38) {
                currentFocus--;
                if (currentFocus < 0) currentFocus = suggestions.length - 1;
                setActiveSuggestion(suggestions);
            }
            // Enter
            else if (e.keyCode === 13 && currentFocus > -1) {
                e.preventDefault();
                suggestions[currentFocus].click();
            }
        });
        
        // Function to set active suggestion
        const setActiveSuggestion = (suggestions) => {
            // Remove active class from all suggestions
            Array.from(suggestions).forEach(item => {
                item.classList.remove('active');
            });
            
            // Add active class to current focus
            if (currentFocus >= 0 && currentFocus < suggestions.length) {
                suggestions[currentFocus].classList.add('active');
            }
        };
        
        // Close suggestions on click outside
        document.addEventListener('click', function(e) {
            if (e.target !== ingredientNameInput && e.target !== suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
        });
        
        // Auto-fill ingredient metadata on blur
        ingredientNameInput.addEventListener('blur', debounce(async function() {
            const name = this.value.trim();
            
            if (name.length < 2) return;
            
            // Fetch unit and category information
            const info = await fetchIngredientInfo(name);
            
            // Set unit and category if available
            if (info.unit) {
                Array.from(unitSelect.options).forEach(option => {
                    if (option.value === info.unit) {
                        unitSelect.value = info.unit;
                    }
                });
            }
            
            if (info.category) {
                Array.from(categorySelect.options).forEach(option => {
                    if (option.value === info.category) {
                        categorySelect.value = info.category;
                    }
                });
            }
        }, 300));
    }
});
