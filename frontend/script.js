let latestGeneratedPost = "";

// Fetch Profile data from backend
async function fetchProfile() {
    try {
        const res = await fetch('http://127.0.0.1:8000/profile');
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

// Generate LinkedIn post using backend AI
async function generatePost() {
    const prompt = document.getElementById("prompt").value.trim();
    const postType = document.getElementById("postType").value;
    const tone = document.getElementById("tone").value;
    const resultDiv = document.getElementById("result");

    if (!prompt) {
        resultDiv.innerHTML = "<b>Please enter a prompt.</b>";
        return;
    }
    resultDiv.innerHTML = " Generating post... Please wait.";

    const profile = await fetchProfile();

    const payload = {
        prompt: prompt,
        max_length: 200,
        post_type: postType,
        tone: tone,
        name: profile?.name || "",
        keywords: profile?.keywords || "",
        industry: profile?.industry || ""
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/generatepost", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        const data = await response.json();
        resultDiv.innerHTML = `<b>Generated Post:</b><br>${data["Generated Post"]}`;

        // Store the latestGeneratedPost for posting/scheduling
        latestGeneratedPost = data["Generated Post"];
        
        document.getElementById("linkedinBtn").disabled = false; // Enable LinkedIn post button
    } catch (error) {
        console.error(error);
        resultDiv.innerHTML = " Oops, Error: Could not connect to backend.";
    }
}

// Post the latest generated post to LinkedIn
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
    linkedinBtn.disabled = false; // Re-enable button
}

// Fetch industry news/articles from backend API
async function fetchIndustryNews() {
    const resultDiv = document.getElementById("newsResults");
    const industryInput = document.getElementById("industryKeyword");
    const keywordValue = industryInput ? industryInput.value.trim() : "";

    if (!keywordValue) {
        alert("Please enter an industry keyword.");
        return;
    }

    resultDiv.innerHTML = "Loading news...";

    try {
        const response = await fetch(`http://127.0.0.1:8000/industry-news?keyword=${encodeURIComponent(keywordValue)}`);
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<b>Error:</b> ${data.error}`;
            return;
        }
        if (!data.articles || !data.articles.length) {
            resultDiv.innerHTML = "No articles found.";
            return;
        }

        let html = "<ul style='list-style:none; padding-left:0;'>";
        data.articles.forEach(article => {
            html += `<li style="margin-bottom: 15px;">
                <a href="${article.url}" target="_blank" style="font-weight:bold; color:#0073b1;">${article.title}</a><br/>
                <small>${article.description || ''}</small><br/>
                <small><i>Source:</i> ${article.source} | <i>Published:</i> ${new Date(article.publishedAt).toLocaleString()}</small>
            </li>`;
        });
        html += "</ul>";

        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = "Failed to fetch news. Please try again later.";
        console.error(error);
    }
}


// Scheduling Post (Content Calendar)
async function schedulePost() {
    const content = document.getElementById("calendarPostContent").value.trim();
    const scheduledTimeStr = document.getElementById("calendarPostDateTime").value;

    if (!content || !scheduledTimeStr) {
        alert("Please enter post content and select a scheduled time.");
        return;
    }

    const scheduled_time = new Date(scheduledTimeStr);
    if (isNaN(scheduled_time)) {
        alert("Please enter a valid date and time.");
        return;
    }

    try {
        const response = await fetch("http://localhost:8000/schedulepost", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                content: content,
                scheduled_time: scheduled_time.toISOString()
            })
        });
        const data = await response.json();

        if (response.ok) {
            alert("Post scheduled successfully!");
            loadScheduledPosts();
            // Clear inputs after scheduling
            document.getElementById("calendarPostContent").value = "";
            document.getElementById("calendarPostDateTime").value = "";
        } else {
            const errorMsg = data.detail || data.message || JSON.stringify(data);
            console.log(data);
            alert("Error scheduling post: " + errorMsg);
        }
    } catch (error) {
        alert("Network error: " + error.message);
    }
}

// Viewing all Scheduled Posts (runs automatically on page load)
async function loadScheduledPosts() {
    try {
        const response = await fetch("http://localhost:8000/scheduledposts");
        const posts = await response.json();

        const list = document.getElementById("scheduledPostsList");
        if (!list) return;
        list.innerHTML = "";

        posts.forEach(post => {
            const li = document.createElement("li");
            li.textContent = `${new Date(post.scheduled_time).toLocaleString()}: ${post.content}`;
            list.appendChild(li);
        });
    } catch (error) {
        alert("Failed to load scheduled posts: " + error.message);
    }
}

// Fill generated post into scheduling textarea and focus datetime input
function fillScheduledPost() {
    document.getElementById("calendarPostContent").value = latestGeneratedPost;
    if (document.getElementById("calendarPostDateTime")) {
        document.getElementById("calendarPostDateTime").focus();
    }
}

// Show user profile summary on index.html
async function displayProfileOnIndex() {
    try {
        const res = await fetch('http://127.0.0.1:8000/profile');
        if (!res.ok) {
            document.getElementById('profileSummary').innerHTML = `
                <h3>Welcome!</h3>
                <p>No profile set. <a href="profile.html" style="color:#0073b1;">Set up your profile</a></p>
            `;
            return;
        }
        const data = await res.json();

        document.getElementById('profileSummary').innerHTML = `
            <h3>Welcome, ${data.name || 'User'}!</h3>
            <p><strong>Industry:</strong> ${data.industry || 'N/A'}</p>
            <p><strong>Keywords:</strong> ${data.keywords || 'N/A'}</p>
            <a href="profile.html" style="color:#0073b1;">Edit Profile</a>
        `;
    } catch {
        document.getElementById('profileSummary').innerHTML = `
            <h3>Welcome!</h3>
            <p>Profile unavailable.</p>
        `;
    }
}

// Initialization on page load for all pages
window.addEventListener('load', function() {

    // Display profile summary if the element exists
    if (document.getElementById('profileSummary')) {
        displayProfileOnIndex();
    }

    // Auto-fill industry news keyword input if exists
    if (document.getElementById('industryKeyword')) {
        autofillIndustryKeywords();
    }

    // Fill profile edit form if on profile.html
    if (document.getElementById('profileForm')) {
        (async function fillProfileForm() {
            try {
                const res = await fetch('http://127.0.0.1:8000/profile');
                if (!res.ok) return;
                const data = await res.json();
                document.getElementById('name').value = data.name || "";
                document.getElementById('keywords').value = data.keywords || "";
                document.getElementById('industry').value = data.industry || "";
            } catch {}
        })();
    }
});

// Profile form submission handling (for profile.html)
if (document.getElementById('profileForm')) {
    document.getElementById('profileForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const name = document.getElementById('name').value.trim();
        const keywords = document.getElementById('keywords').value.trim();
        const industry = document.getElementById('industry').value.trim();
        const messageDiv = document.getElementById('message');

        const profileData = { name, keywords, industry };

        messageDiv.innerText = "Profile saved! Redirecting to home...";
        try {
            const response = await fetch('http://127.0.0.1:8000/profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileData),
            });
            if (!response.ok) throw new Error('Failed to save profile.');
            setTimeout(() => {
                window.location.href = "index.html";
            }, 1200);
        } catch (error) {
            messageDiv.innerText = "Error: " + error.message;
        }
    });
}

// Auto-fill industry news keyword input on index.html or relevant pages
async function autofillIndustryKeywords() {
    const industryInput = document.getElementById("industryKeyword");
    if (!industryInput) return;

    try {
        const profile = await fetchProfile();
        if (profile) {
            const combined = [profile.industry, profile.keywords].filter(Boolean).join(" ");
            industryInput.value = combined;
        }
    } catch (e) {
        // silently ignore errors
    }
}
