document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('recipe-search-input');
    const suggestionsContainer = document.getElementById('suggestions-container');

    async function fetchSuggestions(term) {
        const response = await fetch(`/api/recipe/suggestions?term=${term}`);
        const data = await response.json();
        return data.suggestions;
    }

    function displaySuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        suggestions.forEach(suggestion => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = suggestion.name;
            suggestionsContainer.appendChild(div);
        });
        suggestionsContainer.style.display = suggestions.length ? 'block' : 'none';
    }

    searchInput.addEventListener('input', async function() {
        const term = searchInput.value.trim();
        if (term.length > 1) {
            const suggestions = await fetchSuggestions(term);
            displaySuggestions(suggestions);
        } else {
            suggestionsContainer.style.display = 'none';
        }
    });
});
