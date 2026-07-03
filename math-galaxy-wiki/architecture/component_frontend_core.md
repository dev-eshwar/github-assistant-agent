# Frontend App Core Component

- **Source Files:**
  - [src/main.jsx](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/src/main.jsx)
  - [src/App.jsx](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/src/App.jsx)
  - [src/components/Header.jsx](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/src/components/Header.jsx)
  - [src/App.css](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/src/App.css)
  - [src/index.css](file:///C:/Users/eshcs/OneDrive/Desktop/Antigravity%20projects/githubrepo_assistant/math-galaxy/src/index.css)

## Responsibility

This component is the root of the React single-page application.
- `main.jsx` initializes the React DOM and mounts the application.
- `App.jsx` serves as the central state coordinator. It manages state transitions between the dashboard, lesson introduction, questions, and explanation views. It handles answer verification, updates streaks and star counts, and coordinates synchronizing state with the Express backend.
- `Header.jsx` displays the user navigation bar and summarizes current user progress details (total star count, streaks, and number of completed planets).
