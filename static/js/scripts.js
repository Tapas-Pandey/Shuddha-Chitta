function loadPosts() {
  fetch("/view_posts")
    .then((response) => response.json())
    .then((posts) => {
      const postsContainer = document.getElementById("postsContainer");
      postsContainer.innerHTML = "";
      posts.forEach((post) => {
        const postElement = document.createElement("div");
        postElement.className = "post";
        postElement.innerHTML = `
                  <p>${post.content}</p>
                  <button onclick="addReaction(${post.id})">❤️ ${
          post.reactions
        }</button>
                  <button onclick="confirmDeletePost(${
                    post.id
                  })" style="color: red;">Delete</button>
                  <div id="comments-${post.id}">
                      <input type="text" placeholder="Add a comment" id="commentInput-${
                        post.id
                      }" />
                      <button onclick="addComment(${
                        post.id
                      })">Post Comment</button>
                      <div class="comments">
                          ${post.comments
                            .map(
                              (comment) =>
                                `<p><strong>${comment.username}:</strong> ${comment.text}</p>`
                            )
                            .join("")}
                      </div>
                  </div>
              `;
        postsContainer.appendChild(postElement);
      });
    })
    .catch((error) => console.error("Error loading posts:", error));
}

document.getElementById("submitPost").addEventListener("click", function () {
  const postContent = document.getElementById("postContent").value;
  fetch("/create_post", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ content: postContent }),
  })
    .then((response) => {
      if (response.ok) {
        document.getElementById("postContent").value = ""; // Clear textarea
        loadPosts(); // Reload posts
      } else {
        console.error("Error creating post:", response);
      }
    })
    .catch((error) => console.error("Error creating post:", error));
});

function addReaction(postId) {
  fetch(`/add_reaction/${postId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        loadPosts(); // Reload posts to update reactions
      } else {
        console.error("Error adding reaction:", response);
      }
    })
    .catch((error) => console.error("Error adding reaction:", error));
}

function confirmDeletePost(postId) {
  if (confirm("Do you really want to delete this post?")) {
    deletePost(postId);
  }
}

function deletePost(postId) {
  fetch(`/delete_post/${postId}`, {
    method: "DELETE",
  })
    .then((response) => {
      if (response.ok) {
        loadPosts(); // Reload posts after deletion
      } else {
        console.error("Error deleting post:", response);
      }
    })
    .catch((error) => console.error("Error deleting post:", error));
}

function addComment(postId) {
  const commentInput = document.getElementById(`commentInput-${postId}`);
  const commentText = commentInput.value;

  if (!commentText) {
    alert("Comment cannot be empty!");
    return;
  }

  fetch("/add_comment", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ post_id: postId, text: commentText }),
  })
    .then((response) => {
      if (response.ok) {
        commentInput.value = ""; // Clear the comment input field
        loadPosts(); // Reload posts to show the new comment
      } else {
        console.error("Error adding comment:", response);
      }
    })
    .catch((error) => console.error("Error adding comment:", error));
}

// Load posts when the page is loaded
document.addEventListener("DOMContentLoaded", loadPosts);
