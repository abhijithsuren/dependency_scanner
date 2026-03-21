// Toggle Details
function toggle(btn, index) {
    const el = document.getElementById("details-" + index);

    if (!el) return;

    if (el.classList.contains("hidden")) {
        el.classList.remove("hidden");
        btn.innerText = "Hide details";
    } else {
        el.classList.add("hidden");
        btn.innerText = "View details";
    }
}


// Drag & Drop Setup
const dropArea = document.getElementById("drop-area");
const fileInput = document.getElementById("fileInput");
const uploadText = document.getElementById("upload-text");


// Prevent default drag behaviors (ONLY ONCE)
["dragenter", "dragover", "dragleave", "drop"].forEach(event => {
    dropArea.addEventListener(event, e => e.preventDefault());
});


// Drag Effects (UI Feedback)
["dragenter", "dragover"].forEach(event => {
    dropArea.addEventListener(event, () => {
        dropArea.classList.add("dragover"); // visual highlight
        dropArea.classList.add("active");   // popup effect
    });
});

["dragleave", "drop"].forEach(event => {
    dropArea.addEventListener(event, () => {
        dropArea.classList.remove("dragover");
        dropArea.classList.remove("active");
    });
});


//Handles File Drop
dropArea.addEventListener("drop", e => {
    const files = e.dataTransfer.files;

    if (files.length > 0) {
        fileInput.files = files;
        uploadText.innerText = files[0].name;
    }
});


//Handles Manual File Selection
fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        uploadText.innerText = fileInput.files[0].name;
    }
});


// Auto scroll to results after page load
window.addEventListener("load", () => {
    const results = document.getElementById("results");

    if (results) {
        results.scrollIntoView({ behavior: "smooth" });
    }
});