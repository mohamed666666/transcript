const startRecordButton = document.getElementById("start-record");
const stopRecordButton = document.getElementById("stop-record");
const transcriptionText = document.getElementById("transcription-text");
const translationText = document.getElementById("translation-text");
const sourceLanguageDropdown = document.getElementById("source");
const targetLanguageDropdown = document.getElementById("target");
const fileUploadButton = document.getElementById("file-upload");
const transcribeButton = document.getElementById("transcribe-button");
const fileTranscription = document.getElementById("file-transcription");
const mediaUpload = document.getElementById("media-upload");
const mediaPlayerContainer = document.getElementById("media-player-container");
const mediaPlayer = document.getElementById("media-player");

// Get a reference to the night mode button and the body element
const nightModeButton = document.getElementById('nightModeButton');
const body = document.body;

// Function to toggle night mode
function toggleNightMode() {
  body.classList.toggle('night-mode');
}

// Add a click event listener to the night mode button
nightModeButton.addEventListener('click', toggleNightMode);

// Initialize the SpeechRecognition API
const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
// const recognition = new window.SpeechRecognition();

let isTranscriptionDelayed = false; // Variable to track translation delay
let isTranslationDelayed = false; // Variable to track translation delay
// 2000
const translationDelayDuration = 2000; // 3 seconds delay (adjust as needed)
// 500
const transcriptionDelayDuration = 2000; // 3 seconds delay (adjust as needed)

// Set recognition options
recognition.continuous = true;
recognition.interimResults = true;

// Function to set recognition language based on source dropdown
function setRecognitionLanguage() {
    const sourceLang = sourceLanguageDropdown.value;
    recognition.lang = sourceLang;
}

// Event listener to update recognition language when source language changes
sourceLanguageDropdown.addEventListener("change", () => {
    setRecognitionLanguage();
    // Get the selected source language after the change
    const sourceLang = sourceLanguageDropdown.value;targetLanguageDropdown
});

// Event listener to update target language when target language changes
targetLanguageDropdown.addEventListener("change", () => {
    // Get the selected target language after the change
    const targetLang = targetLanguageDropdown.value;

    // You can use the targetLang value as needed
});


function translateText(text, targetLanguage) {
    if (text.trim() === '') {
        // Handle empty text input (e.g., when starting the application)
        console.log('Translation skipped: Empty text');
        return;
    }

    fetch('translate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCSRFToken(),
        },
        body: `text=${encodeURIComponent(text)}&target_language=${targetLanguage}`,
    })
    .then((response) => response.json())
    .then((data) => {
        if (data.translated_text) {
            translationText.textContent = data.translated_text;
        } else {
            console.error('Translation failed.');
        }
    })
    .catch((error) => {
        console.error('Translation error:', error);
    });
}

let isRecording = false; // Add this variable to track recording state
let latestSentence = ''; // Variable to store the latest sentence
let translatedText = '';

startRecordButton.addEventListener("click", () => {
    if (!isRecording) { // Check if not already recording
        setRecognitionLanguage(); // Set language before starting recognition
        isRecording = true;
        recognition.start();
        transcription = ""; // Clear existing transcription when starting a new recording
        startRecordButton.disabled = true;
        stopRecordButton.disabled = false;
    }
});

stopRecordButton.addEventListener("click", () => {
    if (isRecording) { // Check if currently recording
        isRecording = false;
        recognition.stop();
        startRecordButton.disabled = false;
        stopRecordButton.disabled = true;
    }
});


recognition.onend = () => {
    if (isRecording) { // Check if it should be restarted
        recognition.start();
    }
};


let transcription = "";

recognition.onresult = (event) => {
    let transcription = "";
    if (!isTranscriptionDelayed) {
        isTranscriptionDelayed = true;
        const sourceLang = sourceLanguageDropdown.value;
        const targetLang = targetLanguageDropdown.value;
        
        setTimeout(() => {
            // Check if the silence duration is within the threshold
            for (const result of event.results) {
                if (result.isFinal) {    
                    transcription += result[0].transcript.trim() + ' ';
                } else if (result[0].transcript.trim() !== '') {
                    transcription += result[0].transcript.trim() + ' ';
                }
            }
            translateText(transcription, targetLang);            
            
            
            // Check if sourceLang is not Arabic before applying NER highlighting
            if (sourceLang !== "ar-EG") {
                fetch('/ner_highlight/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRFToken(), // Replace with actual CSRF token retrieval
                    },
                    body: `text=${encodeURIComponent(transcription)}&language=${sourceLang}`,
                })
                .then((response) => response.json())
                .then((data) => {
                    console.log('Response data:', data); // Add this line for debugging

                    if (data.highlighted_text) {
                        // Check for words like "didn't" and replace the space after the apostrophe with a non-breaking space
                        let highlightedText = data.highlighted_text.replace(/\s'(\w)/g, "'$1").replace(/\sn't/g, "n't").replace(/<\s*br\s*>/g, "<br>");

                        // Update transcriptionText directly with highlighting
                        transcriptionText.innerHTML = highlightedText;
                    }
                })
                .catch((error) => {
                    console.error('NER and highlighting error:', error);
                });
            }
            else {
                transcriptionText.innerHTML = transcription;
            }
            
            isTranscriptionDelayed = false;
        }, transcriptionDelayDuration);
    }
};

// Event listener for media upload
mediaUpload.addEventListener("change", () => {
    const file = mediaUpload.files[0];
    if (file) {
        mediaPlayer.src = URL.createObjectURL(file);
        mediaPlayerContainer.style.display = "block";
    }
});

// Function to get CSRF token (replace with your actual implementation)
function getCSRFToken() {
    const csrfCookie = document.cookie
        .split('; ')
        .find((cookie) => cookie.startsWith("csrftoken="));

    if (csrfCookie) {
        return csrfCookie.split('=')[1];
    }

    return "";
}

fileUploadButton.addEventListener("change", handleFileUpload);

function handleFileUpload() {
    const fileInput = fileUploadButton; // Reference the file input directly

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];

        // Create a FormData object to send the file
        const formData = new FormData();
        formData.append("audio", file);

        // Send the audio file to the server for transcription
        transcribeAudio(formData)
            .then((transcription) => {
                fileTranscription.innerHTML = transcription;
                //fileTranscription.textContent = transcription;
            })
            .catch((error) => {
                console.error("Transcription error:", error);
                fileTranscription.textContent = "Transcription failed.";
            });
    }
}

transcribeButton.addEventListener("click", () => {
    fileUploadButton.click(); // Trigger a click event on the hidden file input
});

function transcribeAudio(formData) {
    return new Promise((resolve, reject) => {
        // Make an AJAX POST request to the server to transcribe the audio
        fetch("/transcribe_audio/", {
            method: "POST",
            headers: {
                'X-CSRFToken': getCSRFToken(), // Include the CSRF token in the headers
            },
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.transcription) {
                    resolve(data.transcription);
                } else {
                    reject(new Error("Transcription failed."));
                }
            })
            .catch((error) => {
                reject(error);
            });
    });
}