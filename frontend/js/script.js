let context = "";
let uploadedFilePath = null; // Global variable to store the uploaded file path

// File upload functionality
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('document-file');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please upload a file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (result.status === 'success') {
            uploadedFilePath = result.file_path; // Save the file path for later use
            document.getElementById('upload-status').innerText = "File uploaded successfully!";
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error uploading file:", error);
        alert("An error occurred while uploading the file.");
    }
});

// Question answering functionality
document.getElementById('question-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const questionInput = document.getElementById('user-question');
    const question = questionInput.value;
    if (!question) {
        alert("Please enter a question.");
        return;
    }

    if (!uploadedFilePath) {
        alert("Please upload a document first.");
        return;
    }

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, file_path: uploadedFilePath }),
        });

        const result = await response.json();
        if (result.status === 'success') {
            const qaContainer = document.getElementById('qa-container');

            // Display the answer in a container
            const answerContainer = document.createElement('div');
            answerContainer.classList.add('answer-container');
            answerContainer.innerHTML = `<p><strong>Answer:</strong> ${result.answer}</p>`;
            qaContainer.appendChild(answerContainer);

            // Add follow-up prompt with Yes/No buttons
            const followUpContainer = document.createElement('div');
            followUpContainer.classList.add('follow-up-buttons');
            followUpContainer.innerHTML = `
                <p>Should I tell the risk factors of this and give suggestions for making it better?</p>
                <button id="yes-button" class="btn btn-success">Yes</button>
                <button id="no-button" class="btn btn-danger">No</button>
            `;
            qaContainer.appendChild(followUpContainer);

            // Handle Yes button
            document.getElementById('yes-button').addEventListener('click', async () => {
                const riskResponse = await fetch('/detect-risks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file_path: uploadedFilePath }),
                });

                const riskResult = await riskResponse.json();
                if (riskResult.status === 'success') {
                    const riskContainer = document.createElement('div');
                    riskContainer.classList.add('risk-container');
                    riskContainer.innerHTML = `<p><strong>Risks:</strong> ${riskResult.analysis}</p>`;
                    qaContainer.appendChild(riskContainer);
                } else {
                    alert(riskResult.message);
                }
            });

            // Handle No button
            document.getElementById('no-button').addEventListener('click', () => {
                const noResponseContainer = document.createElement('div');
                noResponseContainer.classList.add('no-response-container');
                noResponseContainer.innerHTML = `
                    <p>It would be good if you check the risk factors of your resume. Click on Yes, and I will provide you with the risk factors.</p>
                `;
                qaContainer.appendChild(noResponseContainer);
            });
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error asking question:", error);
        alert("An error occurred while processing your question.");
    }
});

// Function to upload a file
async function uploadFile() {
    const fileInput = document.getElementById('pdfFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    const response = await fetch('/upload', { method: 'POST', body: formData });
    const data = await response.json();
    if (data.status === "success") {
        context = data.text;
        alert('File uploaded and content extracted successfully!');
    } else {
        alert(`Error: ${data.message}`);
    }
}

// Function to ask a question
async function askQuestion() {
    const question = document.getElementById('question').value;
    if (!context) {
        alert("Please upload a document first!");
        return;
    }
    if (!question) {
        alert("Please enter a question!");
        return;
    }
    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context, question }),
    });
    const data = await response.json();
    addQuestionAnswer(question, data.answer || "No answer found.");
    document.getElementById('question').value = ""; // Clear the question input
}

// Function to add a question-answer pair to the UI
function addQuestionAnswer(question, answer) {
    const qaContainer = document.getElementById('qa-container');
    const qaItem = document.createElement('div');
    qaItem.classList.add('qa-item');

    // Split the answer into points based on newlines
    const points = answer.split('\n').filter(point => point.trim() !== '');

    // Create a list for the points
    const pointsList = points.map(point => `<li>${point}</li>`).join('');

    qaItem.innerHTML = `
        <p><strong>Question:</strong> ${question}</p>
        <p><strong>Answer:</strong></p>
        <ul>${pointsList}</ul>
    `;
    qaContainer.appendChild(qaItem);
}

// Event listener for setting reminders
document.getElementById('assistant-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const task = document.getElementById('task').value;
    const time = document.getElementById('time').value;
    const email = document.getElementById('email').value;

    const response = await fetch('/set-reminder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, time, email }),
    });

    const result = await response.json();
    alert(result.message);
});

async function compareDocuments() {
    const firstDoc = document.getElementById('firstDoc').files[0];
    const secondDoc = document.getElementById('secondDoc').files[0];

    if (!firstDoc || !secondDoc) {
        alert('Please upload both documents!');
        return;
    }

    const formData = new FormData();
    formData.append('firstDoc', firstDoc);
    formData.append('secondDoc', secondDoc);

    const response = await fetch('/compare', { method: 'POST', body: formData });
    const data = await response.json();

    if (data.status === 'success') {
        displayComparisonResults(data.similarities, data.differences);
    } else {
        alert(`Error: ${data.message}`);
    }
}

function displayComparisonResults(similarities, differences) {
    const comparisonResults = document.getElementById('comparison-results');

    // Separate differences into 1st document and 2nd document
    const firstDocDifferences = differences.firstDoc || [];
    const secondDocDifferences = differences.secondDoc || [];

    comparisonResults.innerHTML = `
        <h3>Similarities:</h3>
        <ul>${similarities.map(sim => `<li>${sim}</li>`).join('')}</ul>
        <h3>Differences:</h3>
        <div class="differences-container">
            <div class="doc-differences">
                <h4>1st Document:</h4>
                <ul>${firstDocDifferences.map(diff => `<li>${diff}</li>`).join('')}</ul>
            </div>
            <div class="doc-differences">
                <h4>2nd Document:</h4>
                <ul>${secondDocDifferences.map(diff => `<li>${diff}</li>`).join('')}</ul>
            </div>
        </div>
    `;
}

function showFileName(inputId, displayId) {
    const fileInput = document.getElementById(inputId);
    const fileNameDisplay = document.getElementById(displayId);

    if (fileInput.files.length > 0) {
        fileNameDisplay.textContent = `Uploaded: ${fileInput.files[0].name}`;
    } else {
        fileNameDisplay.textContent = '';
    }
}

async function recordVoice() {
    if (!navigator.mediaDevices || !window.MediaRecorder) {
        alert("Your browser does not support voice recording.");
        return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        const response = await fetch('/transcribe', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.status === 'success') {
            document.getElementById('question').value = data.transcription; // Set the transcribed text in the textarea
        } else {
            alert(`Error: ${data.message}`);
        }
    };

    mediaRecorder.start();
    alert("Recording... Click OK to stop.");
    setTimeout(() => mediaRecorder.stop(), 5000); // Automatically stop recording after 5 seconds
}

function redirectToAskAnything() {
    window.location.href = '/ask-anything';
}

async function askGeneralQuestion() {
    const question = document.getElementById('general-question').value;
    if (!question) {
        alert("Please enter a question!");
        return;
    }

    const response = await fetch('/general-question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
    });

    const data = await response.json();
    if (data.status === 'success') {
        addChatMessage('You', question);
        addChatMessage('Chatbot', data.answer);
        document.getElementById('general-question').value = ''; // Clear the input
    } else {
        alert(`Error: ${data.message}`);
    }
}

function addChatMessage(sender, message) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender === 'You' ? 'user' : 'bot');

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.innerText = message;

    messageElement.appendChild(messageContent);
    chatContainer.appendChild(messageElement);

    // Scroll to the bottom of the chat container
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

document.getElementById('news-btn').addEventListener('click', async () => {
    const response = await fetch('/read-news');
    const news = await response.json();
    alert(news.articles.join('\n'));
});

document.getElementById('document-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('document-file');
    const file = fileInput.files[0];
    if (!file) {
        alert("Please upload a file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/analyze-document', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (result.status === 'success') {
            document.getElementById('analysis-result').innerHTML = `
                <h4>Analysis Results:</h4>
                <p>${result.analysis}</p>
            `;
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error("Error analyzing document:", error);
        alert("An error occurred while analyzing the document.");
    }
});