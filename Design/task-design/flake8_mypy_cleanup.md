# Design Document: Flake8 & Mypy Error Cleanup

**Version:** 1.0
**Date:** 2024-08-13
**Author:** AI Assistant & User

## 1. Problem Statement

The backend codebase currently fails `flake8` linting checks and `mypy` type checking, as identified by running the pre-commit hooks (`uv run pre-commit run flake8 --all-files` and `uv run pre-commit run mypy --all-files`). This indicates issues with code style, potential bugs, unused code, incorrect type annotations, and missing docstrings. These failures prevent successful commits and indicate a need for systematic cleanup to improve code quality, maintainability, and reliability.

## 2. Goals

- Resolve all reported `flake8` errors in the backend codebase.
- Resolve all reported `mypy` errors in the backend codebase.
- Ensure the backend codebase passes all `flake8` and `mypy` pre-commit checks.
- Improve overall code quality, readability, and type safety.
- Establish a cleaner baseline for future development.

## 3. Non-Goals

- Major refactoring beyond what's necessary to fix linting/typing errors (e.g., architectural changes, significant logic rewrites unless required by complexity errors).
- Addressing frontend linting/typing issues (handled separately).
- Fixing errors related to other pre-commit hooks (e.g., `black`, `isort`, `prettier`) unless they are blockers for `flake8`/`mypy`.

## 4. Proposed Solution: Phased Cleanup Plan

We will address the errors systematically in phases, focusing on categories of errors to make the process manageable.

**Phase 1: Low-Hanging Fruit (Flake8)**

- Fix Docstring Formatting (D\*\*\* codes)
- Remove Unused Imports (F401)
- Fix Module Import Order (E402)
- Remove Unused Variables (F841)
- Fix simple style issues (E712, F541)

**Phase 2: Mypy Setup & Basic Type Errors**

- Address `import-not-found` errors (add stubs or fix paths).
- Fix `no-untyped-def` errors (add basic type hints to functions).
- Fix `assignment` errors related to `None` vs. explicit `Optional`.
- Fix `var-annotated` errors (add type hints to variables).

**Phase 3: Complex Mypy Errors & Flake8 Logic**

- Address `arg-type` errors (mismatched types in function calls).
- Fix `call-arg` errors (incorrect keyword arguments, missing arguments).
- Address `attr-defined` errors (missing attributes, often due to incorrect types or API changes).
- Resolve `operator` errors (type mismatches in operations).
- Fix `return-value` errors (function returns type different from annotation).
- Address `override` errors (method signature incompatible with superclass).
- Fix `union-attr` errors (accessing attributes on potentially `None` values).
- Address `no-any-return` errors (replace `Any` with specific types where possible).
- Fix `misc` errors (e.g., untyped decorators).
- Address Flake8 Complexity (C901) by refactoring specific functions.

**Phase 4: Validation & Iteration**

- Re-run `flake8 --all-files` and `mypy --all-files` frequently within phases.
- After each phase, run both tools to ensure no regressions.
- Final run of all pre-commit hooks to confirm success.

## 5. Detailed Error List

### 5.1 Mypy Errors (280 errors in 50 files)

```
$ uv run pre-commit run mypy --all-files
mypy.....................................................................Failed
- hook id: mypy
- exit code: 1

app\services\task\interface.py:14: error: Incompatible default for argument "metadata" (default has type "None", argument has type "dict[str, Any]")  [assignment]
app\services\task\interface.py:14: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
app\services\task\interface.py:14: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
app\core\middleware\__init__.py:5: error: Skipping analyzing "app.core.middleware.prioritization": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\core\exceptions.py:514: error: Argument 2 to "__init__" of "ConfigurationError" has incompatible type "dict[str, Any]"; expected "str | None"  [arg-type]
app\api\routes\health\utils.py:15: error: Missing return statement  [return]
app\models\common\base.py:19: error: Need type annotation for "json_encoders" (hint: "json_encoders: dict[<type>, <type>] = ...")  [var-annotated]
app\models\export\request.py:38: error: Function is missing a type annotation  [no-untyped-def]
app\models\export\request.py:46: error: Function is missing a type annotation  [no-untyped-def]
app\models\concept\request.py:61: error: Function is missing a type annotation  [no-untyped-def]
app\core\config.py:93: error: Function is missing a return type annotation  [no-untyped-def]
app\core\config.py:93: note: Use "-> None" if function does not return a value
app\core\config.py:181: error: Function is missing a type annotation  [no-untyped-def]
app\utils\jwt_utils.py:14: error: Library stubs not installed for "jose"  [import-untyped]
app\utils\jwt_utils.py:15: error: Library stubs not installed for "jose.exceptions"  [import-untyped]
app\utils\jwt_utils.py:15: note: Hint: "python3 -m pip install types-python-jose"
app\utils\jwt_utils.py:15: note: (or run "mypy --install-types" to install all missing stub packages)
app\utils\jwt_utils.py:61: error: Returning Any from function declared to return "str"  [no-any-return]
app\utils\jwt_utils.py:83: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
app\utils\jwt_utils.py:115: error: Incompatible types in assignment (expression has type "dict[str, Any] | None", variable has type "dict[str, Any]")  [assignment]
app\utils\jwt_utils.py:122: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\utils\jwt_utils.py:124: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\utils\jwt_utils.py:126: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\utils\jwt_utils.py:158: error: Returning Any from function declared to return "str"  [no-any-return]
app\utils\jwt_utils.py:181: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\limiter\redis_store.py:130: error: Returning Any from function declared to return "int"  [no-any-return]
app\core\limiter\redis_store.py:152: error: Argument 1 to "int" has incompatible type "Awaitable[Any] | Any"; expected "str | Buffer | SupportsInt | SupportsIndex | SupportsTrunc"  [arg-type]
app\core\limiter\redis_store.py:357: error: "Awaitable[Any]" object is not iterable  [misc]
app\services\image\conversion.py:90: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\services\image\conversion.py:144: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\services\image\conversion.py:151: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\services\image\conversion.py:161: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\services\image\conversion.py:194: error: Need type annotation for "metadata"  [var-annotated]
app\services\image\conversion.py:218: error: Unsupported target for indexed assignment ("dict[Any, Any] | int | str | float | None")  [index]
app\services\image\conversion.py:264: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\utils\auth\user.py:40: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\utils\auth\user.py:49: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\utils\auth\user.py:84: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\services\jigsawstack\client.py:226: error: Dict entry 2 has incompatible type "str": "bytes"; expected "str": "str"  [dict-item]
app\services\jigsawstack\client.py:263: error: Dict entry 2 has incompatible type "str": "bytes"; expected "str": "str"  [dict-item]
app\services\jigsawstack\client.py:877: error: Incompatible return value type (got "str", expected "bytes")  [return-value]
app\api\routes\health\endpoints.py:22: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\endpoints.py:36: error: Function is missing a return type annotation  [no-untyped-def]
app\api\middleware\rate_limit_headers.py:72: error: Returning Any from function declared to return "Response"  [no-any-return]
app\services\jigsawstack\service.py:117: error: Incompatible return value type (got "bytes", expected "dict[str, Any]")  [return-value]
app\services\jigsawstack\service.py:155: error: "JigsawStackClient" has no attribute "generate_color_palettes"; maybe "generate_multiple_palettes"?  [attr-defined]
app\services\jigsawstack\service.py:160: error: Returning Any from function declared to return "list[dict[str, Any]]"  [no-any-return]
app\services\image\service.py:240: error: Incompatible types in assignment (expression has type "Image", variable has type "ImageFile")  [assignment]
app\services\image\service.py:372: error: Need type annotation for "_image_cache" (hint: "_image_cache: dict[<type>, <type>] = ...")  [var-annotated]
app\services\image\service.py:391: error: Returning Any from function declared to return "bytes"  [no-any-return]
app\services\image\service.py:414: error: "ImagePersistenceServiceInterface" has no attribute "get_image_async"  [attr-defined]
app\services\image\processing.py:76: error: No overload variant of "kmeans" matches argument types "ndarray[tuple[int, int], dtype[floating[_32Bit]]]", "int", "None", "tuple[int, int, float]", "int", "int"  [call-overload]
app\services\image\processing.py:76: note: Possible overload variants:
app\services\image\processing.py:76: note:     def kmeans(data: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], K: int, bestLabels: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], criteria: tuple[int, int, float], attempts: int, flags: int, centers: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]] | None = ...) -> tuple[float, Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]]]
app\services\image\processing.py:76: note:     def kmeans(data: UMat, K: int, bestLabels: UMat, criteria: tuple[int, int, float], attempts: int, flags: int, centers: UMat | None = ...) -> tuple[float, UMat, UMat]
app\services\image\processing.py:94: error: Incompatible return value type (got "list[tuple[tuple[int, ...], Any]]", expected "list[tuple[tuple[int, int, int], float]]")  [return-value]
app\services\image\processing.py:138: error: No overload variant of "cvtColor" matches argument types "unsignedinteger[_8Bit]", "int"  [call-overload]
app\services\image\processing.py:138: note: Possible overload variants:
app\services\image\processing.py:138: note:     def cvtColor(src: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], code: int, dst: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]] | None = ..., dstCn: int = ..., hint: int = ...) -> Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]]
app\services\image\processing.py:138: note:     def cvtColor(src: UMat, code: int, dst: UMat | None = ..., dstCn: int = ..., hint: int = ...) -> UMat
app\services\image\processing.py:138: error: Argument 1 to "unsignedinteger" has incompatible type "list[list[tuple[int, int, int]]]"; expected "SupportsInt | SupportsIndex | str | bytes"  [arg-type]
app\services\image\processing.py:193: error: Incompatible return value type (got "tuple[float, ...]", expected "tuple[float, float, float]")  [return-value]
app\services\image\processing.py:241: error: Incompatible types in assignment (expression has type "str | bytes", variable has type "bytes")  [assignment]
app\services\image\processing.py:268: error: No overload variant of "kmeans" matches argument types "ndarray[tuple[int, int], dtype[floating[_32Bit]]]", "int", "None", "tuple[int, int, float]", "int", "int"  [call-overload]
app\services\image\processing.py:268: note: Possible overload variants:
app\services\image\processing.py:268: note:     def kmeans(data: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], K: int, bestLabels: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], criteria: tuple[int, int, float], attempts: int, flags: int, centers: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]] | None = ...) -> tuple[float, Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]]]
app\services\image\processing.py:268: note:     def kmeans(data: UMat, K: int, bestLabels: UMat, criteria: tuple[int, int, float], attempts: int, flags: int, centers: UMat | None = ...) -> tuple[float, UMat, UMat]
app\services\image\processing.py:307: error: Argument 1 to "unsignedinteger" has incompatible type "list[list[Any]]"; expected "SupportsInt | SupportsIndex | str | bytes"  [arg-type]
app\services\image\processing.py:308: error: Argument 1 to "unsignedinteger" has incompatible type "list[list[tuple[int, int, int]]]"; expected "SupportsInt | SupportsIndex | str | bytes"  [arg-type]
app\services\image\processing.py:310: error: No overload variant of "cvtColor" matches argument types "unsignedinteger[_8Bit]", "int"  [call-overload]
app\services\image\processing.py:310: note: Possible overload variants:
app\services\image\processing.py:310: note:     def cvtColor(src: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], code: int, dst: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]] | None = ..., dstCn: int = ..., hint: int = ...) -> Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]]
app\services\image\processing.py:310: note:     def cvtColor(src: UMat, code: int, dst: UMat | None = ..., dstCn: int = ..., hint: int = ...) -> UMat
app\services\image\processing.py:311: error: No overload variant of "cvtColor" matches argument types "unsignedinteger[_8Bit]", "int"  [call-overload]
app\services\image\processing.py:311: note: Possible overload variants:
app\services\image\processing.py:311: note:     def cvtColor(src: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]], code: int, dst: Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]] | None = ..., dstCn: int = ..., hint: int = ...) -> Mat | ndarray[Any, dtype[integer[Any] | floating[Any]]]
app\services\image\processing.py:311: note:     def cvtColor(src: UMat, code: int, dst: UMat | None = ..., dstCn: int = ..., hint: int = ...) -> UMat
app\services\concept\refinement.py:77: error: Unexpected keyword argument "init_image_url" for "refine_image" of "JigsawStackClient"; did you mean "image_url"?  [call-arg]
app\services\jigsawstack\client.py:294: note: "refine_image" of "JigsawStackClient" defined here
app\services\concept\refinement.py:77: error: Unexpected keyword argument "guidance_scale" for "refine_image" of "JigsawStackClient"  [call-arg]
app\services\jigsawstack\client.py:294: note: "refine_image" of "JigsawStackClient" defined here
app\services\concept\refinement.py:77: error: Unexpected keyword argument "width" for "refine_image" of "JigsawStackClient"  [call-arg]
app\services\jigsawstack\client.py:294: note: "refine_image" of "JigsawStackClient" defined here
app\services\concept\refinement.py:77: error: Unexpected keyword argument "height" for "refine_image" of "JigsawStackClient"  [call-arg]
app\services\jigsawstack\client.py:294: note: "refine_image" of "JigsawStackClient" defined here
app\services\concept\refinement.py:87: error: "JigsawStackClient" has no attribute "generate_color_palette"  [attr-defined]
app\services\concept\refinement.py:102: error: Unexpected keyword argument "preserve_aspects" for "GenerationResponse"  [call-arg]
app\services\concept\refinement.py:106: error: Argument "image_url" to "GenerationResponse" has incompatible type "bytes"; expected "HttpUrl"  [arg-type]
app\services\concept\refinement.py:110: error: Argument "original_image_url" to "GenerationResponse" has incompatible type "str"; expected "HttpUrl | None"  [arg-type]
app\services\concept\palette.py:106: error: "JigsawStackClient" has no attribute "generate_color_palette"  [attr-defined]
app\services\concept\palette.py:113: error: Returning Any from function declared to return "list[str]"  [no-any-return]
app\services\concept\generation.py:63: error: "JigsawStackClient" has no attribute "generate_color_palette"  [attr-defined]
app\services\concept\generation.py:78: error: Missing named argument "original_image_url" for "GenerationResponse"  [call-arg]
app\services\concept\generation.py:78: error: Missing named argument "refinement_prompt" for "GenerationResponse"  [call-arg]
app\services\concept\generation.py:82: error: Argument "image_url" to "GenerationResponse" has incompatible type "dict[str, str]"; expected "HttpUrl"  [arg-type]
app\services\image\processing_service.py:35: error: Function is missing a return type annotation  [no-untyped-def]
app\services\image\processing_service.py:35: note: Use "-> None" if function does not return a value
app\services\image\processing_service.py:80: error: Argument "width" to "resize_image" of "ImageProcessingService" has incompatible type "Any | None"; expected "int"  [arg-type]
app\services\image\processing_service.py:245: error: Unsupported operand types for / ("int" and "None")  [operator]
app\services\image\processing_service.py:245: note: Right operand is of type "int | None"
app\services\image\processing_service.py:253: error: Incompatible types in assignment (expression has type "int | None", variable has type "int")  [assignment]
app\services\image\processing_service.py:254: error: Unsupported operand types for * ("None" and "float")  [operator]
app\services\image\processing_service.py:254: note: Left operand is of type "int | None"
app\services\image\processing_service.py:259: error: Argument 1 to "resize" of "Image" has incompatible type "tuple[int, int | None]"; expected "tuple[int, int] | list[int] | ndarray[tuple[int, ...], dtype[Any]]"  [arg-type]
app\services\concept\service.py:112: error: Argument 1 to "_download_image" of "ConceptService" has incompatible type "str | None"; expected "str"  [arg-type]
app\services\concept\service.py:114: error: Argument 1 to "len" has incompatible type "bytes | None"; expected "Sized"  [arg-type]
app\services\concept\service.py:124: error: Argument "image_data" to "store_image" of "ImagePersistenceServiceInterface" has incompatible type "bytes | None"; expected "bytes | BytesIO | UploadFile"  [arg-type]
app\services\concept\service.py:168: error: Incompatible types in assignment (expression has type "bytes", target has type "str | None")  [assignment]
app\services\concept\service.py:175: error: Signature of "generate_concept_with_palettes" incompatible with supertype "ConceptServiceInterface"  [override]
app\services\concept\service.py:175: note:      Superclass:
app\services\concept\service.py:175: note:          def generate_concept_with_palettes(self, logo_description: str, theme_description: str, num_palettes: int = ...) -> Coroutine[Any, Any, tuple[list[dict[str, Any]], list[dict[str, Any]]]]
app\services\concept\service.py:175: note:      Subclass:
app\services\concept\service.py:175: note:          def generate_concept_with_palettes(self, logo_description: str, theme_description: str, num_palettes: int = ..., user_id: str | None = ...) -> Coroutine[Any, Any, tuple[dict[str, Any], list[dict[str, Any]]]]
app\services\concept\service.py:257: error: Signature of "refine_concept" incompatible with supertype "ConceptServiceInterface"  [override]
app\services\concept\service.py:257: note:      Superclass:
app\services\concept\service.py:257: note:          def refine_concept(self, original_image_url: str, refinement_prompt: str, logo_description: str | None = ..., theme_description: str | None = ..., user_id: str | None = ..., skip_persistence: bool = ..., strength: float = ...) -> Coroutine[Any, Any, dict[str, Any]]
app\services\concept\service.py:257: note:      Subclass:
app\services\concept\service.py:257: note:          def refine_concept(self, original_image_url: str, logo_description: str | None, theme_description: str | None, refinement_prompt: str, preserve_aspects: list[str], user_id: str | None = ...) -> Coroutine[Any, Any, GenerationResponse]
app\services\concept\service.py:302: error: Argument 1 to "_download_image" of "ConceptService" has incompatible type "HttpUrl"; expected "str"  [arg-type]
app\services\concept\service.py:306: error: Argument "image_data" to "store_image" of "ImagePersistenceServiceInterface" has incompatible type "bytes | None"; expected "bytes | BytesIO | UploadFile"  [arg-type]
app\services\concept\service.py:345: error: Incompatible types in assignment (expression has type "str", variable has type "HttpUrl")  [assignment]
app\services\concept\service.py:423: error: Argument "image_data" to "apply_palette_to_image" of "ImageServiceInterface" has incompatible type "bytes | None"; expected "bytes"  [arg-type]
app\api\routes\__tests__\health_test.py:6: error: Cannot find implementation or library stub for module named "backend.app.main"  [import-not-found]
app\api\routes\__tests__\health_test.py:11: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\__tests__\health_test.py:11: note: Use "-> None" if function does not return a value
app\api\routes\__tests__\health_test.py:28: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\__tests__\health_test.py:28: note: Use "-> None" if function does not return a value
app\api\routes\__tests__\concept_test.py:12: error: Cannot find implementation or library stub for module named "backend.app.main"  [import-not-found]
app\api\routes\__tests__\concept_test.py:13: error: Cannot find implementation or library stub for module named "backend.app.services.jigsawstack.client"  [import-not-found]
app\api\routes\__tests__\concept_test.py:13: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
app\api\routes\__tests__\concept_test.py:19: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:52: error: Function is missing a type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:103: error: Function is missing a type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:156: error: Function is missing a type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:178: error: Function is missing a type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:226: error: Function is missing a type annotation  [no-untyped-def]
app\api\routes\__tests__\concept_test.py:265: error: Function is missing a type annotation  [no-untyped-def]
app\core\supabase\client.py:27: error: Incompatible default for argument "url" (default has type "None", argument has type "str")  [assignment]
app\core\supabase\client.py:27: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
app\core\supabase\client.py:27: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
app\core\supabase\client.py:27: error: Incompatible default for argument "key" (default has type "None", argument has type "str")  [assignment]
app\core\supabase\client.py:66: error: Function is missing a return type annotation  [no-untyped-def]
app\core\supabase\client.py:100: error: Incompatible default for argument "url" (default has type "None", argument has type "str")  [assignment]
app\core\supabase\client.py:100: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
app\core\supabase\client.py:100: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
app\core\supabase\client.py:100: error: Incompatible default for argument "key" (default has type "None", argument has type "str")  [assignment]
app\core\supabase\client.py:165: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
app\services\task\service.py:50: error: Incompatible default for argument "metadata" (default has type "None", argument has type "dict[str, Any]")  [assignment]
app\services\task\service.py:50: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
app\services\task\service.py:50: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
app\services\task\service.py:109: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
app\services\task\service.py:186: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
app\services\task\service.py:247: error: Returning Any from function declared to return "dict[str, Any]"  [no-any-return]
app\services\task\service.py:315: error: Returning Any from function declared to return "list[dict[str, Any]]"  [no-any-return]
app\services\task\service.py:447: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\image_storage.py:172: error: Function is missing a type annotation  [no-untyped-def]
app\core\supabase\image_storage.py:177: error: Function is missing a type annotation  [no-untyped-def]
app\core\supabase\image_storage.py:181: error: Function is missing a type annotation  [no-untyped-def]
app\core\supabase\image_storage.py:358: error: Incompatible return value type (got "None", expected "str")  [return-value]
app\core\supabase\image_storage.py:604: error: Returning Any from function declared to return "str | None"  [no-any-return]
app\core\supabase\concept_storage.py:85: error: Incompatible types in assignment (expression has type "APIResponse[Any]", variable has type "dict[str, Any] | None")  [assignment]
app\core\supabase\concept_storage.py:87: error: Item "dict[str, Any]" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:87: error: Item "None" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:91: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\concept_storage.py:91: error: Item "dict[str, Any]" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:91: error: Item "None" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:154: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\concept_storage.py:223: error: Incompatible types in assignment (expression has type "APIResponse[Any]", variable has type "list[dict[str, Any]] | None")  [assignment]
app\core\supabase\concept_storage.py:228: error: Item "list[dict[str, Any]]" of "list[dict[str, Any]] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:228: error: Item "None" of "list[dict[str, Any]] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:232: error: Returning Any from function declared to return "list[dict[str, Any]] | None"  [no-any-return]
app\core\supabase\concept_storage.py:232: error: Item "list[dict[str, Any]]" of "list[dict[str, Any]] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:232: error: Item "None" of "list[dict[str, Any]] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:292: error: Returning Any from function declared to return "list[dict[str, Any]] | None"  [no-any-return]
app\core\supabase\concept_storage.py:416: error: Returning Any from function declared to return "list[dict[str, Any]] | None"  [no-any-return]
app\core\supabase\concept_storage.py:545: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\concept_storage.py:648: error: Incompatible types in assignment (expression has type "APIResponse[Any]", variable has type "dict[str, Any] | None")  [assignment]
app\core\supabase\concept_storage.py:651: error: Item "dict[str, Any]" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:651: error: Item "None" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:656: error: Item "dict[str, Any]" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:656: error: Item "None" of "dict[str, Any] | None" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:662: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\concept_storage.py:718: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\core\supabase\concept_storage.py:758: error: Skipping analyzing "supabase.postgrest.base_request_builder": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\core\supabase\concept_storage.py:773: error: Item "dict[str, list[dict[str, Any]]]" of "dict[str, list[dict[str, Any]]] | Any" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:778: error: Need type annotation for "variations_by_concept" (hint: "variations_by_concept: dict[<type>, <type>] = ...")  [var-annotated]
app\core\supabase\concept_storage.py:779: error: Item "dict[str, list[dict[str, Any]]]" of "dict[str, list[dict[str, Any]]] | Any" has no attribute "data"  [union-attr]
app\core\supabase\concept_storage.py:840: error: Need type annotation for "variations_by_concept" (hint: "variations_by_concept: dict[<type>, <type>] = ...")  [var-annotated]
app\api\middleware\auth_middleware.py:24: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
app\services\persistence\image_persistence_service.py:44: error: Argument 1 to "ImageStorage" has incompatible type "SyncClient"; expected "SupabaseClient"  [arg-type]
app\services\persistence\image_persistence_service.py:224: error: "ImageStorage" has no attribute "remove_image"  [attr-defined]
app\services\persistence\image_persistence_service.py:250: error: Incompatible return value type (got "str | None", expected "str")  [return-value]
app\services\persistence\image_persistence_service.py:437: error: Returning Any from function declared to return "list[dict[str, Any]]"  [no-any-return]
app\services\persistence\concept_persistence_service.py:193: error: Returning Any from function declared to return "str"  [no-any-return]
app\services\persistence\concept_persistence_service.py:225: error: "SupabaseClient" has no attribute "settings"  [attr-defined]
app\services\persistence\concept_persistence_service.py:231: error: "SupabaseClient" has no attribute "settings"  [attr-defined]
app\api\errors.py:169: error: Argument "detail" to "__init__" of "APIError" has incompatible type "str | dict[str, Any]"; expected "str"  [arg-type]
app\api\errors.py:547: error: Function is missing a type annotation  [no-untyped-def]
app\api\errors.py:555: error: Untyped decorator makes function "api_error_handler" untyped  [misc]
app\api\errors.py:580: error: Untyped decorator makes function "http_exception_handler" untyped  [misc]
app\api\errors.py:608: error: Untyped decorator makes function "validation_exception_handler" untyped  [misc]
app\api\errors.py:626: error: Need type annotation for "field_errors" (hint: "field_errors: dict[<type>, <type>] = ...")  [var-annotated]
app\api\errors.py:660: error: Untyped decorator makes function "application_error_handler" untyped  [misc]
app\api\errors.py:698: error: Incompatible types in assignment (expression has type "dict[str, Any]", target has type "str")  [assignment]
app\api\errors.py:707: error: Untyped decorator makes function "task_not_found_handler" untyped  [misc]
app\services\persistence\__init__.py:57: error: Incompatible return value type (got "ImagePersistenceService", expected "ImagePersistenceServiceInterface")  [return-value]
app\services\persistence\__init__.py:57: error: Argument "client" to "ImagePersistenceService" has incompatible type "SupabaseClient"; expected "SyncClient"  [arg-type]
app\api\routes\health\check.py:32: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\check.py:51: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\check.py:73: error: Unsupported operand types for < ("datetime" and "object")  [operator]
app\core\limiter\config.py:24: error: Need type annotation for "NON_COUNTING_ENDPOINTS" (hint: "NON_COUNTING_ENDPOINTS: list[<type>] = ...")  [var-annotated]
app\core\limiter\config.py:80: error: Dict entry 0 has incompatible type "str": "Redis"; expected "str": "str"  [dict-item]
app\core\limiter\config.py:121: error: Argument 2 to "add_exception_handler" of "Starlette" has incompatible type "Callable[[Request, RateLimitExceeded], Response]"; expected "Callable[[Request, Exception], Response | Awaitable[Response]] | Callable[[WebSocket, Exception], Awaitable[None]]"  [arg-type]
app\core\limiter\config.py:138: error: Function is missing a type annotation  [no-untyped-def]
app\core\limiter\config.py:142: error: Function is missing a type annotation  [no-untyped-def]
app\core\limiter\config.py:147: error: Function is missing a type annotation  [no-untyped-def]
app\core\limiter\config.py:171: error: Cannot assign to a method  [method-assign]
app\core\limiter\__init__.py:114: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
app\core\limiter\__init__.py:148: error: Argument "limit" to "check_rate_limit" of "RedisStore" has incompatible type "str"; expected "int"  [arg-type]
app\api\routes\health\limits.py:31: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\limits.py:55: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\limits.py:77: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\health\limits.py:251: error: Function is missing a type annotation  [no-untyped-def]
app\utils\api_limits\decorators.py:18: error: Function is missing a return type annotation  [no-untyped-def]
app\utils\api_limits\decorators.py:34: error: Function is missing a return type annotation  [no-untyped-def]
app\utils\api_limits\decorators.py:36: error: Function is missing a type annotation  [no-untyped-def]
app\services\export\service.py:14: error: Skipping analyzing "vtracer": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\services\export\service.py:158: error: Value of type "tuple[int, int] | None" is not indexable  [index]
app\services\export\service.py:159: error: Value of type "tuple[int, int] | None" is not indexable  [index]
app\services\export\service.py:334: error: Unsupported operand types for > ("int" and "None")  [operator]
app\services\export\service.py:334: note: Left operand is of type "float | tuple[int, ...] | None"
app\services\export\service.py:334: error: Unsupported operand types for < ("tuple[int, ...]" and "int")  [operator]
app\api\middleware\rate_limit_apply.py:100: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\middleware\rate_limit_apply.py:105: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\middleware\rate_limit_apply.py:110: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\middleware\rate_limit_apply.py:116: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\middleware\rate_limit_apply.py:123: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\middleware\rate_limit_apply.py:234: error: Returning Any from function declared to return "Response"  [no-any-return]
app\api\dependencies.py:40: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\api\dependencies.py:64: error: Returning Any from function declared to return "dict[str, Any] | None"  [no-any-return]
app\api\dependencies.py:135: error: Incompatible types in assignment (expression has type "dict[str, Any] | None", variable has type "None")  [assignment]
app\api\routes\export\export_routes.py:28: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\export\export_routes.py:28: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
app\api\routes\export\export_routes.py:78: error: "ImagePersistenceServiceInterface" has no attribute "get_image_async"  [attr-defined]
app\api\routes\task\routes.py:28: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\task\routes.py:65: error: Unexpected keyword argument "error" for "TaskResponse"  [call-arg]
app\api\routes\task\routes.py:69: error: Argument "type" to "TaskResponse" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\task\routes.py:80: error: "Settings" has no attribute "DEBUG"  [attr-defined]
app\api\routes\task\routes.py:88: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\task\routes.py:120: error: Unexpected keyword argument "error" for "TaskResponse"  [call-arg]
app\api\routes\task\routes.py:124: error: Argument "type" to "TaskResponse" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\task\routes.py:142: error: "Settings" has no attribute "DEBUG"  [attr-defined]
app\api\routes\task\routes.py:150: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\task\routes.py:192: error: "Settings" has no attribute "DEBUG"  [attr-defined]
app\api\routes\concept_storage\storage_routes.py:29: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept_storage\storage_routes.py:108: error: Unexpected keyword argument "color_palettes" for "GenerationResponse"; did you mean "color_palette"?  [call-arg]
app\api\routes\concept_storage\storage_routes.py:109: error: Invalid index type "str" for "str"; expected type "SupportsIndex | slice[Any, Any, Any]"  [index]
app\api\routes\concept_storage\storage_routes.py:130: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept_storage\storage_routes.py:170: error: "ImagePersistenceServiceInterface" has no attribute "get_signed_url"; maybe "get_image_url"?  [attr-defined]
app\api\routes\concept_storage\storage_routes.py:181: error: "ImagePersistenceServiceInterface" has no attribute "get_signed_url"; maybe "get_image_url"?  [attr-defined]
app\api\routes\concept_storage\storage_routes.py:197: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept_storage\storage_routes.py:232: error: "ImagePersistenceServiceInterface" has no attribute "get_signed_url"; maybe "get_image_url"?  [attr-defined]
app\api\routes\concept_storage\storage_routes.py:243: error: "ImagePersistenceServiceInterface" has no attribute "get_signed_url"; maybe "get_image_url"?  [attr-defined]
app\api\routes\concept\refinement.py:44: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\refinement.py:85: error: Argument "user_id" to "get_tasks_by_user" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:88: error: Argument "user_id" to "get_tasks_by_user" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:105: error: Argument 1 to "mask_id" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:110: error: Missing named argument "completed_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:110: error: Missing named argument "result_id" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:110: error: Missing named argument "image_url" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:110: error: Missing named argument "error_message" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:125: error: Argument "user_id" to "create_task" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:136: error: Argument "original_image_url" to "add_task" of "BackgroundTasks" has incompatible type "HttpUrl"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:139: error: Argument "user_id" to "add_task" of "BackgroundTasks" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\refinement.py:151: error: Missing named argument "updated_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:151: error: Missing named argument "completed_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:151: error: Missing named argument "result_id" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:151: error: Missing named argument "image_url" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:151: error: Missing named argument "error_message" for "TaskResponse"  [call-arg]
app\api\routes\concept\refinement.py:162: error: Unexpected keyword argument "detail" for "ServiceUnavailableError"; did you mean "details"?  [call-arg]
app\core\exceptions.py:627: note: "ServiceUnavailableError" defined here
app\api\routes\concept\refinement.py:170: error: Unexpected keyword argument "detail" for "ServiceUnavailableError"; did you mean "details"?  [call-arg]
app\core\exceptions.py:627: note: "ServiceUnavailableError" defined here
app\api\routes\concept\refinement.py:173: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\refinement.py:221: error: Unexpected keyword argument "original_image_data" for "refine_concept" of "ConceptServiceInterface"; did you mean "original_image_url"?  [call-arg]
app\services\concept\interface.py:68: note: "refine_concept" of "ConceptServiceInterface" defined here
app\api\routes\concept\refinement.py:248: error: Argument "client" to "ImagePersistenceService" has incompatible type "SupabaseClient"; expected "SyncClient"  [arg-type]
app\api\routes\concept\refinement.py:300: error: Argument "persistence_service" to "ImageService" has incompatible type "ImagePersistenceService"; expected "ImagePersistenceServiceInterface"  [arg-type]
app\api\routes\concept\generation.py:54: error: Module "app.utils.api_limits.endpoints" has no attribute "get_limit_info"  [attr-defined]
app\api\routes\concept\generation.py:64: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\generation.py:221: error: Incompatible types in assignment (expression has type "httpx._models.Response", variable has type "starlette.responses.Response")  [assignment]
app\api\routes\concept\generation.py:222: error: "Response" has no attribute "raise_for_status"  [attr-defined]
app\api\routes\concept\generation.py:223: error: "Response" has no attribute "content"  [attr-defined]
app\api\routes\concept\generation.py:249: error: Incompatible types in "await" (actual type "tuple[str, str]", expected type "Awaitable[Any]")  [misc]
app\api\routes\concept\generation.py:249: error: Unexpected keyword argument "path" for "store_image" of "ImagePersistenceServiceInterface"  [call-arg]
app\api\routes\concept\generation.py:259: error: "ImageServiceInterface" has no attribute "extract_colors_from_image"  [attr-defined]
app\api\routes\concept\generation.py:266: error: Skipping analyzing "app.services.concept.helpers.palette_generator": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\api\routes\concept\generation.py:341: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\generation.py:381: error: Argument "user_id" to "get_tasks_by_user" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\generation.py:384: error: Argument "user_id" to "get_tasks_by_user" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\generation.py:401: error: Argument 1 to "mask_id" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\generation.py:406: error: Missing named argument "completed_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:406: error: Missing named argument "result_id" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:406: error: Missing named argument "image_url" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:406: error: Missing named argument "error_message" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:428: error: Argument "user_id" to "create_task" of "TaskServiceInterface" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\generation.py:440: error: Argument "user_id" to "add_task" of "BackgroundTasks" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\generation.py:444: error: Argument "concept_persistence_service" to "add_task" of "BackgroundTasks" has incompatible type "ConceptPersistenceServiceInterface"; expected "StorageServiceInterface"  [arg-type]
app\api\routes\concept\generation.py:452: error: Missing named argument "updated_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:452: error: Missing named argument "completed_at" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:452: error: Missing named argument "result_id" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:452: error: Missing named argument "image_url" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:452: error: Missing named argument "error_message" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:474: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\generation.py:585: error: Argument "client" to "ImagePersistenceService" has incompatible type "SupabaseClient"; expected "SyncClient"  [arg-type]
app\api\routes\concept\generation.py:619: error: Argument "persistence_service" to "ImageService" has incompatible type "ImagePersistenceService"; expected "ImagePersistenceServiceInterface"  [arg-type]
app\api\routes\concept\generation.py:680: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\generation.py:713: error: Unexpected keyword argument "error" for "TaskResponse"  [call-arg]
app\api\routes\concept\generation.py:717: error: Argument "type" to "TaskResponse" has incompatible type "Any | None"; expected "str"  [arg-type]
app\api\routes\concept\example_error_handling.py:31: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\concept\example_error_handling.py:72: error: "ConceptPersistenceServiceInterface" has no attribute "get_concept"; maybe "get_concept_detail"?  [attr-defined]
app\api\routes\concept\example_error_handling.py:77: error: Module "app.core.exceptions" has no attribute "AuthorizationError"; maybe "AuthenticationError"?  [attr-defined]
app\api\routes\concept\example_error_handling.py:116: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\auth\auth_routes.py:36: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\auth\auth_routes.py:84: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\auth\auth_routes.py:135: error: Function is missing a return type annotation  [no-untyped-def]
app\api\routes\api.py:6: error: Skipping analyzing "app.api.routes.session": module is installed, but missing library stubs or py.typed marker  [import-untyped]
app\api\routes\api.py:7: error: Skipping analyzing "app.api.routes.svg_conversion": module is installed, but missing library stubs or py.typed marker  [import-untyped]
Found 280 errors in 50 files (checked 97 source files)
```

### 5.2 Flake8 Errors

```
sulma@SK MINGW64 ~/OneDrive/Documents/Data Science/concept_visualizer/backend (develop)
$ uv run pre-commit run flake8 --all-files
flake8...................................................................Failed
- hook id: flake8
- exit code: 1

backend/app/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:16:1: F401 'app.services.export.get_export_service' imported but unused
backend/app/api/dependencies.py:17:1: F401 'app.services.export.interface.ExportServiceInterface' imported but unused
backend/app/api/dependencies.py:18:1: F401 'app.services.image.get_image_processing_service' imported but unused
backend/app/api/dependencies.py:19:1: F401 'app.services.image.interface.ImageProcessingServiceInterface' imported but unused
backend/app/api/dependencies.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:45:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:72:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:94:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/dependencies.py:127:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:9:1: F401 'typing.Type' imported but unused
backend/app/api/errors.py:12:1: F401 'fastapi.exception_handlers.http_exception_handler as fastapi_http_exception_handler' imported but unused
backend/app/api/errors.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:183:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:240:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:272:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:281:5: F401 'app.core.exceptions.ConceptError' imported but unused
backend/app/api/errors.py:429:1: E402 module level import not at top of file
backend/app/api/errors.py:442:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:467:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:490:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:548:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:557:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:584:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:612:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/errors.py:664:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:8:1: F401 'typing.Callable' imported but unused
backend/app/api/middleware/auth_middleware.py:8:1: F401 'typing.Union' imported but unused
backend/app/api/middleware/auth_middleware.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:44:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:122:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:148:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/auth_middleware.py:163:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_apply.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_apply.py:8:1: F401 'datetime.datetime' imported but unused
backend/app/api/middleware/rate_limit_apply.py:9:1: F401 'typing.Dict' imported but unused
backend/app/api/middleware/rate_limit_apply.py:9:1: F401 'typing.List' imported but unused
backend/app/api/middleware/rate_limit_apply.py:17:1: F401 'app.core.limiter.keys.get_endpoint_key' imported but unused
backend/app/api/middleware/rate_limit_apply.py:65:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_apply.py:74:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_apply.py:84:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_headers.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_headers.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_headers.py:27:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/middleware/rate_limit_headers.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/router.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/router.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/router.py:42:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:20:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:20:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:33:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:33:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:53:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:53:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:104:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:104:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:157:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:157:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:179:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:179:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:227:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:227:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/concept_test.py:266:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/concept_test.py:266:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/health_test.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/health_test.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/health_test.py:12:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/__tests__/health_test.py:12:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/__tests__/health_test.py:29:1: D205 1 blank line required between summary line and description
backend/app/api/routes/__tests__/health_test.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/api.py:1:1: D100 Missing docstring in public module
backend/app/api/routes/auth/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Any' imported but unused
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Dict' imported but unused
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Optional' imported but unused
backend/app/api/routes/auth/auth_routes.py:15:1: F401 'app.api.errors.ResourceNotFoundError' imported but unused
backend/app/api/routes/auth/auth_routes.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:85:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:136:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:22:1: F401 'app.models.concept.response.GenerationResponse' imported but unused
backend/app/api/routes/concept/example_error_handling.py:36:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:87:9: F841 local variable 'e' is assigned to but never used
backend/app/api/routes/concept/example_error_handling.py:121:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:7:1: F401 'asyncio' imported but unused
backend/app/api/routes/concept/generation.py:8:1: F401 'json' imported but unused
backend/app/api/routes/concept/generation.py:10:1: F401 'os' imported but unused
backend/app/api/routes/concept/generation.py:11:1: F401 'time' imported but unused
backend/app/api/routes/concept/generation.py:12:1: F401 'urllib.parse' imported but unused
backend/app/api/routes/concept/generation.py:16:1: F401 'typing.Any' imported but unused
backend/app/api/routes/concept/generation.py:16:1: F401 'typing.Dict' imported but unused
backend/app/api/routes/concept/generation.py:16:1: F401 'typing.List' imported but unused
backend/app/api/routes/concept/generation.py:16:1: F401 'typing.Optional' imported but unused
backend/app/api/routes/concept/generation.py:19:1: F401 'fastapi.responses.JSONResponse' imported but unused
backend/app/api/routes/concept/generation.py:20:1: F401 'pydantic.ValidationError as PydanticValidationError' imported but unused
backend/app/api/routes/concept/generation.py:21:1: F401 'slowapi.Limiter' imported but unused
backend/app/api/routes/concept/generation.py:22:1: F401 'slowapi.util.get_remote_address' imported but unused
backend/app/api/routes/concept/generation.py:27:1: F401 'app.api.errors.BadRequestError' imported but unused
backend/app/api/routes/concept/generation.py:27:1: F401 'app.api.errors.UnauthorizedError' imported but unused
backend/app/api/routes/concept/generation.py:37:1: F401 'app.core.constants.TASK_STATUS_COMPLETED' imported but unused
backend/app/api/routes/concept/generation.py:37:1: F401 'app.core.constants.TASK_STATUS_FAILED' imported but unused
backend/app/api/routes/concept/generation.py:44:1: F401 'app.models.concept.response.PaletteVariation' imported but unused
backend/app/api/routes/concept/generation.py:49:1: F401 'app.services.persistence.interface.ConceptPersistenceServiceInterface' imported but unused
backend/app/api/routes/concept/generation.py:53:1: F401 'app.utils.api_limits.decorators.store_rate_limit_info' imported but unused
backend/app/api/routes/concept/generation.py:54:1: F811 redefinition of unused 'apply_multiple_rate_limits' from line 52
backend/app/api/routes/concept/generation.py:54:1: F811 redefinition of unused 'apply_rate_limit' from line 52
backend/app/api/routes/concept/generation.py:54:1: F401 'app.utils.api_limits.endpoints.apply_rate_limit' imported but unused
backend/app/api/routes/concept/generation.py:54:1: F401 'app.utils.api_limits.endpoints.get_limit_info' imported but unused
backend/app/api/routes/concept/generation.py:55:1: F401 'app.utils.security.mask.mask_url' imported but unused
backend/app/api/routes/concept/generation.py:70:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:199:21: F811 redefinition of unused 'os' from line 10
backend/app/api/routes/concept/generation.py:349:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:485:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:536:21: F811 redefinition of unused 'os' from line 10
backend/app/api/routes/concept/generation.py:685:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/refinement.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/refinement.py:10:1: F401 'typing.Any' imported but unused
backend/app/api/routes/concept/refinement.py:10:1: F401 'typing.Dict' imported but unused
backend/app/api/routes/concept/refinement.py:10:1: F401 'typing.List' imported but unused
backend/app/api/routes/concept/refinement.py:10:1: F401 'typing.Optional' imported but unused
backend/app/api/routes/concept/refinement.py:14:1: F401 'fastapi.responses.JSONResponse' imported but unused
backend/app/api/routes/concept/refinement.py:21:1: F401 'app.core.exceptions.ApplicationError' imported but unused
backend/app/api/routes/concept/refinement.py:23:1: F401 'app.models.concept.response.RefinementResponse' imported but unused
backend/app/api/routes/concept/refinement.py:31:1: F401 'app.utils.api_limits.apply_rate_limit' imported but unused
backend/app/api/routes/concept/refinement.py:34:1: F401 'app.utils.security.mask.mask_url' imported but unused
backend/app/api/routes/concept/refinement.py:51:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/refinement.py:186:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:35:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:136:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:203:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/export_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/export_routes.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/check.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/check.py:14:1: F401 'app.api.errors.ServiceUnavailableError' imported but unused
backend/app/api/routes/health/check.py:33:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/check.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/endpoints.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/endpoints.py:10:1: F401 'typing.List' imported but unused
backend/app/api/routes/health/endpoints.py:12:1: F401 'fastapi.Depends' imported but unused
backend/app/api/routes/health/endpoints.py:12:1: F401 'fastapi.Response' imported but unused
backend/app/api/routes/health/endpoints.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/limits.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/limits.py:80:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/limits.py:251:1: C901 'get_limit_info' is too complex (40)
backend/app/api/routes/health/utils.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:17:1: F401 'app.services.task.interface.TaskServiceInterface' imported but unused
backend/app/api/routes/task/routes.py:18:1: F401 'app.services.task.service.TaskError' imported but unused
backend/app/api/routes/task/routes.py:36:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:93:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:155:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/core/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/config.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/config.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/config.py:94:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/constants.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:17:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:54:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:83:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:115:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:151:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:206:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:243:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:278:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:333:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:411:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:437:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:474:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:500:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:529:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:552:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:577:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:607:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:634:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/exceptions.py:665:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/factory.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/factory.py:25:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/__init__.py:39:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/__init__.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/__init__.py:91:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/config.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/config.py:17:1: F401 'app.utils.security.mask.mask_id' imported but unused
backend/app/core/limiter/config.py:28:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/config.py:49:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/config.py:108:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/decorators.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/decorators.py:20:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:21:1: D205 1 blank line required between summary line and description
backend/app/core/limiter/keys.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:62:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:82:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:96:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/keys.py:116:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:7:1: F401 'json' imported but unused
backend/app/core/limiter/redis_store.py:10:1: F401 'typing.List' imported but unused
backend/app/core/limiter/redis_store.py:10:1: F401 'typing.Union' imported but unused
backend/app/core/limiter/redis_store.py:22:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:38:5: F841 local variable 'redis_url' is assigned to but never used
backend/app/core/limiter/redis_store.py:70:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:82:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:94:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:109:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:138:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:160:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:192:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:246:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:325:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/redis_store.py:344:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/middleware/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/core/middleware/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/client.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:737:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:795:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:408:13: F841 local variable 'token' is assigned to but never used
backend/app/core/supabase/image_storage.py:534:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:591:29: F541 f-string is missing placeholders
backend/app/main.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/common/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/base.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/base.py:8:1: F401 'typing.Any' imported but unused
backend/app/models/common/base.py:8:1: F401 'typing.Dict' imported but unused
backend/app/models/common/base.py:8:1: F401 'typing.List' imported but unused
backend/app/models/common/base.py:10:1: F401 'pydantic.HttpUrl' imported but unused
backend/app/models/concept/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/concept/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/domain.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/request.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/response.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/export/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/export/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/export/request.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/export/request.py:7:1: F401 're' imported but unused
backend/app/models/task/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/task/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/task/response.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/task/response.py:8:1: F401 'datetime.datetime' imported but unused
backend/app/services/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/__init__.py:34:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/generation.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/generation.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/generation.py:33:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/generation.py:89:17: F541 f-string is missing placeholders
backend/app/services/concept/generation.py:105:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/interface.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/concept/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/interface.py:8:1: F401 'app.models.concept.response.GenerationResponse' imported but unused
backend/app/services/concept/interface.py:8:1: F401 'app.models.concept.response.RefinementResponse' imported but unused
backend/app/services/concept/interface.py:22:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/interface.py:46:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/interface.py:78:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/interface.py:108:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/palette.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/palette.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/palette.py:33:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/palette.py:84:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/refinement.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/refinement.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/refinement.py:38:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:16:1: F401 'app.models.concept.response.ColorPalette' imported but unused
backend/app/services/concept/service.py:23:1: F401 'app.services.persistence.interface.StorageServiceInterface' imported but unused
backend/app/services/concept/service.py:24:1: F401 'app.services.task.interface.TaskServiceInterface' imported but unused
backend/app/services/concept/service.py:38:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:65:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:182:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:266:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:360:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:395:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/service.py:457:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/interface.py:25:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/interface.py:53:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/interface.py:77:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/interface.py:103:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:7:1: F401 'base64' imported but unused
backend/app/services/export/service.py:12:1: F401 'typing.Any' imported but unused
backend/app/services/export/service.py:12:1: F401 'typing.BinaryIO' imported but unused
backend/app/services/export/service.py:12:1: F401 'typing.Union' imported but unused
backend/app/services/export/service.py:15:1: F401 'fastapi.HTTPException' imported but unused
backend/app/services/export/service.py:20:1: F401 'app.utils.security.mask.mask_id' imported but unused
backend/app/services/export/service.py:29:1: D107 Missing docstring in __init__
backend/app/services/export/service.py:62:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:121:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:203:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:304:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:347:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/__init__.py:31:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/__init__.py:42:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:11:1: F401 'typing.Union' imported but unused
backend/app/services/image/conversion.py:13:1: F401 'PIL.ImageOps' imported but unused
backend/app/services/image/conversion.py:25:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:66:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:122:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:179:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/conversion.py:231:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/image/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:44:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:67:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:92:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:114:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:137:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:158:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:176:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:198:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:217:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:240:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:264:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:290:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:312:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:329:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/interface.py:350:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:10:1: F401 'typing.Any' imported but unused
backend/app/services/image/processing.py:10:1: F401 'typing.Dict' imported but unused
backend/app/services/image/processing.py:16:1: F401 'app.utils.http_utils.download_image' imported but unused
backend/app/services/image/processing.py:22:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:45:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:61:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:98:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:125:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:175:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing.py:221:9: F811 redefinition of unused 'download_image' from line 16
backend/app/services/image/processing_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:27:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:42:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:173:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:201:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:281:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:312:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:333:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:358:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/processing_service.py:399:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:19:1: F401 'app.core.config.settings' imported but unused
backend/app/services/image/service.py:38:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:50:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:64:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:93:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:127:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:156:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:186:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:213:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:341:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/service.py:376:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:10:1: F401 'typing.Optional' imported but unused
backend/app/services/jigsawstack/client.py:10:1: F401 'typing.Union' imported but unused
backend/app/services/jigsawstack/client.py:13:1: F401 'fastapi.Depends' imported but unused
backend/app/services/jigsawstack/client.py:15:1: F401 'app.core.config.get_masked_value' imported but unused
backend/app/services/jigsawstack/client.py:49:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:73:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:301:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:361:29: F541 f-string is missing placeholders
backend/app/services/jigsawstack/client.py:593:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:642:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:693:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:830:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/client.py:923:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/interface.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/jigsawstack/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/interface.py:6:1: F401 'typing.Optional' imported but unused
backend/app/services/jigsawstack/interface.py:6:1: F401 'typing.Union' imported but unused
backend/app/services/jigsawstack/interface.py:20:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/interface.py:45:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/interface.py:66:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:10:1: F401 'typing.Optional' imported but unused
backend/app/services/jigsawstack/service.py:10:1: F401 'typing.Union' imported but unused
backend/app/services/jigsawstack/service.py:13:1: F401 'app.core.exceptions.JigsawStackConnectionError' imported but unused
backend/app/services/jigsawstack/service.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:29:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:45:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:92:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:135:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/jigsawstack/service.py:178:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/__init__.py:32:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/__init__.py:48:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:20:1: D107 Missing docstring in __init__
backend/app/services/persistence/concept_persistence_service.py:28:1: D107 Missing docstring in __init__
backend/app/services/persistence/concept_persistence_service.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:48:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:203:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:259:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:298:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:342:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:372:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:15:1: F401 'requests' imported but unused
backend/app/services/persistence/image_persistence_service.py:22:1: F401 'app.utils.jwt_utils.create_supabase_jwt' imported but unused
backend/app/services/persistence/image_persistence_service.py:22:1: F401 'app.utils.jwt_utils.create_supabase_jwt_for_storage' imported but unused
backend/app/services/persistence/image_persistence_service.py:24:1: F401 'supabase.create_client' imported but unused
backend/app/services/persistence/image_persistence_service.py:33:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:55:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:152:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:185:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:209:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:234:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:259:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:310:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:397:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:447:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:465:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/image_persistence_service.py:497:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:20:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:42:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:62:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:79:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:97:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:118:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:140:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:160:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:177:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:195:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:225:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:247:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:263:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:280:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/interface.py:303:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/__init__.py:15:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/task/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:16:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:40:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:60:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:80:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:100:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:117:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:22:1: D107 Missing docstring in __init__
backend/app/services/task/service.py:30:1: D107 Missing docstring in __init__
backend/app/services/task/service.py:40:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:122:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:196:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:259:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:324:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:393:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/utils/api_limits/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/decorators.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/decorators.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:109:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:152:5: F841 local variable 'limiter' is assigned to but never used
backend/app/utils/auth/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:23:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:69:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:92:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/data/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/utils/data/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/http_utils.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/http_utils.py:8:1: F401 'typing.Optional' imported but unused
backend/app/utils/http_utils.py:8:1: F401 'typing.Union' imported but unused
backend/app/utils/http_utils.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:24:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:69:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:99:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:136:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/jwt_utils.py:162:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:10:1: F401 'os' imported but unused
backend/app/utils/logging/setup.py:12:1: F401 'typing.Any' imported but unused
backend/app/utils/logging/setup.py:12:1: F401 'typing.Dict' imported but unused
backend/app/utils/logging/setup.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:84:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:97:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:2:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:11:1: F401 'typing.Union' imported but unused
backend/app/utils/security/mask.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:46:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:82:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/validation/__init__.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/utils/validation/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/run.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/run.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/scripts/admin/purge_data.py:2:1: D212 Multi-line docstring summary should start at the first line
backend/scripts/admin/purge_data.py:12:1: F401 'typing.Any' imported but unused
backend/scripts/admin/purge_data.py:12:1: F401 'typing.Dict' imported but unused
backend/scripts/admin/purge_data.py:14:1: F401 'app.core.config.settings' imported but unused
backend/tests/app/core/limiter/test_keys.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/core/limiter/test_keys.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/core/limiter/test_keys.py:7:1: F401 'pytest' imported but unused
backend/tests/app/core/limiter/test_redis_store.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/core/limiter/test_redis_store.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/core/supabase/test_concept_storage.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/core/supabase/test_concept_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/core/supabase/test_image_storage.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/core/supabase/test_image_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/core/supabase/test_image_storage.py:6:1: F401 'unittest.mock.ANY' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:6:1: F401 'unittest.mock.mock_open' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:9:1: F401 'requests' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:10:1: F401 'fastapi.UploadFile' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:11:1: F401 'PIL.Image' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:13:1: F401 'app.core.exceptions.ImageNotFoundError' imported but unused
backend/tests/app/core/supabase/test_image_storage.py:28:71: F841 local variable 'mock_masked' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:316:18: F841 local variable 'mock_upload' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:348:18: F841 local variable 'mock_upload' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:542:14: F841 local variable 'mock_jwt' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:609:14: F841 local variable 'mock_jwt' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:677:50: F841 local variable 'excinfo' is assigned to but never used
backend/tests/app/core/supabase/test_image_storage.py:696:14: F841 local variable 'mock_jwt' is assigned to but never used
backend/tests/app/core/supabase/test_supabase_client.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/core/supabase/test_supabase_client.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/common/test_base.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/common/test_base.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/concept/test_domain.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/concept/test_domain.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/concept/test_domain.py:8:1: F401 'pytest' imported but unused
backend/tests/app/models/concept/test_domain.py:9:1: F401 'pydantic.ValidationError' imported but unused
backend/tests/app/models/concept/test_requests.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/concept/test_requests.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/concept/test_requests.py:128:9: F841 local variable 'errors' is assigned to but never used
backend/tests/app/models/concept/test_responses.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/concept/test_responses.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/concept/test_responses.py:5:1: F401 'pytest' imported but unused
backend/tests/app/models/concept/test_responses.py:6:1: F401 'pydantic.ValidationError' imported but unused
backend/tests/app/models/export/test_request.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/export/test_request.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/task/test_response.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/models/task/test_response.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/models/task/test_response.py:5:1: F401 'pytest' imported but unused
backend/tests/app/models/task/test_response.py:6:1: F401 'pydantic.ValidationError' imported but unused
backend/tests/app/services/concept/test_concept_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/concept/test_concept_service.py:14:1: F401 'app.models.concept.response.GenerationResponse' imported but unused
backend/tests/app/services/concept/test_generation.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/concept/test_generation.py:8:1: F401 'datetime' imported but unused
backend/tests/app/services/concept/test_generation.py:10:1: F401 'typing.Any' imported but unused
backend/tests/app/services/concept/test_generation.py:10:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/concept/test_generation.py:10:1: F401 'typing.List' imported but unused
backend/tests/app/services/concept/test_generation.py:10:1: F401 'typing.Tuple' imported but unused
backend/tests/app/services/concept/test_palette.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/concept/test_palette.py:8:1: F401 'typing.Any' imported but unused
backend/tests/app/services/concept/test_palette.py:8:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/concept/test_palette.py:8:1: F401 'typing.List' imported but unused
backend/tests/app/services/concept/test_palette.py:8:1: F401 'typing.Optional' imported but unused
backend/tests/app/services/concept/test_palette.py:9:1: F401 'unittest.mock.MagicMock' imported but unused
backend/tests/app/services/concept/test_refinement.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/concept/test_refinement.py:8:1: F401 'datetime' imported but unused
backend/tests/app/services/concept/test_refinement.py:10:1: F401 'typing.List' imported but unused
backend/tests/app/services/concept/test_refinement.py:10:1: F401 'typing.Optional' imported but unused
backend/tests/app/services/export/test_export_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/export/test_export_service.py:8:1: F401 'os' imported but unused
backend/tests/app/services/export/test_export_service.py:9:1: F401 'tempfile' imported but unused
backend/tests/app/services/export/test_export_service.py:10:1: F401 'io.BytesIO' imported but unused
backend/tests/app/services/export/test_export_service.py:11:1: F401 'unittest.mock.call' imported but unused
backend/tests/app/services/export/test_export_service.py:11:1: F401 'unittest.mock.mock_open' imported but unused
backend/tests/app/services/export/test_export_service.py:14:1: F401 'PIL.Image' imported but unused
backend/tests/app/services/image/test_conversion.py:8:1: F401 'unittest.mock.Mock' imported but unused
backend/tests/app/services/image/test_conversion.py:11:1: F401 'PIL.ImageOps' imported but unused
backend/tests/app/services/image/test_conversion.py:429:72: E712 comparison to True should be 'if cond is True:' or 'if cond:'
backend/tests/app/services/image/test_image_processing_service.py:8:1: F401 'unittest.mock.ANY' imported but unused
backend/tests/app/services/image/test_image_processing_service.py:8:1: F401 'unittest.mock.Mock' imported but unused
backend/tests/app/services/image/test_image_processing_service.py:10:1: F401 'httpx' imported but unused
backend/tests/app/services/image/test_image_processing_service.py:11:1: F401 'numpy as np' imported but unused
backend/tests/app/services/image/test_image_processing_service.py:343:53: E712 comparison to True should be 'if cond is True:' or 'if cond:'
backend/tests/app/services/image/test_image_processing_service.py:371:1: D202 No blank lines allowed after function docstring
backend/tests/app/services/image/test_image_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/image/test_image_service.py:9:1: F401 'io.BytesIO' imported but unused
backend/tests/app/services/image/test_image_service.py:10:1: F401 'typing.Any' imported but unused
backend/tests/app/services/image/test_image_service.py:10:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/image/test_image_service.py:10:1: F401 'typing.List' imported but unused
backend/tests/app/services/image/test_processing.py:8:1: F401 'unittest.mock.AsyncMock' imported but unused
backend/tests/app/services/image/test_processing.py:14:1: F401 'unittest' imported but unused
backend/tests/app/services/image/test_processing.py:170:1: D202 No blank lines allowed after function docstring
backend/tests/app/services/jigsawstack/test_jigsawstack_client.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/jigsawstack/test_jigsawstack_client.py:9:1: F401 'typing.Any' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_client.py:9:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_client.py:9:1: F401 'typing.List' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_client.py:15:1: F401 'app.core.exceptions.JigsawStackError' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/jigsawstack/test_jigsawstack_service.py:12:1: F401 'app.core.exceptions.JigsawStackConnectionError' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_service.py:224:9: F401 'app.services.jigsawstack.service as service_module' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_service.py:225:9: F401 'app.services.jigsawstack.service.get_jigsawstack_service' imported but unused
backend/tests/app/services/jigsawstack/test_jigsawstack_service.py:244:13: F841 local variable 'client' is assigned to but never used
backend/tests/app/services/persistence/test_concept_persistence_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/persistence/test_concept_persistence_service.py:8:1: F401 'uuid' imported but unused
backend/tests/app/services/persistence/test_concept_persistence_service.py:9:1: F401 'typing.Any' imported but unused
backend/tests/app/services/persistence/test_concept_persistence_service.py:9:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/persistence/test_concept_persistence_service.py:9:1: F401 'typing.List' imported but unused
backend/tests/app/services/persistence/test_concept_persistence_service.py:10:1: F401 'unittest.mock.call' imported but unused
backend/tests/app/services/persistence/test_concept_persistence_service.py:13:1: F401 'requests' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/services/persistence/test_image_persistence_service.py:8:1: F401 'io' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:9:1: F401 'datetime.datetime' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:11:1: F401 'typing.Any' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:11:1: F401 'typing.Dict' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:11:1: F401 'typing.Optional' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:11:1: F401 'typing.Tuple' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:12:1: F401 'unittest.mock.call' imported but unused
backend/tests/app/services/persistence/test_image_persistence_service.py:153:24: F541 f-string is missing placeholders
backend/tests/app/services/persistence/test_image_persistence_service.py:448:9: F841 local variable 'image_data' is assigned to but never used
backend/tests/app/services/persistence/test_image_persistence_service.py:518:9: F841 local variable 'url' is assigned to but never used
backend/tests/app/services/persistence/test_image_persistence_service.py:528:9: F841 local variable 'url' is assigned to but never used
backend/tests/app/services/task/test_task_service.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/services/task/test_task_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/api_limits/test_decorators.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/api_limits/test_decorators.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/api_limits/test_endpoints.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/api_limits/test_endpoints.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/api_limits/test_endpoints.py:5:1: F401 'unittest.mock.AsyncMock' imported but unused
backend/tests/app/utils/api_limits/test_endpoints.py:241:52: E712 comparison to False should be 'if cond is False:' or 'if not cond:'
backend/tests/app/utils/api_limits/test_endpoints.py:242:52: E712 comparison to False should be 'if cond is False:' or 'if not cond:'
backend/tests/app/utils/auth/test_user.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/auth/test_user.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/logging/test_setup.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/logging/test_setup.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/logging/test_setup.py:6:1: F401 'pathlib.Path' imported but unused
backend/tests/app/utils/security/__init__.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/security/run_tests.py:2:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/security/test_mask.py:2:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/security/test_mask.py:2:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/test_http_utils.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/test_http_utils.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/test_http_utils.py:5:1: F401 'unittest.mock.MagicMock' imported but unused
backend/tests/app/utils/test_jwt_utils.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/tests/app/utils/test_jwt_utils.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/tests/app/utils/test_jwt_utils.py:7:1: F401 'time' imported but unused
backend/tests/app/utils/test_jwt_utils.py:8:1: F401 'unittest.mock.MagicMock' imported but unused
backend/tests/app/utils/test_jwt_utils.py:12:1: F401 'jose.exceptions.ExpiredSignatureError' imported but unused
scripts/check_api_routes.py:2:1: D212 Multi-line docstring summary should start at the first line
scripts/check_api_routes.py:48:1: D212 Multi-line docstring summary should start at the first line
scripts/check_api_routes.py:80:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:2:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:26:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:54:1: D212 Multi-line docstring summary should start at the first line
```

\*(Note: This is just a sample of the flake8 errors. The complete output showed hundreds of errors, primarily related to docstring formatting issues (D*\*\*), unused imports (F401), and unused variables (F841).)*

## 6. Error Summary by Category

### 6.1 Mypy Errors by Category

1. **Type Annotation Issues**

   - `no-untyped-def`: Missing function return type annotations
   - `assignment`: Incompatible types in assignments (often related to `None` vs explicit `Optional`)
   - `var-annotated`: Missing variable type annotations

2. **Module/Import Issues**

   - `import-not-found`: Can't find implementation or library stubs for modules

3. **Function/Method Call Issues**

   - `arg-type`: Argument type mismatch in function calls
   - `call-arg`: Incorrect or missing named arguments
   - `operator`: Type mismatches in operations (e.g., `/`, `*`)

4. **Class/Interface Issues**
   - `override`: Method signature incompatible with supertype
   - `attr-defined`: Accessing non-existent attributes
   - `union-attr`: Accessing attributes on potentially `None` values
   - `no-any-return`: Returning `Any` where specific type is expected

### 6.2 Flake8 Errors by Category

1. **Docstring Issues**

   - `D200`, `D212`: Docstring formatting issues (most common)
   - `D100`: Missing module docstring
   - `D107`: Missing **init** docstring

2. **Import Issues**

   - `F401`: Unused imports (most common after docstring issues)
   - `E402`: Module level import not at top of file

3. **Variable Issues**

   - `F841`: Local variable assigned but never used

4. **Style Issues**
   - `E712`: Comparison to `True`/`False` should use `is True`/`is False`
   - `F541`: f-string missing placeholders
   - `F811`: Redefinition of unused variable

## 7. Implementation Plan

- **Branch:** Create a new branch `fix/flake8-mypy-backend`.
- **Commits:** Commit changes incrementally, likely per file or per phase/category of errors.
- **Testing:** After significant changes in a module, consider running related `pytest` tests to catch regressions.
- **Pull Request:** Once all errors are resolved and confirmed by pre-commit hooks, create a PR for review.

## 8. Open Questions

- Are there specific files or modules that should be prioritized?
- Should complexity errors (C901) be tackled early or late? (Plan suggests Phase 3)

## 9. Future Considerations

- Add `mypy` and `flake8` checks to CI/CD pipeline if not already present.
- Periodically review `flake8` and `mypy` configurations for potential improvements.

---
