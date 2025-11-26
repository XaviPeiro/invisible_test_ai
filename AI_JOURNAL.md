We will develop an 3 components application: the backend, the frontend and the infrastructure definitions (IAC, mainly with Terraform).

We'll be taking one part at once.

Let's start planning the backend. I will be provinding the different features.

# BACKEND
1. Python Backend Service using a SQL database.
    1. API supporting the behaviors.

# BEHAVIOUR
1. User sign up
2. Authentication for existing user
3. User profile management
4. View user’s groups
5. Group management
  a. Add group
  b. Add user to group as member
6. Expense management
  a. Add expense for group (paying user and amount + any metadata)
  b. View expense history
  c. Summarize balance by amount owed to members (assuming equal share in each
  expense)

