
let latestGeneratedPost = "";


async function generatePost() {
    const prompt = document.getElementById("prompt").value;
    const resultDiv = document.getElementById("result");

    if (!prompt.trim()) {
        resultDiv.innerHTML = "<b>Please enter a prompt.</b>";
        return;
    }

    resultDiv.innerHTML = " Generating post... Please wait.";

    try {
        const response = await fetch("http://127.0.0.1:8000/generatepost", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                prompt: prompt,     //  match backend parameter
                max_length: 200     //  optional, backend will default if missing
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();
        resultDiv.innerHTML = `<b>Generated Post:</b><br>${data["Generated Post"]}`;
    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = " Oops, Error: Could not connect to backend.";
    }

}

async function postToLinkedIn() {
    const linkedinBtn = document.getElementById("linkedinBtn");
    const resultDiv = document.getElementById("result");

    if (!latestGeneratedPost.trim()) {
        resultDiv.innerHTML += "<br><b>No post to publish. Generate one first!</b>";
        return;
    }

    linkedinBtn.disabled = true; // Disable button to prevent double click
    resultDiv.innerHTML += "<br>Posting to LinkedIn...";

    try {
        const response = await fetch("http://127.0.0.1:8000/linkedin/post", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ text: latestGeneratedPost })
        });

        const data = await response.json();

        if (response.ok) {
            resultDiv.innerHTML += "<br><b>Successfully posted to LinkedIn!</b>";
        } else {
            resultDiv.innerHTML += `<br><b>Error:</b> ${JSON.stringify(data.detail)}`;
        }
    } catch (error) {
        resultDiv.innerHTML += "<br><b>Network error posting to LinkedIn.</b>";
    }

    linkedinBtn.disabled = false; // Enable button again
}
