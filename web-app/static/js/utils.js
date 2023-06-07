////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      Helper functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////


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

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      CreateRecipe.html
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// onload function for CreateRecipe.html
// checks device and handles barcode scanning/desktop manual adding
function createRecipe(){
  // Check if the device has a physical keyboard
  const input = document.getElementById("myInput");
  const hasPhysicalKeyboard = !(navigator.maxTouchPoints > 0 || window.matchMedia('(pointer: coarse)').matches);

  if (hasPhysicalKeyboard) {
    input.addEventListener("keydown", function(event) {
      // Handle keydown event
      console.log("Key pressed: " + event.key);
    });
    addItem();
  } else {
    // Code to open virtual keyboard or handle keyboard input in an alternative way
    fetchVideoFeed();
  }
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
      alert(`${name} added to ${listSelect}!`);

      // Redirect home
      window.location.href = '/';
    })
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      HomeScreen.html
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// populates homepage section lists with db data -- used by HomeScreen.html
function populateData(){
  const sections = ['FridgeListS', 'CounterItemS', 'PantryItemS', 'ShoppingListS'];
  for (let i = 0; i < sections.length; i++) {
    get_list_from_db(sections[i]);
  }
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
      if (listName != 'ShoppingListS'){
        div.textContent = `${item[0]},  Expiry at ${expiry}`;
      } else {
        div.textContent = `${item[0]}`; // shopping list shouldnt have expiry dates
      }
      listDiv.appendChild(div);
    });
  })
  .catch(error => console.error('Error:', error));
}

function logout(){
  fetch ('/logout')
  .then(response => {
    window.location.href = '/';
  })
  .catch(error => console.error('Error:', error));
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      ViewRecipe.html
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// helper function to delete item and add to shopping list
async function deleteItem(itemName, listSection) {
  const confirmation = confirm(`Are you sure you want to delete ${itemName}?`);
  if (confirmation) {

    // create a new item object
    var date = new Date();
    date.setDate(new Date().getDate());
    date = date.toISOString().substring(0, 10);    
    const theItem = { "listTage": listSection, "itemName":itemName, "addedDate": date, "expiredDate":date};
    try {
      // delete the item from the db
      await server_request('/delete_item', theItem, 'DELETE');
      // alert(`${itemName} deleted from ${listSection}!`);

      // add automatic shopping list functionality
      if (listSection != 'ShoppingListS'){
        if (confirm(`Do you want to add ${itemName} to your Shopping List?`)){
          const theShoppingItem = { ...theItem, listTage: "ShoppingListS" };
          await server_request('/add_item', theShoppingItem, "POST", function(){
            alert(`${itemName} added to ShoppingListS!`);
          })
        }
      }
    } catch (error) {
      console.error('Error:', error);
    }
  }
}

// helper function for fetch GET route
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

// helper function to compare two items for update
async function compare_items(item1, item2){
  // console.log(item1, item2);
  if (item1 != item2){
    await server_request('/update_item', {'oldItem': item1, 'newItem': item2}, 'PUT', function(){});
  }
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
    // if (listParam !== 'ShoppingListS'){
    newItem.querySelector('.dateExpire').value = item[2].slice(0, 10);
    // }
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

  // add update button functionality
  const updateButton = document.querySelector('.updateButton');
  updateButton.addEventListener('click', async () => {

    // get item elements from page
    const items = document.querySelectorAll('.grocery-list .item');

    // compare the items
    // items.forEach((item, index) => {
    for (const [index, item] of items.entries()) {

      // get old item data
      const theItem = listData[index];
      let oldName = theItem[0];
      let oldAdded = theItem[1].substring(0, 10);
      let oldExpiry = theItem[2].substring(0, 10);

      // get updated item data: name, dateAdded, and dateExpire
      const updatedNameElement = item.querySelector('.inputBox');
      const updatedName = updatedNameElement ? updatedNameElement.value : '';
      const updatedDateAddedElement = item.querySelector('.dateAdded');
      const updatedAdded = updatedDateAddedElement ? updatedDateAddedElement.value : '';
      const updatedDateExpireElement = item.querySelector('.dateExpire');
      const updatedExpire = updatedDateExpireElement ? updatedDateExpireElement.value : '';

      // create items for easier comparison
      const theOldItem = { "listTage": listParam, "itemName":oldName, "addedDate": oldAdded, "expiredDate":oldExpiry};
      const theNewItem = { "listTage": listParam, "itemName":updatedName, "addedDate": updatedAdded, "expiredDate":updatedExpire};
      
      // compare item information-- if any fields changed, then send server_request to update item
      await compare_items(theOldItem, theNewItem);
    }

    // reload the page after all items are checked and updated
    window.location.reload();
  });
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      Camera Functions
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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
  
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//      color them
////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function toggleTheme() {
  const root = document.documentElement;
  const logoImg = document.querySelector('.fridgelogo');
  const themeCheckbox = document.getElementById('theme-checkbox');
  const deleteBtn = document.querySelector('.deleteButton')
  const deleteBtnIcon = deleteBtn.querySelector('.delete');
  const addBtn = document.querySelector('.deleteButton');
  const addBtnIcon = addBtn.querySelector('.add');
  const textElements = document.querySelectorAll('.Item .group1 .Text');

  if (themeCheckbox.checked) { // Dark theme is selected
    // change root color values
    root.style.setProperty('--fridge-dark', '#000000');
    root.style.setProperty('--fridge-medium-dark', '#333333');
    root.style.setProperty('--fridge-medium', '#666666');
    root.style.setProperty('--fridge-medium-light', '#999999');
    root.style.setProperty('--fridge-light', '#CCCCCC');
    root.style.setProperty('--fridge-Item', '#faeadc');
    // set text color to light
    textElements.forEach(element => {
      element.style.color = 'var(--fridge-Item)';
    })
    // set icons to light
    deleteBtnIcon.src = '../static/img/trash_light.png';
    addBtnIcon.src = '../static/img/add_light.png';
    // change background color
    root.style.setProperty('background-color', 'var(--fridge-dark)'); 
    // logoImg.src = '../static/img/logo_fr.jpg'; // Change the logo for dark mode
  } else { // Light theme is selected
    // change root color values
    root.style.setProperty('--fridge-dark', '#37251b');
    root.style.setProperty('--fridge-medium-dark', '#80411e');
    root.style.setProperty('--fridge-medium', '#ad6e2f');
    root.style.setProperty('--fridge-medium-light', '#d49961');
    root.style.setProperty('--fridge-light', '#e4bc84');
    root.style.setProperty('--fridge-Item', '#faeadc');
    // set text color to dark
     
    // set icons to dark
    deleteBtnIcon.src = '../static/img/trash_dark.png';
    addBtnIcon.src = '../static/img/add_dark.png';
    // change background color
    root.style.setProperty('background-color', 'var(--fridge-Item)'); 
    logoImg.src = '../static/img/logo.png'; // Change the image logo for light mode
  }
}




////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//     Junk yard
////////////////////////////////////////////////////////////////////////////////////////////////////////////////

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