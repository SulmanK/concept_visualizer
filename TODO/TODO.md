Okay, let's create a design plan to implement the Git `post-checkout` hook for automatically switching your local `.env` files based on the checked-out branch (`develop` or `main`).

**Design Plan: Automatic Local `.env` Switching via Git Hook**

**1. Goal:**

- Enable developers to automatically use different local configuration settings (especially credentials) stored in `.env` files when switching between the `develop` and `main` branches locally.
- Ensure the application code (FastAPI backend, React frontend) always reads from standard `.env` files without needing branch-specific logic for configuration loading.
- Keep sensitive production credentials out of the main codebase history if possible.

**2. Approach:**

- Utilize a Git `post-checkout` hook. This script runs automatically _after_ a successful `git checkout` operation.
- The hook will detect the current branch name.
- Based on the branch name, it will copy the appropriate pre-defined, branch-specific environment file (e.g., `.env.develop`) to the standard `.env` location used by the application.
- The standard `.env` files will be listed in `.gitignore` to prevent committing local configurations and secrets.

**3. Prerequisites:**

- Git installed and initialized in the project repository.
- Developers need shell access (like Bash, Zsh) to run the hook script.
- Agreement on how to manage secrets within the team (see Step 6).

**4. File Structure & Naming Convention:**

- **Backend:**
  - `backend/.env`: **(Gitignored)** The active environment file loaded by the FastAPI app. _This file will be overwritten by the hook._
  - `backend/.env.develop`: **(Potentially Committed)** Contains settings and credentials for the `develop` branch/environment.
  - `backend/.env.main`: **(Potentially Committed - Use Placeholders for Secrets)** Contains settings and credentials/placeholders for the `main` branch/production environment.
  - `backend/.env.example`: **(Committed)** Template file showing required variables.
- **Frontend:**
  - `frontend/my-app/.env`: **(Gitignored)** The active environment file loaded by Vite/React. _This file will be overwritten by the hook._
  - `frontend/my-app/.env.develop`: **(Potentially Committed)** Contains settings for the `develop` branch.
  - `frontend/my-app/.env.main`: **(Potentially Committed - Use Placeholders for Secrets)** Contains settings/placeholders for the `main` branch.
  - `frontend/my-app/.env.example`: **(Committed)** Template file.

**5. `.gitignore` Update:**

Ensure the following lines are present in your root `.gitignore` file:

```gitignore
# Environment files containing secrets or local settings
backend/.env
frontend/my-app/.env
*.local
```

**6. Secrets Management Strategy:**

- **Decision Needed:** How will actual secrets be handled in the `.env.develop` and `.env.main` files?
  - **Option A (Recommended for Dev, Placeholders for Prod):** Commit `backend/.env.develop` and `frontend/my-app/.env.develop` with real **development** credentials (if acceptable within team security policy). Commit `backend/.env.main` and `frontend/my-app/.env.main` with **placeholders** for production secrets (e.g., `YOUR_PROD_API_KEY_HERE`). Developers will need to get production secrets securely if they need to test the `main` branch config locally.
  - **Option B (Placeholders Everywhere):** Commit all `.env.develop` and `.env.main` files with **only placeholders**. Developers must always obtain credentials for _both_ environments from a secure source (Vault, 1Password, etc.) and manually populate their local, gitignored `.env` file _after_ the hook copies the appropriate placeholder file.
  - **Option C (Not Recommended for Prod Secrets):** Commit real secrets in all files. Only viable for highly trusted, private repositories.
- **Action:** Choose a strategy and populate the `.env.develop` and `.env.main` files accordingly.

**7. Git Hook Script (`post-checkout`):**

- **Location:** Create this file at the **root** of your project repository inside the `.git/hooks/` directory. The full path will be `.git/hooks/post-checkout`.
- **Content:**

```bash
#!/bin/bash
# Git hook to switch .env files based on the checked-out branch.

# --- Configuration ---
BACKEND_DIR="backend"
FRONTEND_DIR="frontend/my-app"
BRANCHES_TO_MANAGE=("develop" "main") # Add other branches if needed

# --- Helper Function ---
copy_env_file() {
    local branch_name="$1"
    local target_env_file="$2" # Full path to the target .env (e.g., backend/.env)
    local branch_specific_source_suffix=".${branch_name}" # e.g., .develop

    # Get the directory and base name of the target file
    local target_dir=$(dirname "$target_env_file")
    local target_basename=$(basename "$target_env_file") # Should be .env
    local source_filename="${target_basename}${branch_specific_source_suffix}" # e.g., .env.develop
    local source_env_file="${target_dir}/${source_filename}" # Full path to source

    # Check if the branch-specific file exists
    if [ -f "$source_env_file" ]; then
        echo "Git Hook: Branch '$branch_name' detected. Copying '$source_env_file' to '$target_env_file'..."
        # Copy the branch-specific file to the target .env location
        cp "$source_env_file" "$target_env_file"
        echo "Git Hook: -> Copied '$source_filename' to '$target_basename'."
    else
        echo "Git Hook: Branch '$branch_name' detected, but no specific file found at '$source_env_file'."
        echo "Git Hook: -> Leaving '$target_env_file' untouched."
        # Optionally, remove the .env file if no branch-specific version exists:
        # echo "Git Hook: -> Removing '$target_env_file'."
        # rm -f "$target_env_file"
    fi
}

# --- Main Hook Logic ---
previous_head=$1
new_head=$2
is_branch_checkout=$3 # 1 if it was a branch checkout, 0 if a file checkout

# Only run if it was a branch checkout (or initial checkout)
if [[ "$is_branch_checkout" == "1" ]]; then
    current_branch=$(git symbolic-ref --short HEAD)

    # Check if the current branch is one we manage env files for
    branch_is_managed=false
    for managed_branch in "${BRANCHES_TO_MANAGE[@]}"; do
        if [[ "$current_branch" == "$managed_branch" ]]; then
            branch_is_managed=true
            break
        fi
    done

    if $branch_is_managed; then
        echo "Git Hook: Switched to managed branch '$current_branch'. Updating .env files..."

        # Update Backend .env
        copy_env_file "$current_branch" "${BACKEND_DIR}/.env"

        # Update Frontend .env
        copy_env_file "$current_branch" "${FRONTEND_DIR}/.env"

        echo "Git Hook: Finished updating .env files."
    else
        echo "Git Hook: Switched to branch '$current_branch'. No managed .env actions defined for this branch."
    fi
else
    # Optional: uncomment if you want feedback on file checkouts
    # echo "Git Hook: File checkout detected, skipping .env update."
    : # No-op for file checkouts
fi

exit 0
```

**8. Hook Installation (Local Setup Required):**

- Every developer cloning the repository needs to make the hook script executable:
  ```bash
  chmod +x .git/hooks/post-checkout
  ```
- **Note:** Since the `.git` directory is not tracked by Git, this hook setup is local. Consider adding instructions to your project's `README.md` or using tools like `husky` or `pre-commit` if you want to automate hook installation for the team.

**9. Developer Workflow:**

1.  Clone the repository.
2.  Install the `post-checkout` hook (`chmod +x .git/hooks/post-checkout`).
3.  Run `git checkout develop`. The hook will automatically copy `.env.develop` to `.env` in both backend and frontend directories.
4.  **Crucial:** If the `.env.develop` files contain placeholders, obtain the actual development secrets from the secure source (Vault, 1Password, team lead) and manually update the contents of the local, gitignored `backend/.env` and `frontend/my-app/.env` files.
5.  Run the backend (`uvicorn ...`) and frontend (`npm run dev`). They will load the development settings from the `.env` files.
6.  Run `git checkout main`. The hook automatically copies `.env.main` to `.env`.
7.  If testing locally with production settings (and if `.env.main` has placeholders), update the local `.env` files with production secrets (if authorized and necessary).
8.  Run the apps again; they will now use the main/production settings.

**10. Testing & Verification:**

1.  After setting up the hook, run `git checkout develop`. Check the contents of `backend/.env` and `frontend/my-app/.env`. They should match the `.develop` versions.
2.  Run `git checkout main`. Check the contents again; they should match the `.main` versions.
3.  Run `git checkout some-other-feature-branch`. The hook should indicate that no specific action is taken for this branch, and the `.env` files should remain unchanged from the previous state (likely the `main` settings if that was the last managed branch checked out).

This plan provides a clear path to implementing the automatic `.env` switching based on your checked-out branch for local development, while respecting your constraint of not changing the application's config loading logic. Remember the importance of the local hook setup and the chosen secrets management strategy.

## Implementation Status

- [x] Created Git `post-checkout` hook for automatic environment switching
- [x] Added setup script `scripts/setup_env_files.sh` to create necessary environment files
- [x] Updated README.md with instructions for environment switching
- [x] Chose Option A for secrets management (real dev credentials, placeholders for prod)
- [ ] **Backend Production Preparation**
  - [ ] Implement secure environment variable management
  - [ ] Configure proper CORS for production domains
  - [ ] Set up production-appropriate logging levels
  - [ ] Optimize FastAPI application for production
  - [ ] Create separate development/staging/production configurations
- [ ] **Frontend Production Optimization**
  - [ ] Optimize bundle size with code splitting
  - [ ] Configure proper caching strategies
  - [ ] Implement performance monitoring
  - [ ] Create optimized Docker build for production
