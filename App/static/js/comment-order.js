let comment_order = document.getElementById('commentModal')
if (comment_order.querySelector('form')) {
        let form = comment_order.querySelector('form');
        form.onsubmit = () => {
            let comment_field = document.querySelector('#new-comment')
            let modalBody = comment_order.querySelector('.modal-body');
            if (comment_field.value === "") {
                modalBody.insertAdjacentHTML(
                    'beforeend',"<p class='m-2 text-danger'>Comment field cannot be empty</p>"
                )
                return false;
            }
        }
}

// Get the modal element

if(comment_order.querySelector('#new-comment')) {
    // Cleaning the comment field after closing the modal window
    comment_order.addEventListener('hidden.bs.modal', () => {
        comment_order.querySelector('#new-comment').value = ""
    })
}


comment_order.addEventListener('show.bs.modal', function (event) {
  // Button that starts the modal window
  let button = event.relatedTarget;
  // get the comment from data attribute
  let comment = button.getAttribute('data-bs-comment');
  let modalBody = comment_order.querySelector('.modal-body');
  // check permission to comment
  let comment_allowed = button.getAttribute('data-bs-permission-to-comment');
  console.log(1)
  // Extract order id from the data attribute-bs-order-id into the hidden order_id field
  if (comment_allowed === "True") {
      let comment_field = comment_order.querySelector('#new-comment')
      // set comment value to textarea
      if(comment !== "None") {
          console.log(comment)
        comment_field.value = comment;
      }
      // set order_id to hidden field
      comment_order.querySelector('#order_id').value = button.getAttribute('data-bs-order-id');
  } else {
    // if user do not have permission to comment
    if (comment_order.querySelector('#new-comment') && comment_order.querySelector('#order_id')) {
      // remove form
      comment_order.querySelector('form').remove();
      // insert new element
      modalBody.insertAdjacentHTML('afterbegin','<p id="courier-comment"></p>');
    }
    //display comment
    if(comment|| comment !== "") {
      comment_order.querySelector('#courier-comment').textContent = comment;
    } else {
      //if no comment
      comment_order.querySelector('#courier-comment').textContent = "No comment";
    }
  }
});