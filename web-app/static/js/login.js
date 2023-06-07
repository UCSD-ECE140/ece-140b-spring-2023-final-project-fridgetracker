const theRegister = document.querySelector('#register');
const theLogin = document.querySelector('#login');
const theRegisterBtn = document.querySelector("#register_btn");
const theLoginBtn = document.querySelector("#login_btn");

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
            // console.log(response);
            if (callback)
                callback(response);
        })
        .catch(error => console.error('Error:', error));
}

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
/* Toggle Register/Login Popups */
// display register form
theRegisterBtn.addEventListener('click', function(){
    toggleDisplay(theRegister);
    hideButtons();
})
// display login form
theLoginBtn.addEventListener('click', function(){
    toggleDisplay(theLogin);
    hideButtons();
})
function toggleDisplay(element){
    element.style.display === 'block' ? element.style.display = 'none' : element.style.display = 'block';
}
function toggleSignUp(){
    toggleDisplay(theLogin);
    toggleDisplay(theRegister);
}
function hideButtons(){
    theRegisterBtn.style.display = 'none';
    theLoginBtn.style.display = 'none';
}

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
/* Handle Form Data from Registration/Login */
// unique data is formatted as [name], shared data with login is differentiated with [name]_[reg/log]

// handle registration
const theRegForm = document.querySelector('#register_form');
theRegForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const action = theRegForm.getAttribute("action");
    const method = theRegForm.getAttribute("method");
    const newUserInfo = Object.fromEntries(new FormData(theRegForm).entries());
    server_request(action, newUserInfo, method, function(response){
        if (response['status'] == 'error'){
            alert('Sorry, there was an error with your registration. Please try again.');
        }
        else {
            alert(`Welcome ${response['first_name']}, please login to continue.`);
            toggleSignUp();
        }
    });
})

// handle login
const theLoginForm = document.querySelector('#login_form');
theLoginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const action = theLoginForm.getAttribute("action");
    const method = theLoginForm.getAttribute("method");
    const loginCredentials = Object.fromEntries(new FormData(theLoginForm).entries());
    console.log(loginCredentials);
    server_request(action, loginCredentials, method, function(response) {
        // redirect to profile/dashboard
        if (response['status'] == 'success'){
            window.location.replace('/');
        }
        else {
            console.log(response);
            alert('Sorry, there was an error with your login. Please try again.');
        }
    })
})