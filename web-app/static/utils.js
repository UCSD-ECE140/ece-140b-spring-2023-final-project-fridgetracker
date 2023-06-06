// request function for handling interactions with the server
// note: this has error when calling GET so use fetch instead
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


// add items to local storage connected to db using server routes -- used by CreateRecipe.html
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


// populates homepage section lists with db data -- used by HomeScreen.html
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

// helper function for deleting item
// function deleteItem(itemName, listSection) {
//   const confirmation = confirm(`Are you sure you want to delete ${itemName}?`);
//   if (confirmation) {
//     // const theItem = { 'item': itemName, 'section': listSelect };
//     const theItem = { "listTage": listSection, "itemName":itemName, "addedDate": 0, "expiredDate":0};
//     console.log(theItem);
//     await server_request('/delete_item', theItem, 'DELETE', function () {
//       alert(`${itemName} deleted from ${listSection}!`);
//     });
//   }
// }
async function deleteItem(itemName, listSection) {
  const confirmation = confirm(`Are you sure you want to delete ${itemName}?`);
  if (confirmation) {
    const theItem = { "listTage": listSection, "itemName":itemName, "addedDate": 0, "expiredDate":0};
    try {
      await server_request('/delete_item', theItem, 'DELETE');
      alert(`${itemName} deleted from ${listSection}!`);
    } catch (error) {
      console.error('Error:', error);
    }
  }
}

// helper function for fetch get route
async function fetch_list(section) {
  let listData = [];
  try {
    const response = await fetch(`/get_${section}_list`, { method: 'GET' });
    const theList = await response.json();
    listData = theList;
  } catch (error) {
    console.error('Error:', error);
  }
  return listData;
}


// populate individual/all sections in ViewRecipe.html
async function populateViewData() {
  // get section name from url
  const urlParams = new URLSearchParams(window.location.search);
  const listParam = urlParams.get('list');

  // update html title to match section
  const nameInput = document.querySelector('.tiltle');
  nameInput.value = listParam;
  let listData;

  // get items list from db
  listData = await fetch_list(listParam);

  // populate lists using template
  const groceryListDiv = document.querySelector('.grocery-list');
  const theItemTemplate = document.querySelector('#item_template');
  listData.forEach(item => {
    // insert element into section list
    groceryListDiv.insertAdjacentHTML('beforeend', theItemTemplate.innerHTML);

    // update element with item information
    let newItem = groceryListDiv.lastElementChild;
    newItem.querySelector('.inputBox').value = item[0];
    newItem.querySelector('.dateAdded').value = item[1].slice(0, 10);
    if (listParam !== 'ShoppingListS'){
      newItem.querySelector('.dateExpire').value = item[2].slice(0, 10);
    }
  });

  // delete checked items functionality
  let checkedItems = [];
  const deleteButton = document.querySelector('.deleteButton');
  deleteButton.addEventListener('click', async () => {

    // keep track of all checked items to delete
    const checkboxes = document.querySelectorAll('.itemCheckbox');
    checkboxes.forEach((checkbox, index) => {
      if (checkbox.checked) {
        const itemName = checkbox.parentElement.querySelector('.inputBox').value;
        checkedItems.push(itemName);
      }
    });
  
    // delete the checked items
    for (const itemName of checkedItems){
      await deleteItem(itemName, listParam);
    }

    // reload the page after the items are deleted
    location.reload();
  });
  
  // if (listParam === 'All') {
  //   // Delete items from individual lists
  //   // local storage version
  //   // const fridgeListData = JSON.parse(localStorage.getItem('FridgeListS') || '[]');
  //   // const counterItemListData = JSON.parse(localStorage.getItem('CounterItemS') || '[]');
  //   // const pantryItemListData = JSON.parse(localStorage.getItem('PantryItemS') || '[]');
  //   // const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');

  //   const deletedItems = [];

  //   checkedItems.forEach((index) => {
  //     if (index < fridgeListData.length) {
  //       const deletedItem = fridgeListData.splice(index - deletedItems.length, 1)[0];
  //       deletedItems.push({
  //         list: 'FridgeListS',
  //         item: deletedItem
  //       });
  //     } else if (index < fridgeListData.length + counterItemListData.length) {
  //       const deletedItem = counterItemListData.splice(index - fridgeListData.length - deletedItems.length, 1)[0];
  //       deletedItems.push({
  //         list: 'CounterItemS',
  //         item: deletedItem
  //       });
  //     } else if (index < fridgeListData.length + counterItemListData.length + pantryItemListData.length) {
  //       const deletedItem = pantryItemListData.splice(index - fridgeListData.length - counterItemListData.length - deletedItems.length, 1)[0];
  //       deletedItems.push({
  //         list: 'PantryItemS',
  //         item: deletedItem
  //       });
  //     } else {
  //       const deletedItem = shoppingListData.splice(index - fridgeListData.length - counterItemListData.length - pantryItemListData.length - deletedItems.length, 1)[0];
  //       deletedItems.push({
  //         list: 'ShoppingListS',
  //         item: deletedItem
  //       });
  //     }
  //   });

  //   // update local storage with new lists
  //   localStorage.setItem('FridgeListS', JSON.stringify(fridgeListData));
  //   localStorage.setItem('CounterItemS', JSON.stringify(counterItemListData));
  //   localStorage.setItem('PantryItemS', JSON.stringify(pantryItemListData));
  //   localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));

  //   deletedItems.forEach((deletedItem) => {
  //     const list = deletedItem.list;
  //     const item = deletedItem.item;

  //     const addToShoppingList = confirm(`Do you want to add "${item.name}" to the ShoppingListS?`);

  //     if (addToShoppingList) {
  //       const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
  //       shoppingListData.push(item);
  //       localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
  //     }

  //     const listData = document.querySelector('.grocery-list[data-list="' + list + '"]');
  //     if (listData) {
  //       listData.innerHTML = '';
  //     }
  //   });
  // } else {
  //   // Delete items from the selected list
  //   // const listData = JSON.parse(localStorage.getItem(listParam) || '[]');
  //   const deletedItems = [];

  //   checkedItems.forEach((index) => {
  //     const deletedItem = listData.splice(index - deletedItems.length, 1)[0];
  //     deletedItems.push(deletedItem);

  //     const addToShoppingList = confirm(`Do you want to add "${deletedItem.name}" to the ShoppingListS?`);

  //     if (addToShoppingList) {
  //       const shoppingListData = JSON.parse(localStorage.getItem('ShoppingListS') || '[]');
  //       shoppingListData.push(deletedItem);
  //       localStorage.setItem('ShoppingListS', JSON.stringify(shoppingListData));
  //     }
  //   });

  //   localStorage.setItem(listParam, JSON.stringify(listData));

  //   const listDataElement = document.querySelector('.grocery-list[data-list="' + listParam + '"]');
  //   if (listDataElement) {
  //     listDataElement.innerHTML = '';
  //   }
  // }
  
    // window.location.reload();
  }
  
  function fetchVideoFeed() {
    fetch('/enable_scan')
      .then(response => response.json())
      .then(data => {
        console.log(data);
        const queryString = Object.keys(data)
          .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
          .join('&');
        const redirectUrl = '/CreateRecipe.html?' + queryString;
        window.location.href = redirectUrl;
      })
      .catch(error => {
        console.error('Error:', error);
      });
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
// // });

// function fetchProductData(barcodeVal) {
//   url = '/barcode'

//   fetch(url, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ barcode: barcodeVal })
//   })
//     .then(response => response.json())
//     .then(data => {
//       // Handle the response from the server
//       console.log(data);

//       const queryString = Object.keys(data)
//         .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
//         .join('&');

//       // Construct the URL for the target page with the query string
//       const redirectUrl = '/CreateRecipe.html?' + queryString;

// // Redirect to the target page
// window.location.href = redirectUrl;

//     })
//     .catch(error => {
//       // Handle any errors that occurred during the request
//       console.error('Error:', error);
//     });

// }

// function openCamera() {
//   // Get the video element
//   const video = document.createElement('video');
//   video.setAttribute('class', 'camera');
//   video.style.width = '90%'; // Set the video width to 90% of the screen

//   // Check if the browser supports getUserMedia
//   if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
//     navigator.mediaDevices.getUserMedia({ video: true })
//       .then(function(stream) {
//         // Set the video source and start scanning
//         video.srcObject = stream;
//         video.play();
//         startBarcodeScanner();
//       })
//       .catch(function(error) {
//         console.error('Error accessing camera:', error);
//       });
//   } else {
//     console.error('getUserMedia not supported');
//   }

//   // Create a canvas element to render the scanned barcode
//   const canvas = document.createElement('canvas');
//   canvas.setAttribute('id', 'barcode-canvas');
//   canvas.style.display = 'none';

//   // Append the video and canvas elements to the document body
//   document.body.appendChild(video);
//   document.body.appendChild(canvas);
// }
// 


// function startBarcodeScanner() {
//   Quagga.init({
//     inputStream: {
//       name: 'Live',
//       type: 'LiveStream',
//       target: '#camera-preview',
//       constraints: {
//         facingMode: 'environment' // Use the back camera
//       },
//     },
//     decoder: {
//       readers: ['ean_reader'] // Specify the barcode type to scan (e.g., EAN)
//     }
//   }, function(err) {
//     if (err) {
//       console.error('Error initializing Quagga:', err);
//       return;
//     }
//     Quagga.start();
//   });

//   Quagga.onDetected(function(result) {
//     // Handle the detected barcode here
//     const barcode = result.codeResult.code;
//     console.log('Barcode detected:', barcode);
//     console.log(typeof(barcode));

//     // Fetch the product data from the API
//     fetchProductData(barcode);

//     // Stop the scanner after the first successful scan
//     Quagga.stop();
//   });

// }