Okay, let's focus on resolving the SVG export issue related to the `vtracer` library. The error message `AttributeError: module 'vtracer' has no attribute 'Configuration'` is the key clue. It means the way your code is trying to configure `vtracer` (using `vtracer.Configuration()`) is incorrect for the version you have installed or the current API of the library.

The file locking error (`WinError 32`) might be a secondary consequence – if the `vtracer` call fails prematurely due to the `AttributeError`, the temporary files might not be properly released before the `finally` block tries to delete them. Fixing the main error will likely resolve this too, but we'll include a check for file handling.

Here's a plan to fix the SVG conversion:

**Phase 1: Investigation & Verification**

1.  **Verify `vtracer` Version:**

    - **Action:** Check your `backend/pyproject.toml` file for the exact version constraint specified for the `vtracer` dependency (e.g., `vtracer>=0.0.11`).
    - **Action:** In your activated backend virtual environment, run `uv pip show vtracer` to confirm the _actually installed_ version. Ensure it matches the expected version range.
    - **Goal:** Confirm you are working with the intended version of the library.

2.  **Consult `vtracer` Documentation (Crucial Step):**
    - **Action:** Go to the `vtracer` PyPI page (`https://pypi.org/project/vtracer/`) and find the link to its documentation or GitHub repository.
    - **Action:** Review the usage examples for the installed version, specifically focusing on how to call the main conversion function (likely `vtracer.convert_image_to_svg`) and how to pass configuration options (like `color_mode`, `path_precision`, `filter_speckle`, etc.).
    - **Goal:** Understand the correct API usage for passing parameters. _Hypothesis:_ Parameters are likely passed as direct keyword arguments to the conversion function, not via a `Configuration` object. Also check if `vtracer.ColorMode.COLOR` or `vtracer.ColorMode.BINARY` are still valid enums or if string values like `'color'` or `'binary'` should be used.

**Phase 2: Code Refactoring (`_convert_to_svg` method)**

3.  **Refactor Color Mode Conversion:**

    - **File:** `backend/app/services/export/service.py`
    - **Action:** Locate the `_convert_to_svg` method.
    - **Action:** Remove the lines creating the `config = vtracer.Configuration()` object.
    - **Action:** Modify the call to `vtracer.convert_image_to_svg` for the `color` mode. Instead of passing the `config` object, pass the parameters directly as keyword arguments based on the documentation found in Step 2.
    - **Example (adjust based on actual docs):**

      ```python
      # Remove: config = vtracer.Configuration()
      # Remove: config.color_mode = vtracer.ColorMode.COLOR # Check if ColorMode enum exists
      # Remove: config.hierarchical = True
      # Remove: config.filter_speckle = 4
      # Remove: config.path_precision = 3
      # Remove: Parameter setting from svg_params onto config

      # Replace the call vtracer.convert_image_to_svg(input_path, output_path, config) with something like:
      vtracer.convert_image_to_svg(
          input_path,
          output_path,
          color_mode='color', # Or whatever the correct string/enum is
          hierarchical=True,
          filter_speckle=svg_params.get('filter_speckle', 4) if svg_params else 4,
          path_precision=svg_params.get('path_precision', 3) if svg_params else 3,
          # Add other relevant parameters based on vtracer docs and svg_params
          # Example: corner_threshold=svg_params.get('corner_threshold', 60) if svg_params else 60,
          # Example: length_threshold=svg_params.get('length_threshold', 4.0) if svg_params else 4.0,
          # ... etc
      )
      ```

    - **Action:** Ensure the `mode` parameter from `svg_params` correctly maps to the `color_mode` argument (or its equivalent) for `vtracer`. Verify the expected value (e.g., string `'color'` vs. an enum).
    - **Action:** Ensure parameters passed in the `svg_params` dictionary correctly override the defaults when calling the function.

4.  **Refactor Simplified/Monochrome Mode Conversion:**
    - **File:** `backend/app/services/export/service.py`
    - **Action:** Locate the `else` block within `_convert_to_svg` that handles non-color modes (likely the `_create_simple_svg_from_image` call, which itself calls `vtracer.convert_image_to_svg`).
    - **Action:** Apply the same refactoring as in Step 3 to the call within `_create_simple_svg_from_image`. Remove `vtracer.Configuration()`.
    - **Action:** Pass parameters like `color_mode` (e.g., `'binary'`), `hierarchical`, `filter_speckle`, `path_precision`, `corner_threshold`, `length_threshold` directly as keyword arguments. Verify the correct names and values from the documentation.

**Phase 3: File Handling & Cleanup**

5.  **Ensure Proper File Closing (Optional but Recommended):**

    - **File:** `backend/app/services/export/service.py`
    - **Action:** Inside the `_convert_to_svg` method's `finally` block, ensure the temporary file objects (`temp_input`, `temp_output`) are explicitly closed _before_ `os.unlink` is called, although the `with` statement should handle this. This is just an extra precaution.

      ```python
      finally:
          # Optional: Explicitly close if needed, though 'with' should handle it
          # if 'temp_input' in locals() and not temp_input.closed:
          #     temp_input.close()
          # if 'temp_output' in locals() and not temp_output.closed:
          #     temp_output.close()

          # Clean up temporary files
          try:
              if 'input_path' in locals() and os.path.exists(input_path):
                   os.unlink(input_path)
              if 'output_path' in locals() and os.path.exists(output_path):
                   os.unlink(output_path)
          except (OSError, PermissionError) as e:
              logger.warning(f"Error cleaning up temp files: {str(e)}")
      ```

    - **Action:** Wrap the `os.unlink` calls in their own `try...except (OSError, PermissionError, FileNotFoundError)` block to log warnings instead of crashing if cleanup fails (e.g., due to unexpected locking or the file already being gone).

**Phase 4: Testing**

6.  **Test SVG Export:**
    - **Action:** Run the backend server.
    - **Action:** Use the frontend or an API client (like Postman or Insomnia) to trigger an SVG export request via the `/api/export/process` endpoint.
    - **Check:** Verify that the `AttributeError` no longer occurs.
    - **Check:** Confirm that a valid SVG file is generated and returned.
    - **Check:** Monitor the backend logs for any `WinError 32` or file cleanup warnings.
7.  **Test Different SVG Parameters:**
    - **Action:** Send export requests with different values in the optional `svg_params` field (if your frontend/request allows it).
    - **Check:** Verify that the parameters influence the output SVG as expected (e.g., fewer colors, different path precision). This confirms parameters are being passed correctly to the updated `vtracer` call.
8.  **Test Simplified Mode:**
    - **Action:** If applicable, test the SVG export flow that results in the simplified/binary mode being used.
    - **Check:** Ensure this path also works correctly without `AttributeError`.

This plan directly addresses the `AttributeError` by adapting the code to the correct `vtracer` API usage and includes steps to mitigate potential file locking issues during cleanup.
