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
  // function addItem() {
  //   const productBrandInput = document.querySelector('input[name="ProductBrand"]');
  //   const dateAddedInput = document.querySelector('input[name="dateAdded"]');
  //   const dateExpireInput = document.querySelector('input[name="dateExpire"]');
  //   const listSelect = document.getElementById('list-select');
  
  //   const newItem = {
  //     name: productBrandInput.value,
  //     dateAdded: dateAddedInput.value,
  //     dateExpire: dateExpireInput.value,
  //   };
  
  //   const selectedList = listSelect.value;
  //   const listData = JSON.parse(localStorage.getItem(selectedList) || '[]');
  //   listData.push(newItem);
  //   localStorage.setItem(selectedList, JSON.stringify(listData));
  //   window.location.href = './HomeScreen.html';
  // }
  
  // display items
  function display_items(categoryDiv){
    categoryDiv.forEach(item => {
      const div = document.createElement('div');
      // div.classList.add('PantryListItem');
      div.textContent = `${item.name}, Added: ${item.dateAdded}, Expiry: ${item.dateExpire}`;
      categoryDiv.appendChild(div);
    })
  }
  
  //current populating js
  function populateData() {
    const fridgeList = JSON.parse(localStorage.getItem('FridgeListS') || '[]');
    const counterItems = JSON.parse(localStorage.getItem('CounterItemS') || '[]');
    const pantryItems = JSON.parse(localStorage.getItem('PantryItemS') || '[]');
    const shoppingList = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
  
    const fridgeListDiv = document.querySelector('.FridgeListS');
    fridgeList.forEach(item => {
      const div = document.createElement('div');
      div.classList.add('FridgeListItem');
      div.textContent = `${item.name}, Added at ${item.dateAdded}, Expiry at ${item.dateExpire}`;
      fridgeListDiv.appendChild(div);
    });
  
    const counterItemDiv = document.querySelector('.CounterItemS');
    counterItems.forEach(item => {
      const div = document.createElement('div');
      div.classList.add('CounterListItem');
      div.textContent = `${item.name}, Added at ${item.dateAdded}, Expiry at ${item.dateExpire}`;
      counterItemDiv.appendChild(div);
    });
  
    const pantryItemDiv = document.querySelector('.PantryItemS');
    pantryItems.forEach(item => {
      const div = document.createElement('div');
      div.classList.add('PantryListItem');
      div.textContent = `${item.name}, Added: ${item.dateAdded}, Expiry: ${item.dateExpire}`;
      pantryItemDiv.appendChild(div);
    });
  
    const shoppingListDiv = document.querySelector('.ShoppingListS');
    shoppingList.forEach(item => {
      const div = document.createElement('div');
      div.classList.add('ShoppingListItem');
      div.textContent = `${item.name}, Added: ${item.dateAdded}, Expiry: ${item.dateExpire}`;
      shoppingListDiv.appendChild(div);
    });
  }
  
  function populateViewData() {
    const urlParams = new URLSearchParams(window.location.search);
    const listParam = urlParams.get('list');
    const nameInput = document.querySelector('.tiltle');
    nameInput.value = listParam;
    let listData = [];
  
    if (listParam == "All") {
      const fridgeListData = JSON.parse(localStorage.getItem("FridgeListS") || '[]');
      const counterItemListData = JSON.parse(localStorage.getItem("CounterItemS") || '[]');
      const pantryItemListData = JSON.parse(localStorage.getItem("PantryItemS") || '[]');
      const shoppingListData = JSON.parse(localStorage.getItem("ShoppingListS") || '[]');
      listData = listData.concat(fridgeListData, counterItemListData, pantryItemListData, shoppingListData);
    } else {
      listData = JSON.parse(localStorage.getItem(listParam) || '[]');
    }
  
    if (listParam === 'ShoppingListS') {
      const groceryListDiv = document.querySelector('.grocery-list');
      listData.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'itemCheckbox';
        const group1Div = document.createElement('div');
        group1Div.className = 'group1';
        const productP = document.createElement('p');
        productP.className = 'itemtext';
        productP.textContent = item.name;
        const dateAddedInput = document.createElement('input');
        dateAddedInput.type = 'date';
        dateAddedInput.className = 'dateAdded';
        dateAddedInput.value = item.dateAdded;
        group1Div.appendChild(checkbox);
        group1Div.appendChild(productP);
        group1Div.appendChild(dateAddedInput);
        div.appendChild(group1Div);
        groceryListDiv.appendChild(div);
      });
    } else {
      const groceryListDiv = document.querySelector('.grocery-list');
      listData.forEach(item => {
        const div = document.createElement('div');
        div.className = 'item';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'itemCheckbox';
        const group1Div = document.createElement('div');
        group1Div.className = 'group1';
        const productP = document.createElement('p');
        productP.className = 'itemtext';
        productP.textContent = item.name;
        const dateAddedInput = document.createElement('input');
        dateAddedInput.type = 'date';
        dateAddedInput.className = 'dateAdded';
        dateAddedInput.value = item.dateAdded;
        const dateExpireInput = document.createElement('input');
        dateExpireInput.type = 'date';
        dateExpireInput.className = 'dateExpire';
        dateExpireInput.value = item.dateExpire;
        group1Div.appendChild(checkbox);
        group1Div.appendChild(productP);
        group1Div.appendChild(dateAddedInput);
        group1Div.appendChild(dateExpireInput);
        div.appendChild(group1Div);
        groceryListDiv.appendChild(div);
      });
    }
  
    const deleteButton = document.querySelector('.deleteButton');
  deleteButton.addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.itemCheckbox');
    const checkedItems = [];
  
    checkboxes.forEach((checkbox, index) => {
      if (checkbox.checked) {
        checkedItems.push(index);
      }
    });
  
    if (listParam === 'All') {
      // Delete items from individual lists
      const fridgeListData = JSON.parse(localStorage.getItem('FridgeListS') || '[]');
      const counterItemListData = JSON.parse(localStorage.getItem('CounterItemS') || '[]');
      const pantryItemListData = JSON.parse(localStorage.getItem('PantryItemS') || '[]');
      const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
  
      const deletedItems = [];
  
      checkedItems.forEach((index) => {
        if (index < fridgeListData.length) {
          fridgeListData.splice(index - deletedItems.length, 1);
          deletedItems.push('FridgeListS');
        } else if (index < fridgeListData.length + counterItemListData.length) {
          counterItemListData.splice(index - fridgeListData.length - deletedItems.length, 1);
          deletedItems.push('CounterItemS');
        } else if (index < fridgeListData.length + counterItemListData.length + pantryItemListData.length) {
          pantryItemListData.splice(index - fridgeListData.length - counterItemListData.length - deletedItems.length, 1);
          deletedItems.push('PantryItemS');
        } else {
          shoppingListData.splice(index - fridgeListData.length - counterItemListData.length - pantryItemListData.length - deletedItems.length, 1);
          deletedItems.push('ShoppingListS');
        }
      });
  
      localStorage.setItem('FridgeListS', JSON.stringify(fridgeListData));
      localStorage.setItem('CounterItemS', JSON.stringify(counterItemListData));
      localStorage.setItem('PantryItemS', JSON.stringify(pantryItemListData));
      localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
  
      deletedItems.forEach((list) => {
        const listData = document.querySelector('.grocery-list[data-list="' + list + '"]');
        if (listData) {
          listData.innerHTML = '';
        }
      });
    } else {
      // Delete items from the selected list
      checkedItems.forEach((index) => {
        listData.splice(index, 1);
      });
  
      localStorage.setItem(listParam, JSON.stringify(listData));
  
      const listDataElement = document.querySelector('.grocery-list[data-list="' + listParam + '"]');
      if (listDataElement) {
        listDataElement.innerHTML = '';
      }
    }
  
    window.location.reload();
  });
  }
  