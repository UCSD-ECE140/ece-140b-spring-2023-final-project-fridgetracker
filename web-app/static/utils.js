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
// add items to local storage -- TODO: connect to db using server routes
function addItem() {
  console.log("addItem()");
    // Get values entered in form
    const name = document.querySelector('input[name="ProductBrand"]').value;
    const dateAdded = document.querySelector('input[name="dateAdded"]').value;
    const dateExpire = document.querySelector('input[name="dateExpire"]').value;
    const listSelect = document.querySelector('select[name="list-select"]').value;

    // create item for server pydantic model
    theItem = { "listTage": listSelect, "itemName":name, "addedDate": dateAdded, "expiredDate":dateExpire}
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
  
    // Redirect home
    window.location.href = './HomeScreen.html';
}
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
    div.textContent = `${item.name},  Expiry at ${item.dateExpire}`;
    fridgeListDiv.appendChild(div);
  });

  const counterItemDiv = document.querySelector('.CounterItemS');
  counterItems.forEach(item => {
    const div = document.createElement('div');
    div.classList.add('CounterListItem');
    div.textContent = `${item.name},  Expiry at ${item.dateExpire}`;
    counterItemDiv.appendChild(div);
  });

  const pantryItemDiv = document.querySelector('.PantryItemS');
  pantryItems.forEach(item => {
    const div = document.createElement('div');
    div.classList.add('PantryListItem');
    div.textContent = `${item.name},  Expiry: ${item.dateExpire}`;
    pantryItemDiv.appendChild(div);
  });

  const shoppingListDiv = document.querySelector('.ShoppingListS');
  shoppingList.forEach(item => {
    const div = document.createElement('div');
    div.classList.add('ShoppingListItem');
    div.textContent = `${item.name}, Added: ${item.dateAdded}`;
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
      const productNameInput = document.createElement('input');
      productNameInput.type = 'text';
      productNameInput.className = 'inputBox';
      productNameInput.value = item.name;
      const dateAddedInput = document.createElement('input');
      dateAddedInput.type = 'date';
      dateAddedInput.className = 'dateAdded';
      dateAddedInput.value = item.dateAdded;
      group1Div.appendChild(checkbox);
      group1Div.appendChild(productNameInput);
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
      const productNameInput = document.createElement('input');
      productNameInput.type = 'text';
      productNameInput.className = 'inputBox';
      productNameInput.value = item.name;
      const dateAddedInput = document.createElement('input');
      dateAddedInput.type = 'date';
      dateAddedInput.className = 'dateAdded';
      dateAddedInput.value = item.dateAdded;
      const dateExpireInput = document.createElement('input');
      dateExpireInput.type = 'date';
      dateExpireInput.className = 'dateExpire';
      dateExpireInput.value = item.dateExpire;
      group1Div.appendChild(checkbox);
      group1Div.appendChild(productNameInput);
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
          const deletedItem = fridgeListData.splice(index - deletedItems.length, 1)[0];
          deletedItems.push({
            list: 'FridgeListS',
            item: deletedItem
          });
        } else if (index < fridgeListData.length + counterItemListData.length) {
          const deletedItem = counterItemListData.splice(index - fridgeListData.length - deletedItems.length, 1)[0];
          deletedItems.push({
            list: 'CounterItemS',
            item: deletedItem
          });
        } else if (index < fridgeListData.length + counterItemListData.length + pantryItemListData.length) {
          const deletedItem = pantryItemListData.splice(index - fridgeListData.length - counterItemListData.length - deletedItems.length, 1)[0];
          deletedItems.push({
            list: 'PantryItemS',
            item: deletedItem
          });
        } else {
          const deletedItem = shoppingListData.splice(index - fridgeListData.length - counterItemListData.length - pantryItemListData.length - deletedItems.length, 1)[0];
          deletedItems.push({
            list: 'ShoppingListS',
            item: deletedItem
          });
        }
      });
  
      localStorage.setItem('FridgeListS', JSON.stringify(fridgeListData));
      localStorage.setItem('CounterItemS', JSON.stringify(counterItemListData));
      localStorage.setItem('PantryItemS', JSON.stringify(pantryItemListData));
      localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
  
      deletedItems.forEach((deletedItem) => {
        const list = deletedItem.list;
        const item = deletedItem.item;
  
        const addToShoppingList = confirm(`Do you want to add "${item.name}" to the ShoppingListS?`);
  
        if (addToShoppingList) {
          const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
          shoppingListData.push(item);
          localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
        }
  
        const listData = document.querySelector('.grocery-list[data-list="' + list + '"]');
        if (listData) {
          listData.innerHTML = '';
        }
      });
    } else {
      // Delete items from the selected list
      const listData = JSON.parse(localStorage.getItem(listParam) || '[]');
      const deletedItems = [];
  
      checkedItems.forEach((index) => {
        const deletedItem = listData.splice(index - deletedItems.length, 1)[0];
        deletedItems.push(deletedItem);
  
        const addToShoppingList = confirm(`Do you want to add "${deletedItem.name}" to the ShoppingListS?`);
  
        if (addToShoppingList) {
          const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
          shoppingListData.push(deletedItem);
          localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
        }
      });
  
      localStorage.setItem(listParam, JSON.stringify(listData));
  
      const listDataElement = document.querySelector('.grocery-list[data-list="' + listParam + '"]');
      if (listDataElement) {
        listDataElement.innerHTML = '';
      }
    }
  
    window.location.reload();
  });
  
  

  const updateButton = document.querySelector('.updateButton');
updateButton.addEventListener('click', () => {
  let listData = JSON.parse(localStorage.getItem(listParam) || '[]');
  console.log('Retrieved listData:', listData);

  const items = document.querySelectorAll('.grocery-list .item');
  console.log(items);

  items.forEach((item, index) => {
    const updatedNameElement = item.querySelector('.inputBox');
    const updatedName = updatedNameElement ? updatedNameElement.value : '';

    const updatedDateAddedElement = item.querySelector('.dateAdded');
    const updatedDateAdded = updatedDateAddedElement ? updatedDateAddedElement.value : '';

    const updatedDateExpireElement = item.querySelector('.dateExpire');
    const updatedDateExpire = updatedDateExpireElement ? updatedDateExpireElement.value : '';

    listData[index].name = updatedName;
    listData[index].dateAdded = updatedDateAdded;
    listData[index].dateExpire = updatedDateExpire;
  });

  console.log('Updated listData:', listData);

  localStorage.setItem(listParam, JSON.stringify(listData));

  window.location.reload();
});


}
