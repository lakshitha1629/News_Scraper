function copyText(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    alert('Copied to clipboard!');
}

function downloadImage(imgUrl) {
    const link = document.createElement('a');
    link.href = imgUrl;
    link.download = imgUrl.split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

document.getElementById('scrapeForm').onsubmit = function (event) {
    event.preventDefault(); // Prevent form from submitting normally
    var submitBtn = document.getElementById('submitBtn');
    var stopBtn = document.getElementById('stopBtn');
    var progressBar = document.getElementById('progressBar');
    var progressBarFill = document.getElementById('progressBarFill');

    submitBtn.disabled = true; // Disable the submit button
    stopBtn.style.display = 'block'; // Show the stop button
    progressBar.style.display = 'block'; // Show the progress bar
    progressBarFill.style.width = '50%'; // Example to show progress

    var formData = new FormData(this);
    var xhr = new XMLHttpRequest();
    xhr.open(this.method, this.action, true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            submitBtn.disabled = false; // Enable the button
            stopBtn.style.display = 'none'; // Hide stop button
            progressBar.style.display = 'none'; // Hide progress bar
            document.querySelector('.articles').innerHTML = xhr.responseText; // Assuming response is HTML
        } else {
            console.error('Error occurred:', xhr.responseText);
        }
    };

    xhr.onerror = function () {
        console.error('Request failed');
    };

    xhr.send(formData);

    // Handle stop button
    stopBtn.onclick = function () {
        xhr.abort(); // Abort the request
        submitBtn.disabled = false;
        stopBtn.style.display = 'none';
        progressBar.style.display = 'none';
        alert('Scraping stopped by user.');
    };
};
