document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      // Prevent duplicate options when reloading
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Top content
        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Participants section (built with DOM methods to avoid HTML injection)
        const participantsDiv = document.createElement("div");
        participantsDiv.className = "participants";
        const participantsTitle = document.createElement("h5");
        participantsTitle.textContent = "Participants";
        participantsDiv.appendChild(participantsTitle);

        if (Array.isArray(details.participants) && details.participants.length > 0) {
          const ul = document.createElement("ul");
          details.participants.forEach((p) => {
            const li = document.createElement("li");
            const span = document.createElement("span");
            span.textContent = p;
            li.appendChild(span);

            // Create delete button
            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-participant-btn";
            deleteBtn.textContent = "✕";
            deleteBtn.type = "button";
            deleteBtn.title = `Remove ${p} from ${name}`;
            deleteBtn.addEventListener("click", async (e) => {
              e.preventDefault();
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(p)}`,
                  {
                    method: "DELETE",
                  }
                );

                if (response.ok) {
                  const result = await response.json();
                  messageDiv.textContent = result.message;
                  messageDiv.className = "success";
                  fetchActivities(); // Refresh the activities list
                } else {
                  const error = await response.json();
                  messageDiv.textContent = error.detail || "Failed to unregister";
                  messageDiv.className = "error";
                }

                messageDiv.classList.remove("hidden");
                setTimeout(() => {
                  messageDiv.classList.add("hidden");
                }, 5000);
              } catch (error) {
                messageDiv.textContent = "Failed to unregister. Please try again.";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
                console.error("Error unregistering:", error);
              }
            });

            li.appendChild(deleteBtn);
            ul.appendChild(li);
          });
          participantsDiv.appendChild(ul);
        } else {
          const noneP = document.createElement("p");
          noneP.className = "none";
          noneP.textContent = "No participants yet";
          participantsDiv.appendChild(noneP);
        }

        activityCard.appendChild(participantsDiv);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh the activities list
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
