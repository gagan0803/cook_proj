document.addEventListener('DOMContentLoaded', function() {
    // Recipe search auto-suggest
    const searchInput = document.querySelector('input[name="term"]');
    
    if (searchInput) {
        // Auto-suggestion for recipe search
        let currentFocus = -1;
        
        // Create auto-suggest container
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container';
        suggestionsContainer.style.display = 'none';
        searchInput.parentNode.appendChild(suggestionsContainer);
        
        // Function to fetch suggestions
        const fetchSuggestions = async (query) => {
            try {
                const response = await fetch(`/recipe/suggestions?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Network error');
                return await response.json();
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                return [];
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
                suggestionItem.addEventListener('click', function() {
                    searchInput.value = this.getAttribute('data-value');
                    suggestionsContainer.style.display = 'none';
                    currentFocus = -1;
                    
                    // Submit the form
                    searchInput.form.submit();
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
        searchInput.addEventListener('input', debounce(async function() {
            const query = this.value.trim();
            
            if (query.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            const suggestions = await fetchSuggestions(query);
            displaySuggestions(suggestions);
        }, 300));
        
        // Key navigation for suggestions
        searchInput.addEventListener('keydown', function(e) {
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
            if (e.target !== searchInput && e.target !== suggestionsContainer) {
                suggestionsContainer.style.display = 'none';
            }
        });
    }
    
    // Add to meal plan functionality
    const addToMealPlanBtn = document.querySelector('a[href*="meal_plan.index"]');
    
    if (addToMealPlanBtn) {
        addToMealPlanBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Extract recipe ID from URL
            const urlPath = window.location.pathname;
            const recipeId = urlPath.split('/').pop();
            
            // Create modal for meal plan selection
            const modalContainer = document.createElement('div');
            modalContainer.className = 'meal-plan-modal';
            modalContainer.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s;';
            
            // Create modal content
            modalContainer.innerHTML = `
                <div class="card" style="width: 100%; max-width: 500px; transform: translateY(20px); transition: transform 0.3s;">
                    <div class="card-body">
                        <h2>Add to Meal Plan</h2>
                        <p>Select when you want to cook this recipe.</p>
                        
                        <form method="POST" action="/meal-plan/add?next=${urlPath}">
                            <input type="hidden" name="recipe_id" value="${recipeId}">
                            <input type="hidden" name="csrf_token" value="${document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''}">
                            
                            <div class="form-group">
                                <label for="day_of_week" class="form-label">Day</label>
                                <select id="day_of_week" name="day_of_week" class="form-select">
                                    <option value="0">Monday</option>
                                    <option value="1">Tuesday</option>
                                    <option value="2">Wednesday</option>
                                    <option value="3">Thursday</option>
                                    <option value="4">Friday</option>
                                    <option value="5">Saturday</option>
                                    <option value="6">Sunday</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="meal_type" class="form-label">Meal Type</label>
                                <select id="meal_type" name="meal_type" class="form-select">
                                    <option value="breakfast">Breakfast</option>
                                    <option value="lunch">Lunch</option>
                                    <option value="dinner">Dinner</option>
                                    <option value="snack">Snack</option>
                                    <option value="dessert">Dessert</option>
                                </select>
                            </div>
                            
                            <div class="d-flex justify-content-between mt-4">
                                <button type="button" id="close-meal-plan-modal" class="btn btn-outline">Cancel</button>
                                <button type="submit" class="btn btn-primary">Add to Meal Plan</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            
            // Add modal to the document
            document.body.appendChild(modalContainer);
            
            // Show modal
            setTimeout(() => {
                modalContainer.style.display = 'flex';
                setTimeout(() => {
                    modalContainer.style.opacity = '1';
                    modalContainer.querySelector('.card').style.transform = 'translateY(0)';
                }, 10);
            }, 0);
            
            // Close modal on cancel button click
            document.getElementById('close-meal-plan-modal').addEventListener('click', function() {
                modalContainer.style.opacity = '0';
                modalContainer.querySelector('.card').style.transform = 'translateY(20px)';
                setTimeout(() => {
                    modalContainer.style.display = 'none';
                    modalContainer.remove();
                }, 300);
            });
            
            // Close modal on outside click
            modalContainer.addEventListener('click', function(e) {
                if (e.target === modalContainer) {
                    modalContainer.style.opacity = '0';
                    modalContainer.querySelector('.card').style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        modalContainer.style.display = 'none';
                        modalContainer.remove();
                    }, 300);
                }
            });
        });
    }
});
