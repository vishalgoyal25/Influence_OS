
// Automatically switch backend URL based on where frontend is running

let BACKEND_URL;
if (window.location.hostname === "localhost") {
    BACKEND_URL = "http://localhost:8000"; // Local backend
} else {
    BACKEND_URL = "https://influence-os-dovy.onrender.com"; // Deployed backend
}
