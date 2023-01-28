function createElementFromHTML(htmlString) {
    let div = document.createElement('div');
	div.className = 'product-entry'
	div.innerHTML = htmlString.trim();
	return div.firstChild;
}

// Get the button that adds new product entries
const products = document.querySelector('#products')
// Create a template for a new product entry

const productTemplate = `
	<div class="product-entry d-flex align-items-center flex-row mt-2" style="width:106.5%;">
		<input type="number" class="id1 form-control" placeholder="Enter vendor code" name="product_vendor_code" required>
	    <input type="number" class="form-control" id="quantity" placeholder="Enter quantity" style="margin-left: 5px" name="product_quantity" min="1" required>
	    <button class="delete-button btn btn-danger btn-sm rounded-1" type="button" data-toggle="tooltip" style="margin-left: 5px"><i class="fa fa-trash"></i></button>
	</div>
`;



// Add an event listener to the add product button
products.addEventListener("click", function(event) {
	const products_array = document.getElementsByClassName('product-entry')
	if (event.target.matches(".add-product")) {
		// Add a new product entry to the form
		products_array[products_array.length - 1].after(createElementFromHTML(productTemplate))
	}
	console.log(products_array.length)
	// If something exists in array
	if(products_array.length !== 1) {
		if(event.target.matches('.delete-button') || event.target.matches('.delete-button .fa-trash')) {
			// Delete this product entry from the form
			if(event.target.matches('.delete-button')) {
				event.target.parentElement.remove()

			} else {
				event.target.parentElement.parentElement.remove()
			}
		}
	}
});
