let latestGeneratedPost = "";

// Generate LinkedIn post using backend AI
async function generatePost() {
    const prompt = document.getElementById("prompt").value;
    const postType = document.getElementById("postType").value;
    const tone = document.getElementById("tone").value;

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
                prompt: prompt,          //  match backend parameter
                max_length: 200,          //  optional, backend will default if missing
                post_type: postType,
                tone: tone
            })
        });
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        const data = await response.json();
        resultDiv.innerHTML = `<b>Generated Post:</b><br>${data["Generated Post"]}`;

        // Store the latestGeneratedPost (optional if using in postToLinkedIn)
        latestGeneratedPost = data["Generated Post"];
        
        document.getElementById("linkedinBtn").disabled = false; // Allow posting
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
    linkedinBtn.disabled = false; // Enable button again
}

// Fetch industry news/articles from backend API
async function fetchIndustryNews() {
    const keyword = document.getElementById("industryKeyword").value.trim();
    if (!keyword) {
        alert("Please enter an industry keyword.");
        return;
    }
    const resultDiv = document.getElementById("newsResults");
    resultDiv.innerHTML = "Loading news...";
    try {
        const response = await fetch(`http://localhost:8000/industry-news?keyword=${encodeURIComponent(keyword)}`);
        const data = await response.json();
        if (data.error) {
            resultDiv.innerHTML = `<b>Error:</b> ${data.error}`;
            return;
        }
        if (!data.articles.length) {
            resultDiv.innerHTML = "No articles found.";
            return;
        }
        let html = `<h4>News on '${data.keyword}':</h4><ul>`;
        data.articles.forEach(article => {
            html += `
                <li>
                    <a href="${article.url}" target="_blank">${article.title}</a>
                    <p>${article.description || ""}</p>
                    <small>Source: ${article.source} | Published: ${new Date(article.publishedAt).toLocaleString()}</small>
                </li>
            `;
        });
        html += "</ul>";
        resultDiv.innerHTML = html;
    } catch (error) {
        resultDiv.innerHTML = `<b>Error fetching news:</b> ${error.message}`;
    }
}


// Scheduling Post (Content Calender)

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

// Viewing all Scheduled Posts. ( It runs automatically when the page finishes loading.)

async function loadScheduledPosts() {
  try {
    const response = await fetch("http://localhost:8000/scheduledposts");
    const posts = await response.json();

    const list = document.getElementById("scheduledPostsList");
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
// Load posts on page load ( It runs automatically when the page finishes loading.)
window.onload = loadScheduledPosts;

// <!-- Filling the Generated Post to Scheduling Post Text Area-->
function fillScheduledPost() {
  document.getElementById("calendarPostContent").value = latestGeneratedPost;
  document.getElementById("calendarPostDateTime").focus();
}
