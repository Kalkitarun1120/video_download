const form =
    document.getElementById("downloadForm");

const button =
    document.getElementById("downloadButton");

const status =
    document.getElementById("status");


form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        const url =
            document.getElementById("url").value.trim();

        const quality =
            document.getElementById("quality").value;


        if (!url) {

            status.textContent =
                "Please enter a YouTube URL.";

            return;
        }


        button.disabled = true;

        button.textContent =
            "Downloading...";

        status.textContent =
            "Preparing your download...";


        try {

            const response =
                await fetch("/api/download", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        url: url,
                        quality: quality
                    })

                });


            if (!response.ok) {

                let message =
                    "Download failed.";

                try {

                    const error =
                        await response.json();

                    message =
                        error.detail ||
                        message;

                } catch (_) {}

                throw new Error(message);
            }


            status.textContent =
                "Download completed. Preparing file...";


            const blob =
                await response.blob();


            const downloadUrl =
                window.URL.createObjectURL(blob);


            const link =
                document.createElement("a");

            link.href =
                downloadUrl;

            let filename = "video.mp4";
            const disposition = response.headers.get("Content-Disposition");
            if (disposition && disposition.includes("filename=")) {
                const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (match && match[1]) {
                    filename = match[1].replace(/['"]/g, "").trim();
                }
            }

            link.download = filename;

            document.body.appendChild(link);

            link.click();

            link.remove();

            window.URL.revokeObjectURL(
                downloadUrl
            );


            status.textContent =
                "Download completed successfully ✓";


        } catch (error) {

            console.error(error);

            status.textContent =
                error.message ||
                "Something went wrong.";

        } finally {

            button.disabled = false;

            button.textContent =
                "Download Video";
        }

    }
);