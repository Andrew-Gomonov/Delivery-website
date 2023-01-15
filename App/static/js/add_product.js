function createElementFromHTML(htmlString) {
    let div = document.createElement('div');
	div.className = 'product-entry'
	div.innerHTML = htmlString.trim();
	return div.firstChild;
}

// Get the button that adds new product entries
const addProductButton = document.querySelector('.add-product');


// Create a template for a new product entry
const productTemplate = `
	<div class="product-entry d-flex align-items-center flex-row mt-2">
		<input type="number" class="form-control" placeholder="Enter vendor code" name="order_vendor_code" required>
	    <input type="number" class="form-control" id="quantity" placeholder="Enter quantity" style="margin-left: 5px" name="order_quantity" min="1" required>
	</div>
	`;

// Add an event listener to the add product button
addProductButton.addEventListener('click', () => {
    const products = document.getElementsByClassName('product-entry')
	// Add a new product entry to the form
	products[products.length - 1].after(createElementFromHTML(productTemplate))
});