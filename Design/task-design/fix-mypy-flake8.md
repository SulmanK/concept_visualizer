# Design Document: Fix mypy and flake8 errors in backend/app

**Status:** Proposed
**Author:** AI Assistant
**Date:** 2024-08-15

## 1. Problem Statement

The `backend/app` directory and its subdirectories (`api`, `models`, `services`, `utils`, `core`) contain numerous `mypy` type checking errors (approx. 280) and `flake8` linting violations, as identified by the `pre-commit` hooks. These errors hinder code readability, maintainability, and reliability, and prevent successful commits according to project standards (`@context/coding_standards.md`, `@context/pre-commit-hooks.md`).

## 2. Goals

- Resolve all `mypy` errors within `backend/app` and its subdirectories.
- Resolve all `flake8` violations within `backend/app` and its subdirectories.
- Ensure all Python files in the target directories pass `uv run pre-commit run mypy --all-files` and `uv run pre-commit run flake8 --all-files`.
- Improve overall code quality, type safety, and adherence to project coding standards.
- Enable clean commits without pre-commit hook failures for the backend Python code.

## 3. Non-Goals

- Fixing errors outside the specified backend directories (e.g., `frontend/`, `tests/`, `scripts/`).
- Major refactoring beyond what's necessary to fix linting or typing errors.
- Implementing new features or changing existing business logic (unless required to fix a type error).
- Optimizing performance unless directly related to fixing an error.
- Updating dependencies unless required for type stub installation.

## 4. Proposed Solution

We will adopt a phased approach, addressing errors directory by directory. This allows for focused effort, manageable changes, and easier tracking of progress.

### 4.1. Branching Strategy

1.  Create a new branch from the main development branch: `git checkout -b fix/backend-lint-type-errors`

### 4.2. Methodology per Directory

For each directory in the specified order, we will perform the following steps:

1.  **Run flake8:** `uv run pre-commit run flake8 --files backend/app/<directory_path>/**/*.py`
2.  **Fix flake8:** Address all reported `flake8` errors. This typically involves fixing formatting, removing unused imports, adding missing docstrings (following Google style), and resolving style violations according to `@context/coding_standards.md`.
3.  **Run mypy:** `uv run pre-commit run mypy --files backend/app/<directory_path>/**/*.py`
4.  **Fix mypy:** Address all reported `mypy` errors. This will involve:
    - Adding missing type hints for variables, function arguments, and return values.
    - Correcting incompatible type assignments.
    - Installing missing type stubs (e.g., `uv add types-python-jose`). If stubs are unavailable, use `# type: ignore[<error-code>]` sparingly with a comment explaining why.
    - Resolving `AttributeError` issues, potentially indicating incorrect object usage or missing attributes.
    - Addressing issues related to `Any` type usage where possible (`no-any-return`, etc.).
    - Fixing issues with `Optional` types (e.g., `Incompatible default for argument`, `no-implicit-optional`).
    - Correcting decorator issues (`Untyped decorator`).
5.  **Verify:** Repeat steps 1-4 until both `flake8` and `mypy` pass for all files within the target directory.
6.  **Commit:** Commit the changes for the directory with a clear message (e.g., `fix(backend): resolve flake8/mypy errors in models directory`).

### 4.3. Order of Directories

We will process directories in an order that generally minimizes dependency issues, starting with foundational code:

1.  `backend/app/models/` (Data structures)
2.  `backend/app/core/` (Configuration, core utilities, exceptions)
3.  `backend/app/utils/` (Shared utilities)
4.  `backend/app/services/` (Business logic, external integrations)
5.  `backend/app/api/` (API routes, request/response handling, dependencies)
6.  `backend/app/` (Root files like `main.py`, `__init__.py` if errors exist)

### 4.4. Tooling

- `uv run pre-commit run flake8 --files <path>`
- `uv run pre-commit run mypy --files <path>`
- `uv add <package>` (for installing type stubs)
- Editor integration for `flake8` and `mypy` for real-time feedback.

## 5. Alternatives Considered

- **Fixing all errors at once:** This is highly discouraged due to the large number of errors (280+). It would create a massive, hard-to-review commit and make debugging difficult if new issues arise.
- **Using automated fixing tools (e.g., `autoflake`, `pyupgrade`, `no_implicit_optional` script):** While potentially helpful for _some_ `flake8` issues or bulk `Optional` changes, they cannot address most `mypy` errors or complex `flake8` violations (like missing docstrings or complex logic checks). We can use them as aids, but manual intervention and review are essential.

## 6. Open Questions / Risks

- **Complexity:** Some `mypy` errors, particularly those involving complex types, generics, or external library interactions (like `supabase`, `cv2`, `jose`), might be challenging to resolve correctly and could require deeper understanding or minor refactoring.
- **Missing Stubs:** Some third-party libraries might lack type stubs. We may need to use `# type: ignore` or create basic stub files (`.pyi`).
- **Time Estimation:** Given the volume and potential complexity of errors, the time required is uncertain. The phased approach helps manage this.
- **Test Failures:** Fixing type errors might uncover latent bugs or necessitate changes that break existing tests. Running tests (`uv run pytest backend/tests/`) after fixing each major directory is recommended.

## 7. Rollout Plan

1.  Create the feature branch `fix/backend-lint-type-errors`.
2.  Execute the fixing process (Section 4.2) for each directory in the order specified (Section 4.3).
3.  Commit changes after successfully cleaning each directory.
4.  After all directories are processed, run a final full check: `uv run pre-commit run --all-files`.
5.  Run backend tests: `uv run pytest backend/tests/`. Address any failures.
6.  Push the branch to the remote repository.
7.  Create a Pull Request for review, linking this design document.
8.  Address review comments and merge upon approval.

## 8. Future Considerations

- Consider enabling stricter `mypy` rules after this initial cleanup.
- Investigate creating or contributing missing type stubs for third-party libraries.
- Regularly monitor and address new linting/typing errors to prevent accumulation.
