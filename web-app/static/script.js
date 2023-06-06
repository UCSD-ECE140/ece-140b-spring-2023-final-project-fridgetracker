// Check if the browser is Safari on iOS
const isSafariOnIOS = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);

let stream; // Variable to store the camera stream

// Function to access the camera and start streaming
function startCameraStream() {
  // Get the video element
  const video = document.getElementById('camera-preview');

  // Check if the browser is Safari on iOS
  if (isSafariOnIOS) {
    // Request user permission to access the camera
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(function(streamObj) {
        stream = streamObj; // Store the camera stream
        // Set the video source and start streaming
        video.srcObject = stream;
      })
      .catch(function(error) {
        console.error('Error accessing camera:', error);
      });

    // Listen for the page visibility change event
    document.addEventListener('visibilitychange', handleVisibilityChange);
  } else {
    console.error('Camera streaming not supported on this browser.');
  }
}

// Function to handle page visibility change
function handleVisibilityChange() {
  // Check if the page is visible
  if (document.visibilityState === 'visible' && isSafariOnIOS) {
    // Restart the camera stream
    startCameraStream();
  }
}

// Start camera streaming when the page is loaded
window.addEventListener('load', startCameraStream);
