const form = document.getElementById("downloadForm");
const urlInput = document.getElementById("url");
const qualitySelect = document.getElementById("quality");
const button = document.getElementById("downloadButton");
const status = document.getElementById("status");
const pasteBtn = document.getElementById("pasteButton");

const videoPreview = document.getElementById("videoPreview");
const previewThumbnail = document.getElementById("previewThumbnail");
const previewTitle = document.getElementById("previewTitle");
const previewAuthor = document.getElementById("previewAuthor");
const previewDuration = document.getElementById("previewDuration");

let debounceTimer = null;

// Format duration helper
function formatDuration(seconds) {
    if (!seconds) return "";
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
        return `${hrs}:${mins < 10 ? "0" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
    }
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

// Paste button helper
if (pasteBtn && navigator.clipboard) {
    pasteBtn.addEventListener("click", async () => {
        try {
            const text = await navigator.clipboard.readText();
            if (text) {
                urlInput.value = text.trim();
                triggerInfoFetch(urlInput.value);
            }
        } catch (err) {
            console.warn("Clipboard access denied or not supported:", err);
            status.textContent = "Please paste the URL manually.";
        }
    });
}

// Fetch video preview info
async function fetchPreview(url) {
    if (!url || (!url.includes("youtube.com") && !url.includes("youtu.be") && !url.includes("instagram.com"))) {
        videoPreview.classList.add("hidden");
        return;
    }

    try {
        const res = await fetch(`/api/info?url=${encodeURIComponent(url)}`);
        if (!res.ok) return;

        const data = await res.json();
        if (data && data.title) {
            previewTitle.textContent = data.title;
            previewAuthor.textContent = data.uploader || "";
            previewThumbnail.src = data.thumbnail || "";
            previewDuration.textContent = formatDuration(data.duration);
            previewDuration.style.display = data.duration ? "inline-block" : "none";
            videoPreview.classList.remove("hidden");
        }
    } catch (_) {
        videoPreview.classList.add("hidden");
    }
}

function triggerInfoFetch(url) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchPreview(url);
    }, 400);
}

urlInput.addEventListener("input", (e) => {
    triggerInfoFetch(e.target.value.trim());
});

urlInput.addEventListener("paste", () => {
    setTimeout(() => {
        triggerInfoFetch(urlInput.value.trim());
    }, 100);
});

// Download Submission
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = urlInput.value.trim();
    const quality = qualitySelect.value;

    if (!url) {
        status.textContent = "Please enter a valid video URL.";
        return;
    }

    button.disabled = true;
    button.querySelector(".btn-text").textContent = "Processing & Downloading...";
    status.style.color = "#cbd5e1";
    status.textContent = "Connecting to server and processing media stream...";

    try {
        const response = await fetch("/api/download", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url,
                quality: quality
            })
        });

        if (!response.ok) {
            let message = "Download failed.";
            try {
                const error = await response.json();
                message = error.detail || message;
            } catch (_) {}
            throw new Error(message);
        }

        status.textContent = "Download complete! Saving to your device...";

        // Extract real filename from Content-Disposition header
        let filename = quality === "audio" ? "audio.mp3" : "video.mp4";
        const disposition = response.headers.get("Content-Disposition");
        if (disposition && disposition.includes("filename=")) {
            const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
            if (match && match[1]) {
                filename = match[1].replace(/['"]/g, "").trim();
            }
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        status.style.color = "#4ade80";
        status.textContent = `✓ Successfully downloaded: ${filename}`;

    } catch (error) {
        console.error(error);
        status.style.color = "#f87171";
        status.textContent = error.message || "Something went wrong. Please check the URL and try again.";
    } finally {
        button.disabled = false;
        button.querySelector(".btn-text").textContent = "Download Now";
    }
});