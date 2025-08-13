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
