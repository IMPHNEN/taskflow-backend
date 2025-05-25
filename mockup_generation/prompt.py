prompt_task = """
---

### Prompt for Lovable Agent – Website Mockup Request

**Objective:**  
Log in to Lovable using the provided email and password, then request a **website mockup** based on the given query and requirements.

---

### Step 1: Log In

- Go to the Lovable website.
- Use the credentials below to log in:

  - **Email:**'{email}'  
  - **Password:**'{password}'

**Important:** Do **not** use "Sign in with Google" or "Sign in with GitHub". Use only the Email and Password fields.

### Step 2: Sign in

- Click the Sign in Button
- Check if you are logged in by checking if there is the '{email}' in the top-right corner.

if you are not logged in, try to login again.

---

### Step 3: Submit the Mockup Request

- After logging in, locate the input field for mockup requests.
- Submit the following query:

{query}

---

### Step 4: Wait for the Draft

- Wait **180,000 milliseconds (180 seconds)** for the mockup draft to generate.
- If the draft is not ready, wait an additional **180,000 milliseconds**.
- Continue waiting in 180-second intervals until the mockup is ready.

---

### Step 5: Output the Result

  Once the mockup is ready:
- Click the **Publish** button (top-right corner).
- After that there will be a Popup in the top right corner, click on the **Publish** button in the popup.
- Wait **30,000 milliseconds (30 seconds)** for the mockup to be published.
- If successful, the button label will change from **Publish** to **Update**.
- **Return only the preview link** of the published mockup.

**Important:** The site will show you the website but ITS NOT PUBLISHED YET, you need to publish it first.
**Important:** Make sure to check if the website is published before returning the link.
**Important:** Do **not** include any additional text or context. Return only the preview link.

---

**Important Notes:**  
Ensure the submitted query is clear, design-focused, and suitable for a modern business homepage. Emphasize usability, aesthetic appeal, and functional clarity.  
If the input query is unclear or ambiguous, feel free to **rephrase it** to better guide the agentic system on Lovable toward generating an optimal mockup.

---
"""