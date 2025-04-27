Okay, let's create a GitHub Actions workflow file to run your backend (`pytest`) and frontend (`npm test`) tests automatically. This workflow will trigger on pushes to `main` and `develop`, and on pull requests targeting these branches.

**Steps:**

1.  **Create the Workflow File:** ✅

    - In the root of your project, create the directory path `.github/workflows/` if it doesn't already exist.
    - Inside `.github/workflows/`, create a new file named `ci-tests.yml`.

2.  **Add the Workflow Content:** ✅ Paste the following YAML content into `ci-tests.yml`:

```yaml
name: CI Tests (Backend & Frontend)

on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop
  workflow_dispatch: # Allows manual triggering

jobs:
  backend-tests:
    name: Run Backend Tests (Python)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend # Set default directory for backend steps

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install uv
        run: pip install uv

      - name: Install backend dependencies
        # Install editable with dev dependencies for pytest
        run: uv pip install -e ".[dev]"

      - name: Run Pytest
        run: uv run pytest tests/ # Specify the tests directory

  frontend-tests:
    name: Run Frontend Tests (Node.js)
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend/my-app # Set default directory for frontend steps

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: "18"
          cache: "npm" # Enable caching for npm dependencies
          cache-dependency-path: frontend/my-app/package-lock.json # Cache based on lock file

      - name: Install frontend dependencies
        # Use 'ci' for clean installs in CI environments based on package-lock.json
        run: npm ci

      - name: Run NPM Tests
        # The 'CI=true' environment variable often makes test runners like Jest
        # run non-interactively and exit after tests complete.
        run: npm test
        env:
          CI: true
```

**Explanation:**

1.  **`name`**: The name of the workflow as it appears in the GitHub Actions UI.
2.  **`on`**: Defines the events that trigger the workflow:
    - `push`: Runs when code is pushed to `main` or `develop`.
    - `pull_request`: Runs when a pull request is opened or updated targeting `main` or `develop`.
    - `workflow_dispatch`: Allows manual triggering from the Actions tab.
3.  **`jobs`**: Defines the tasks to run. We have two parallel jobs: `backend-tests` and `frontend-tests`.
4.  **`backend-tests` Job:**
    - `name`: Display name for the job.
    - `runs-on`: Specifies the runner environment (Ubuntu Linux).
    - `defaults.run.working-directory`: Sets the default directory for subsequent `run` steps to `./backend`.
    - **Steps:**
      - `Checkout code`: Gets the repository code onto the runner.
      - `Set up Python`: Installs the specified Python version (3.11).
      - `Install uv`: Installs your package manager using pip.
      - `Install backend dependencies`: Uses `uv` to install the backend package in editable mode (`-e`) along with its `[dev]` dependencies (which should include `pytest`).
      - `Run Pytest`: Executes `pytest` using `uv run` within the backend directory, targeting the `tests/` subdirectory.
5.  **`frontend-tests` Job:**
    - `name`, `runs-on`, `defaults.run.working-directory`: Similar setup, but targeting `./frontend/my-app`.
    - **Steps:**
      - `Checkout code`: Gets the repository code.
      - `Set up Node.js`: Installs Node.js version 18.
      - `cache: 'npm'`: Enables caching of `node_modules` based on `package-lock.json` to speed up subsequent runs.
      - `Install frontend dependencies`: Uses `npm ci` which is recommended for CI as it installs dependencies exactly as specified in `package-lock.json`.
      - `Run NPM Tests`: Executes the `test` script defined in your `frontend/my-app/package.json`. The `CI: true` environment variable is often necessary for test runners like Jest (used by Create React App/Vite) to run in a non-interactive mode suitable for CI.

**To Use This:** ✅

1.  Save the YAML content into `.github/workflows/ci-tests.yml`.
2.  Commit and push this file to your repository (on `develop` first, then merge to `main`).
3.  GitHub Actions will automatically detect this file and start running the workflow on the specified triggers (pushes/PRs to `main` or `develop`). You can monitor the progress under the "Actions" tab of your GitHub repository.

**Important Notes:**

- **Test Dependencies:** Ensure `pytest` and any other testing libraries are listed under the `[project.optional-dependencies.dev]` section in your `backend/pyproject.toml`. Ensure your frontend testing dependencies are in `frontend/my-app/package.json` (usually under `devDependencies`).
- **Frontend Test Script:** ✅ Verify that the `test` script in `frontend/my-app/package.json` is configured to run non-interactively (e.g., doesn't default to watch mode). Using `CI=true` usually handles this for common React setups.
- **Environment Variables for Tests:** This workflow currently _does not_ inject any secrets or environment variables from `.env` files. Your tests should ideally mock external dependencies (like Supabase, JigsawStack). If your tests _require_ specific environment variables (e.g., pointing to a _test_ database or API), you would need to add steps to create a temporary `.env` file during the CI run or (better) pass them using GitHub Actions secrets/variables if they are sensitive. For non-sensitive test config, you could potentially commit a `.env.test` file and copy it.
