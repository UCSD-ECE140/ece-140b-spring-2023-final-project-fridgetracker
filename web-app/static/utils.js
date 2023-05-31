// request function for handling interactions with the server
function server_request(url, data = {}, verb, callback) {
  return fetch(url, {
      credentials: 'same-origin',
      method: verb,
      body: JSON.stringify(data),
      headers: { 'Content-Type': 'application/json' }
  })
      .then(response => response.json())
      .then(response => {
          if (callback)
              callback(response);
      })
      .catch(error => console.error('Error:', error));
}

// # Define a Pydantic model for the item data
// class Item(BaseModel):
//     listTage: str
//     itemName: str
//     addedDate: str
//     expierdDate: str

// add items to local storage -- TODO: connect to db using server routes
function addItem() {
    // Get values entered in form
    const name = document.querySelector('input[name="ProductBrand"]').value;
    const dateAdded = document.querySelector('input[name="dateAdded"]').value;
    const dateExpire = document.querySelector('input[name="dateExpire"]').value;
    const listSelect = document.querySelector('select[name="list-select"]').value;

    // create item for server pydantic model
    theItem = { "listTage": listSelect, "itemName":name, "addedDate": dateAdded, "expierdDate":dateExpire}
    console.log(theItem);

    // add item to db using fetch/server requests
    server_request('/add_item', theItem, 'POST', function(){
      // modify html elements here
      console.log("server_request() successful");
      console.log("modifying items...");
    })
  
    // Get the existing list of items for the selected list
    const items = JSON.parse(localStorage.getItem(listSelect)) || [];
  
    // Add the new item to the list
    items.push({ name, dateAdded, dateExpire });
  
    // Save the updated list to localStorage
    localStorage.setItem(listSelect, JSON.stringify(items));
  
    // Redirect to HomeScreen.html
    window.location.href = './HomeScreen.html';
}

// display items
function display_items(categoryDiv){
  categoryDiv.forEach(item => {
    const div = document.createElement('div');
    // div.classList.add('PentryListItem');
    div.textContent = `${item.name}, Added: ${item.dateAdded}, Expiry: ${item.dateExpire}`;
    categoryDiv.appendChild(div);
  })
}