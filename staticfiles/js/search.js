document.addEventListener('DOMContentLoaded', function () {
    const searchBar = document.getElementById('search-bar');
    const productList = document.getElementById('product-list');

    searchBar.addEventListener('input', function () {
        const query = searchBar.value.trim();

        if (query.length > 0) {
            fetch(`/products/search/?q=${query}`, {
                headers: {
                    'x-requested-with': 'XMLHttpRequest',
                },
            })
                .then(response => response.json())
                .then(data => {
                    productList.innerHTML = data.html;
                })
                .catch(error => console.error('Error fetching search results:', error));
        } else {
            // Reset the product list if search is empty
            fetch(`/products/`)
                .then(response => response.text())
                .then(html => {
                    productList.innerHTML = html;
                });
        }
    });
});