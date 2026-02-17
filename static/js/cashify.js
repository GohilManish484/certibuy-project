(() => {
    const dropdownToggles = document.querySelectorAll('[data-dropdown]');
    const dropdownMenus = document.querySelectorAll('[data-menu]');

    const closeAllDropdowns = () => {
        dropdownMenus.forEach(menu => menu.classList.remove('is-open'));
    };

    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', (event) => {
            event.stopPropagation();
            const target = toggle.getAttribute('data-dropdown');
            const menu = document.querySelector(`[data-menu="${target}"]`);
            if (!menu) {
                return;
            }
            const isOpen = menu.classList.contains('is-open');
            closeAllDropdowns();
            if (!isOpen) {
                menu.classList.add('is-open');
            }
        });
    });

    document.addEventListener('click', () => {
        closeAllDropdowns();
    });

    const searchInput = document.getElementById('cbSearchInput');
    const suggestBox = document.getElementById('cbSuggest');

    if (searchInput && suggestBox) {
        let controller = null;
        let lastQuery = '';

        const renderSuggestions = (items) => {
            suggestBox.innerHTML = '';
            if (!items.length) {
                suggestBox.classList.remove('is-open');
                return;
            }
            items.forEach(item => {
                const anchor = document.createElement('a');
                anchor.textContent = item.name;
                anchor.href = `/shop/?search=${encodeURIComponent(item.name)}`;
                suggestBox.appendChild(anchor);
            });
            suggestBox.classList.add('is-open');
        };

        const fetchSuggestions = async (query) => {
            const endpoint = searchInput.getAttribute('data-suggest-url');
            if (!endpoint) {
                return;
            }
            if (controller) {
                controller.abort();
            }
            controller = new AbortController();
            const response = await fetch(`${endpoint}?q=${encodeURIComponent(query)}`, {
                signal: controller.signal
            });
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            renderSuggestions(data.results || []);
        };

        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            if (query.length < 2 || query === lastQuery) {
                suggestBox.classList.remove('is-open');
                return;
            }
            lastQuery = query;
            fetchSuggestions(query).catch(() => {
                suggestBox.classList.remove('is-open');
            });
        });

        document.addEventListener('click', (event) => {
            if (!suggestBox.contains(event.target) && event.target !== searchInput) {
                suggestBox.classList.remove('is-open');
            }
        });
    }
})();
