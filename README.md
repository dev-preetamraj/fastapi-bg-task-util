### Example background task in FastAPI

1. Polling example on frontend
   Get the `taskId` from the response and keep polling to check the status of task.

   ```js
   function pollForTaskStatus(taskId) {
     const interval = setInterval(async () => {
       try {
         const response = await fetch(`${API_URL}/status/${taskId}`);

         if (response.status === 404) {
           showError(
             `Task ${taskId} not found. The server may have restarted.`
           );
           clearInterval(interval);
           return;
         }

         if (!response.ok) {
           // Don't stop polling for general network errors, just log them
           console.error(`Polling error: HTTP status ${response.status}`);
           return;
         }

         const data = await response.json();

         if (data.status === "completed") {
           // --- Step 3: Task is complete, display the result ---
           clearInterval(interval);
           statusArea.classList.add("hidden");
           resultArea.classList.remove("hidden");
           resultData.textContent = JSON.stringify(data.result, null, 2);
         } else if (data.status === "processing") {
           // The task is still running, the loop will continue.
           console.log("Task is still processing...");
         } else {
           // Handle other statuses like 'failed' if you implement them
           showError(`Task failed or has an unknown status: ${data.status}`);
           clearInterval(interval);
         }
       } catch (error) {
         console.error("Error during polling:", error);
         showError("An error occurred while checking task status.");
         clearInterval(interval); // Stop polling on critical error
       }
     }, 3000); // Poll every 3 seconds
   }
   ```

### For Celery and Redis
- Spin up a redis instance
- Run the celery worker using `celery -A celery_worker.celery_app worker --loglevel=info`