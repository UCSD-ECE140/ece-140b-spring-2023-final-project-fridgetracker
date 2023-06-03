// request function for handling interactions with the server
// note: server_request has error when calling GET so use fetch instead
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


// add items to local storage connected to db using server routes
function addItem() {
    // Get values entered in form
    const name = document.querySelector('input[name="ProductBrand"]').value;
    const dateAdded = document.querySelector('input[name="dateAdded"]').value;
    const dateExpire = document.querySelector('input[name="dateExpire"]').value;
    const listSelect = document.querySelector('select[name="list-select"]').value;

    // create item for server pydantic model
    theItem = { "listTage": listSelect, "itemName":name, "addedDate": dateAdded, "expiredDate":dateExpire};

    // add item to db using fetch/server requests
    server_request('/add_item', theItem, 'POST', function(){
      
      // next 3 lines are local storage, remove later
      // Get the existing list of items for the selected list
      const items = JSON.parse(localStorage.getItem(listSelect)) || [];
    
      // Add the new item to the list
      items.push({ name, dateAdded, dateExpire });
    
      // Save the updated list to localStorage
      localStorage.setItem(listSelect, JSON.stringify(items));
    
      // Redirect home
      alert(`${name} added to ${listSelect}!`);
      window.location.href = '/';
    })
}


// populates homepage section lists with db data
function populateData(){
  const sections = ['FridgeListS', 'CounterItemS', 'PantryItemS', 'ShoppingListS'];
  for (let i = 0; i < sections.length; i++) {
    get_list_from_db(sections[i]);
  }
  console.log('homepage section lists populated with db data.');
}

// helper function to get list from db and add elements.
// input: listName (string)
function get_list_from_db(listName){
  fetch(`/get_${listName}_list`, {method:'GET'})
  .then(response => response.json())
  .then(retrievedList => {

    // select the div container for section list
    const listDiv = document.querySelector(`.${listName}`);
    var listClass = '';
    if (listName == 'FridgeListS'){
      listClass = 'FridgeListItem'
    } else if (listName == 'CounterItemS'){
      listClass = 'CounterListItem'
    } else if (listName == 'PantryItemS'){
      listClass = 'PantryListItem'
    } else if (listName == 'ShoppingListS'){
      listClass = 'ShoppingListItem'
    } 

    // add each item to list
    retrievedList.forEach(item => {
      const div = document.createElement('div');
      div.classList.add(listClass);
      expiry = item[2].substring(0, 10);
      div.textContent = `${item[0]},  Expiry at ${expiry}`;
      listDiv.appendChild(div);
    });
  })
  .catch(error => console.error('Error:', error));
}

//helper function for delete
function deleteItem(itemName, listSelect) {
  const confirmation = confirm(`Are you sure you want to delete ${itemName}?`);
  if (confirmation) {
    const data = { listTage: listSelect, itemName: itemName };
    server_request('/delete_item', data, 'DELETE', function () {
      // Remove the item from the DOM or perform any other necessary actions
      alert(`${itemName} deleted from ${listSelect}!`);
      location.reload(); // Refresh the page
    });
  }
}

// helper function for fetch get route
function fetch_list(section){
  var listData;
  fetch(`/get_${section}_list`, {method: 'GET'})
  .then(response => response.json())
  .then(theList => { 
    listData = theList.json();
  })
  .catch(error => console.error('Error:', error));
  return listData;
}

// populate individual sections in viewrecipe.html
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
  //sako
  deleteButton.addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.itemCheckbox');
    const checkedItems = [];
  
    checkboxes.forEach((checkbox, index) => {
      if (checkbox.checked) {
        const itemName = checkbox.parentElement.querySelector('.inputBox').value;
        checkedItems.push(itemName);
      }
    });
  
    checkedItems.forEach((itemName) => {
      deleteItem(itemName, listSelect);
    });
  });
  
  // const deleteButton = document.querySelector('.deleteButton');
  // deleteButton.addEventListener('click', () => {
  //   const checkboxes = document.querySelectorAll('.itemCheckbox');
  //   const checkedItems = [];
  
  //   checkboxes.forEach((checkbox, index) => {
  //     if (checkbox.checked) {
  //       checkedItems.push(index);
  //     }
  //   });
  
    if (listParam === 'All') {
      // Delete items from individual lists
      
      // local storage version
      // const fridgeListData = JSON.parse(localStorage.getItem('FridgeListS') || '[]');
      const counterItemListData = JSON.parse(localStorage.getItem('CounterItemS') || '[]');
      const pantryItemListData = JSON.parse(localStorage.getItem('PantryItemS') || '[]');
      const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
  
      // use a fetch request 
      var fridgeListData;
      fetch('/get_FridgeListS_list', {method: 'GET'})
      .then(response => response.json())
      .then(theFridgeList => { 
        fridgeListData = theFridgeList.json();
      })
      .catch(error => console.error('Error:', error));
      console.log(fridgeListData);

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
  }
  
  
// this is giving an error
// const updateButton = document.querySelector('.updateButton');
// updateButton.addEventListener('click', () => {
//   let listData = JSON.parse(localStorage.getItem(listParam) || '[]');
//   console.log('Retrieved listData:', listData);

//   const items = document.querySelectorAll('.grocery-list .item');
//   console.log(items);

//   items.forEach((item, index) => {
//     const updatedNameElement = item.querySelector('.inputBox');
//     const updatedName = updatedNameElement ? updatedNameElement.value : '';

//     const updatedDateAddedElement = item.querySelector('.dateAdded');
//     const updatedDateAdded = updatedDateAddedElement ? updatedDateAddedElement.value : '';

//     const updatedDateExpireElement = item.querySelector('.dateExpire');
//     const updatedDateExpire = updatedDateExpireElement ? updatedDateExpireElement.value : '';

//     listData[index].name = updatedName;
//     listData[index].dateAdded = updatedDateAdded;
//     listData[index].dateExpire = updatedDateExpire;
//   });

//   console.log('Updated listData:', listData);

//   localStorage.setItem(listParam, JSON.stringify(listData));

//   window.location.reload();
// });
