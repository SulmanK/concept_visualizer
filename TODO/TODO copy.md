> git -c user.useConfigOnly=true commit --quiet --allow-empty-message --file -
> trim trailing whitespace.................................................Failed

- hook id: trailing-whitespace
- exit code: 1
- files were modified by this hook

Fixing scripts/check_shared_components.py
Fixing .pre-commit-config.yaml
Fixing scripts/check_api_routes.py
Fixing scripts/README.md

fix end of files.........................................................Failed

- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing scripts/check_shared_components.py
Fixing .pre-commit-config.yaml
Fixing scripts/check_api_routes.py
Fixing scripts/README.md

check yaml...............................................................Passed
check json...............................................................Passed
check for added large files..............................................Passed
debug statements (python)................................................Passed
check for merge conflicts................................................Passed
black....................................................................Failed

- hook id: black
- files were modified by this hook

reformatted backend\app\api\middleware\auth_middleware.py
reformatted backend\app\api\middleware\rate_limit_apply.py
reformatted backend\app\api\dependencies.py
reformatted backend\app\api\routes\api.py
reformatted backend\app\api\middleware\rate_limit_headers.py
reformatted backend\app\api\routes\auth\auth_routes.py
reformatted backend\app\api\routes\concept\example_error_handling.py
reformatted backend\app\api\router.py
reformatted backend\app\api\routes\health\_\_init**.py
reformatted backend\app\api\errors.py
reformatted backend\app\api\routes\health\endpoints.py
reformatted backend\app\api\routes\export\export_routes.py
reformatted backend\app\api\routes\_\_tests**\concept_test.py
reformatted backend\app\api\routes\health\check.py
reformatted backend\app\core\factory.py
reformatted backend\app\api\routes\task\routes.py
reformatted backend\app\core\config.py
reformatted backend\app\core\limiter\_\_init**.py
reformatted backend\app\api\routes\concept_storage\storage_routes.py
reformatted backend\app\core\limiter\config.py
reformatted backend\app\core\limiter\decorators.py
reformatted backend\app\api\routes\concept\refinement.py
reformatted backend\app\core\limiter\keys.py
reformatted backend\app\models\_\_init**.py
reformatted backend\app\models\common\base.py
reformatted backend\app\api\routes\health\limits.py
reformatted backend\app\models\concept\request.py
reformatted backend\app\core\supabase\client.py
reformatted backend\app\models\concept\domain.py
reformatted backend\app\core\limiter\redis_store.py
reformatted backend\app\models\task\response.py
reformatted backend\app\models\export\request.py
reformatted backend\app\services\concept\_\_init**.py
reformatted backend\app\services\concept\interface.py
reformatted backend\app\core\exceptions.py
reformatted backend\app\models\concept\response.py
reformatted backend\app\core\supabase\image_storage.py
reformatted backend\app\services\export\interface.py
reformatted backend\app\services\concept\palette.py
reformatted backend\app\services\image\_\_init**.py
reformatted backend\app\services\concept\refinement.py
reformatted backend\app\services\concept\generation.py
reformatted backend\app\services\image\interface.py
reformatted backend\app\core\supabase\concept_storage.py
reformatted backend\app\services\export\service.py
reformatted backend\app\services\jigsawstack\_\_init**.py
reformatted backend\app\services\concept\service.py
reformatted backend\app\services\jigsawstack\interface.py
reformatted backend\app\services\persistence\_\_init**.py
reformatted backend\app\services\jigsawstack\service.py
reformatted backend\app\services\image\conversion.py
reformatted backend\app\services\image\service.py
reformatted backend\app\services\task\interface.py
reformatted backend\app\api\routes\concept\generation.py
reformatted backend\app\services\image\processing.py
reformatted backend\app\services\image\processing_service.py
reformatted backend\app\services\persistence\interface.py
reformatted backend\app\services\persistence\concept_persistence_service.py
reformatted backend\app\utils\api_limits\decorators.py
reformatted backend\app\utils\auth\user.py
reformatted backend\app\utils\logging\setup.py
reformatted backend\app\utils\jwt_utils.py
reformatted backend\scripts\admin\purge_data.py
reformatted backend\app\utils\api_limits\endpoints.py
reformatted backend\app\services\task\service.py
reformatted backend\tests\app\core\limiter\test_keys.py
reformatted backend\tests\app\models\common\test_base.py
reformatted backend\app\services\persistence\image_persistence_service.py
reformatted backend\tests\app\models\concept\test_requests.py
reformatted backend\tests\app\core\supabase\test_supabase_client.py
reformatted backend\tests\app\models\concept\test_domain.py
reformatted backend\tests\app\models\export\test_request.py
reformatted backend\tests\app\models\task\test_response.py
reformatted backend\tests\app\models\concept\test_responses.py
reformatted backend\tests\app\core\limiter\test_redis_store.py
reformatted backend\tests\app\services\concept\test_concept_service.py
reformatted backend\tests\app\services\concept\test_generation.py
reformatted backend\tests\app\services\concept\test_refinement.py
reformatted backend\tests\app\services\concept\test_palette.py
reformatted backend\tests\app\core\supabase\test_image_storage.py
reformatted backend\app\services\jigsawstack\client.py
reformatted backend\tests\app\services\export\test_export_service.py
reformatted backend\tests\app\core\supabase\test_concept_storage.py
reformatted backend\tests\app\services\image\test_image_service.py
reformatted backend\tests\app\services\image\test_conversion.py
reformatted backend\tests\app\services\jigsawstack\test_jigsawstack_service.py
reformatted backend\tests\app\services\jigsawstack\test_jigsawstack_client.py
reformatted backend\tests\app\utils\api_limits\test_decorators.py
reformatted backend\tests\app\utils\auth\test_user.py
reformatted backend\tests\app\utils\security\run_tests.py
reformatted backend\tests\app\utils\logging\test_setup.py
reformatted backend\tests\app\utils\api_limits\test_endpoints.py
reformatted backend\tests\app\utils\test_http_utils.py
reformatted backend\tests\app\services\persistence\test_concept_persistence_service.py
reformatted backend\tests\app\utils\security\test_mask.py
reformatted scripts\check_api_routes.py
reformatted backend\tests\app\services\image\test_image_processing_service.py
reformatted scripts\check_shared_components.py
reformatted backend\tests\app\services\task\test_task_service.py
reformatted backend\tests\app\utils\test_jwt_utils.py
reformatted backend\tests\app\services\persistence\test_image_persistence_service.py
reformatted backend\tests\app\services\image\test_processing.py

All done! \u2728 \U0001f370 \u2728
102 files reformatted, 30 files left unchanged.

isort....................................................................Failed

- hook id: isort
- files were modified by this hook

Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\dependencies.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\errors.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\routes\concept\example_error_handling.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\routes\concept\generation.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\routes\concept\refinement.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\api\routes\concept_storage\storage_routes.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\models\_\_init**.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\concept\_\_init**.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\concept\service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\export\service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\image\_\_init**.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\image\processing_service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\image\service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\jigsawstack\client.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\jigsawstack\service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\app\services\persistence\_\_init**.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\core\limiter\test_keys.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\core\supabase\test_supabase_client.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\models\concept\test_domain.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\models\concept\test_responses.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\image\test_conversion.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\image\test_image_processing_service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\image\test_processing.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\jigsawstack\test_jigsawstack_client.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\jigsawstack\test_jigsawstack_service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\services\persistence\test_concept_persistence_service.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\utils\auth\test_user.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\backend\tests\app\utils\test_jwt_utils.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\scripts\check_api_routes.py
Fixing C:\Users\sulma\OneDrive\Documents\Data Science\concept_visualizer\scripts\check_shared_components.py

flake8...................................................................Failed

- hook id: flake8
- exit code: 1

backend/app/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/api/routes/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:19:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:32:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:32:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:52:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:103:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:103:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:156:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:156:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:178:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:178:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:226:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:226:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/concept_test.py:265:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/concept_test.py:265:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/health_test.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/health_test.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/health_test.py:11:1: D200 One-line docstring should fit on one line with quotes
backend/app/api/routes/**tests**/health_test.py:11:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/**tests**/health_test.py:28:1: D205 1 blank line required between summary line and description
backend/app/api/routes/**tests**/health_test.py:28:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/api.py:1:1: D100 Missing docstring in public module
backend/app/api/routes/auth/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Any' imported but unused
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Dict' imported but unused
backend/app/api/routes/auth/auth_routes.py:9:1: F401 'typing.Optional' imported but unused
backend/app/api/routes/auth/auth_routes.py:15:1: F401 'app.api.errors.ResourceNotFoundError' imported but unused
backend/app/api/routes/auth/auth_routes.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:85:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/auth/auth_routes.py:136:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:22:1: F401 'app.models.concept.response.GenerationResponse' imported but unused
backend/app/api/routes/concept/example_error_handling.py:36:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/example_error_handling.py:87:9: F841 local variable 'e' is assigned to but never used
backend/app/api/routes/concept/example_error_handling.py:121:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:11:1: F401 'typing.Any' imported but unused
backend/app/api/routes/concept/generation.py:11:1: F401 'typing.Dict' imported but unused
backend/app/api/routes/concept/generation.py:11:1: F401 'typing.Optional' imported but unused
backend/app/api/routes/concept/generation.py:14:1: F401 'fastapi.responses.JSONResponse' imported but unused
backend/app/api/routes/concept/generation.py:15:1: F401 'slowapi.Limiter' imported but unused
backend/app/api/routes/concept/generation.py:16:1: F401 'slowapi.util.get_remote_address' imported but unused
backend/app/api/routes/concept/generation.py:21:1: F401 'app.api.errors.BadRequestError' imported but unused
backend/app/api/routes/concept/generation.py:21:1: F401 'app.api.errors.UnauthorizedError' imported but unused
backend/app/api/routes/concept/generation.py:23:1: F401 'app.core.constants.TASK_STATUS_COMPLETED' imported but unused
backend/app/api/routes/concept/generation.py:23:1: F401 'app.core.constants.TASK_STATUS_FAILED' imported but unused
backend/app/api/routes/concept/generation.py:30:1: F401 'app.models.concept.response.PaletteVariation' imported but unused
backend/app/api/routes/concept/generation.py:35:1: F401 'app.services.persistence.interface.ConceptPersistenceServiceInterface' imported but unused
backend/app/api/routes/concept/generation.py:39:1: F401 'app.utils.api_limits.decorators.store_rate_limit_info' imported but unused
backend/app/api/routes/concept/generation.py:40:1: F811 redefinition of unused 'apply_multiple_rate_limits' from line 38
backend/app/api/routes/concept/generation.py:40:1: F811 redefinition of unused 'apply_rate_limit' from line 38
backend/app/api/routes/concept/generation.py:40:1: F401 'app.utils.api_limits.endpoints.apply_rate_limit' imported but unused
backend/app/api/routes/concept/generation.py:56:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:335:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:471:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:671:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept/generation.py:710:16: F821 undefined name 'TaskNotFoundError'
backend/app/api/routes/concept/generation.py:712:19: F821 undefined name 'ResourceNotFoundError'
backend/app/api/routes/concept/generation.py:716:12: F821 undefined name 'ResourceNotFoundError'
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
backend/app/api/routes/concept_storage/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:35:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:136:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/concept_storage/storage_routes.py:203:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/export_routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/export/export_routes.py:37:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/health/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/api/routes/task/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:17:1: F401 'app.services.task.interface.TaskServiceInterface' imported but unused
backend/app/api/routes/task/routes.py:18:1: F401 'app.services.task.service.TaskError' imported but unused
backend/app/api/routes/task/routes.py:36:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:93:1: D212 Multi-line docstring summary should start at the first line
backend/app/api/routes/task/routes.py:155:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/core/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/core/limiter/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/**init**.py:39:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/**init**.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/limiter/**init**.py:91:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/core/middleware/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/core/middleware/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/client.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:737:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/concept_storage.py:795:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:408:13: F841 local variable 'token' is assigned to but never used
backend/app/core/supabase/image_storage.py:534:1: D212 Multi-line docstring summary should start at the first line
backend/app/core/supabase/image_storage.py:591:29: F541 f-string is missing placeholders
backend/app/main.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/common/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/base.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/common/base.py:8:1: F401 'typing.Any' imported but unused
backend/app/models/common/base.py:8:1: F401 'typing.Dict' imported but unused
backend/app/models/common/base.py:8:1: F401 'typing.List' imported but unused
backend/app/models/common/base.py:10:1: F401 'pydantic.HttpUrl' imported but unused
backend/app/models/concept/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/concept/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/domain.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/request.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/concept/response.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/export/request.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/export/request.py:7:1: F401 're' imported but unused
backend/app/models/task/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/models/task/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/task/response.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/models/task/response.py:8:1: F401 'datetime.datetime' imported but unused
backend/app/services/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/concept/**init**.py:34:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/services/export/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/services/export/service.py:29:1: D107 Missing docstring in **init**
backend/app/services/export/service.py:62:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:121:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:203:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:304:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/export/service.py:347:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/**init**.py:31:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/image/**init**.py:42:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/services/jigsawstack/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/services/persistence/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/**init**.py:32:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/**init**.py:48:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/persistence/concept_persistence_service.py:20:1: D107 Missing docstring in **init**
backend/app/services/persistence/concept_persistence_service.py:28:1: D107 Missing docstring in **init**
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
backend/app/services/task/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/**init**.py:15:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/services/task/interface.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:16:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:40:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:60:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:80:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:100:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/interface.py:117:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:22:1: D107 Missing docstring in **init**
backend/app/services/task/service.py:30:1: D107 Missing docstring in **init**
backend/app/services/task/service.py:40:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:52:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:122:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:196:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:259:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:324:1: D212 Multi-line docstring summary should start at the first line
backend/app/services/task/service.py:393:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/**init**.py:1:1: D200 One-line docstring should fit on one line with quotes
backend/app/utils/api_limits/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/decorators.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/decorators.py:19:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:21:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:109:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/api_limits/endpoints.py:152:5: F841 local variable 'limiter' is assigned to but never used
backend/app/utils/auth/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:23:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:69:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/auth/user.py:92:1: D212 Multi-line docstring summary should start at the first line
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
backend/app/utils/logging/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:10:1: F401 'os' imported but unused
backend/app/utils/logging/setup.py:12:1: F401 'typing.Any' imported but unused
backend/app/utils/logging/setup.py:12:1: F401 'typing.Dict' imported but unused
backend/app/utils/logging/setup.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:84:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/logging/setup.py:97:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:2:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:11:1: F401 'typing.Union' imported but unused
backend/app/utils/security/mask.py:18:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:46:1: D212 Multi-line docstring summary should start at the first line
backend/app/utils/security/mask.py:82:1: D212 Multi-line docstring summary should start at the first line
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
backend/tests/app/services/image/test_processing.py:169:1: D202 No blank lines allowed after function docstring
backend/tests/app/services/image/test_processing.py:203:49: F821 undefined name 'ANY'
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
backend/tests/app/utils/security/**init**.py:1:1: D212 Multi-line docstring summary should start at the first line
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
scripts/check_api_routes.py:17:1: F401 'typing.Dict' imported but unused
scripts/check_api_routes.py:17:1: F401 'typing.Optional' imported but unused
scripts/check_api_routes.py:17:1: F401 'typing.Set' imported but unused
scripts/check_api_routes.py:48:1: D212 Multi-line docstring summary should start at the first line
scripts/check_api_routes.py:80:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:2:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:26:1: D212 Multi-line docstring summary should start at the first line
scripts/check_shared_components.py:54:1: D212 Multi-line docstring summary should start at the first line

mypy.....................................................................Failed

- hook id: mypy
- exit code: 2

backend\app\api\errors.py:506: error: Library stubs not installed for "dateutil" [import-untyped]
backend\app\api\errors.py:506: note: Hint: "python3 -m pip install types-python-dateutil"
backend\app\api\errors.py:506: note: (or run "mypy --install-types" to install all missing stub packages)
backend\app\api\errors.py:506: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
backend\app\services\jigsawstack\client.py: error: Source file found twice under different module names: "app.services.jigsawstack.client" and "backend.app.services.jigsawstack.client"
backend\app\services\jigsawstack\client.py: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#mapping-file-paths-to-modules for more info
backend\app\services\jigsawstack\client.py: note: Common resolutions include: a) adding `__init__.py` somewhere, b) using `--explicit-package-bases` or adjusting MYPYPATH
Found 2 errors in 2 files (errors prevented further checking)

prettier.................................................................Failed

- hook id: prettier
- exit code: 2
- files were modified by this hook

docs/backend/core/supabase/image_storage.md
frontend/my-app/src/utils/**tests**/stringUtils.test.ts
frontend/my-app/src/hooks/useConceptMutations.ts
frontend/my-app/src/types/ui.types.ts
docs/frontend/services/apiClient.md
docs/backend/api/routes/health/utils.md
frontend/my-app/playwright-report/trace/assets/codeMirrorModule-DpJ-EmBQ.js
docs/frontend/features/refinement/RefinementPage.md
frontend/my-app/src/features/concepts/detail/components/EnhancedImagePreview.tsx
docs/backend/api/errors.md
frontend/my-app/src/components/ui/ConceptCard.module.css
frontend/my-app/src/features/concepts/create/index.ts
docs/backend/services/concept/refinement.md
Design/supabase_setup_guide.md
frontend/my-app/src/types/index.ts
frontend/my-app/src/services/configService.ts
docs/frontend/components/concept/ConceptImage.md
docs/backend/core/limiter/decorators.md
docs/frontend/features/landing/components/RecentConceptsSection.md
Design/supabase_signed_url_migration.md
Design/concept_visualizer_design.md
docs/frontend/features/landing/components/ConceptFormSection.md
frontend/my-app/src/services/**tests**/supabaseClient.test.ts
frontend/my-app/src/components/ui/TextArea.tsx
frontend/my-app/src/features/refinement/**tests**/RefinementSelectionPage.test.tsx
frontend/my-app/src/hooks/**tests**/useNetworkStatus.test.tsx
docs/frontend/features/concepts/recent/components/ConceptList.md
frontend/my-app/src/utils/validationUtils.ts
docs/backend/services/task/service.md
frontend/my-app/src/components/ui/**tests**/OptimizedImage.test.tsx
docs/backend/core/README.md
frontend/my-app/src/hooks/useSessionQuery.ts
frontend/my-app/src/utils/formatUtils.ts
docs/frontend/features/concepts/recent/RecentConceptsPage.md
frontend/my-app/src/components/ui/ConceptCard.tsx
frontend/my-app/src/features/landing/**tests**/LandingPage.test.tsx
frontend/my-app/src/theme.tsx
frontend/my-app/src/setupTests.ts
Design/backend/service_layer.md
frontend/my-app/playwright-report/trace/codeMirrorModule.C3UTv-Ge.css
frontend/my-app/playwright-report/trace/index.CUq7VgrV.js
docs/frontend/features/refinement/components/RefinementActions.md
TODO/frontend-backend.md
frontend/my-app/src/utils/**tests**/errorUtils.test.ts
docs/frontend/hooks/useExportImageMutation.md
Design/backend/api_endpoints.md
frontend/my-app/src/utils/errorUtils.ts
frontend/my-app/src/hooks/animation/useAnimatedValue.tsx
frontend/my-app/src/services/mocks/mockHooks.ts
Design/session_optimization_plan.md
Design/frontend/state_management.md
docs/frontend/hooks/useTaskQueries.md
Design/backend/jigsawstack_client.md
frontend/my-app/src/services/mocks/testSetup.ts
frontend/my-app/tests/e2e/concept-generation.spec.ts
docs/backend/utils/http_utils.md
docs/backend/services/user_service.md
docs/backend/services/task/interface.md
docs/backend/services/image/interface.md
frontend/my-app/src/components/ui/ErrorMessage.tsx
docs/backend/api/routes/health/check.md
frontend/my-app/src/components/concept/**tests**/ConceptResult.test.tsx
frontend/my-app/src/features/refinement/**tests**/RefinementPage.test.tsx
frontend/my-app/src/hooks/useTaskQueries.ts
frontend/my-app/src/features/landing/components/HowItWorks.tsx
docs/backend/services/concept/service.md
frontend/my-app/tailwind.config.js
docs/backend/utils/data/README.md
frontend/my-app/src/features/index.ts
frontend/my-app/src/utils/**tests**/dev-logging.test.ts
frontend/my-app/src/hooks/**tests**/useErrorHandling.test.tsx
frontend/my-app/src/components/concept/ConceptForm.tsx
docs/backend/utils/security/mask.md
frontend/my-app/src/hooks/useErrorHandling.tsx
Design/frontend/old/index.ts
docs/backend/services/README.md
frontend/my-app/src/components/common/QueryResultHandler.tsx
docs/frontend/features/refinement/components/RefinementForm.md
docs/backend/models/task/response.md
docs/frontend/theme.md
docs/backend/core/constants.md
docs/frontend/utils/formatUtils.md
frontend/my-app/src/services/**tests**/eventService.test.ts
Design/frontend/component_mockups/ModernFooterComponent.tsx
docs/frontend/components/common/QueryResultHandler.md
frontend/my-app/src/components/ui/Button.tsx
docs/frontend/api/README.md
docs/backend/core/limiter/config.md
frontend/my-app/src/contexts/AuthContext.tsx
docs/frontend/main.md
frontend/my-app/src/services/mocks/mockApiService.ts
Design/frontend/refinement_feature.md
docs/backend/api/routes/health/endpoints.md
docs/frontend/README.md
docs/frontend/hooks/useConceptMutations.md
docs/frontend/assets/README.md
docs/frontend/setupTests.md
frontend/my-app/src/components/ui/SkeletonLoader.tsx
Design/prompt_optimization.md
docs/frontend/services/conceptService.md
frontend/my-app/src/types/api.types.ts
docs/frontend/components/ui/TextArea.md
docs/frontend/features/concepts/detail/ConceptDetailPage.md
docs/backend/utils/validation/README.md
frontend/my-app/src/contexts/RateLimitContext.tsx
frontend/my-app/src/components/RateLimitsPanel/RateLimitsPanel.tsx
frontend/my-app/src/hooks/useNetworkStatus.tsx
frontend/my-app/src/features/concepts/detail/components/ExportOptions.tsx
frontend/my-app/src/hooks/**tests**/useToast.test.tsx
frontend/my-app/src/utils/dev-logging.ts
frontend/my-app/src/components/concept/ConceptResult.tsx
docs/backend/models/concept/domain.md
frontend/my-app/playwright-report/trace/sw.bundle.js
frontend/my-app/src/components/ui/Toast.tsx
backend/supabase/functions/cleanup-old-data/index.ts
frontend/my-app/src/types/form.types.ts
frontend/my-app/src/services/mocks/index.ts
docs/backend/core/limiter/README.md
frontend/my-app/src/components/ui/**tests**/Button.test.tsx
frontend/my-app/src/features/refinement/components/index.ts
frontend/my-app/src/config/**tests**/queryKeys.test.ts
frontend/my-app/src/index.css
docs/frontend/components/layout/Footer.md
frontend/my-app/src/components/ui/LoadingIndicator.tsx
docs/frontend/services/eventService.md
Design/frontend/old/EnhancedImagePreview.tsx
frontend/my-app/src/hooks/useConceptQueries.ts
docs/backend/api/routes/README.md
TODO/backend_refacotr.md
docs/frontend/utils/stringUtils.md
frontend/my-app/README.md
Design/refactoring/jigsawstack_client.md
docs/backend/api/middleware/rate_limit_apply.md
docs/frontend/utils/url.md
frontend/my-app/src/utils/url.ts
docs/backend/core/exceptions.md
docs/frontend/components/ui/Select.md
docs/backend/utils/api_limits/endpoints.md
frontend/my-app/src/services/eventService.ts
docs/frontend/contexts/AuthContext.md
frontend/my-app/src/hooks/useRateLimitsQuery.ts
docs/frontend/features/landing/components/HowItWorks.md
frontend/my-app/src/features/landing/components/ConceptHeader.tsx
docs/frontend/components/concept/ConceptResult.md
frontend/my-app/vitest.config.ts
docs/frontend/components/ui/Button.md
docs/frontend/hooks/useNetworkStatus.md
docs/backend/services/concept_service.md
docs/backend/api/routes/auth/auth_routes.md
docs/frontend/components/ui/ColorPalette.md
docs/backend/api/router.md
Design/rate_limit_optimization.md
frontend/my-app/src/types/concept.types.ts
Design/refactoring/image_services.md
frontend/my-app/src/config/**tests**/apiEndpoints.test.ts
frontend/my-app/src/hooks/animation/index.ts
frontend/my-app/src/components/ui/index.ts
frontend/my-app/src/styles/variables.css
Design/frontend/component_mockups/Concept Visualizer_files/css2.css
docs/frontend/styles/README.md
frontend/my-app/tests/e2e/concept-refinement.spec.ts
docs/frontend/features/refinement/components/RefinementHeader.md
Design/supabase_anonymous_auth_migration.md
TODO/backup_todo_before.md
docs/frontend/utils/README.md
docs/backend/core/factory.md
docs/backend/services/persistence/image_persistence_service.md
frontend/my-app/src/features/refinement/components/RefinementActions.tsx
frontend/my-app/src/components/RateLimitsPanel/index.ts
TODO/V1_Refactor.md
docs/frontend/hooks/useConfigQuery.md
frontend/my-app/src/features/concepts/recent/RecentConceptsPage.tsx
frontend/my-app/src/components/ui/**tests**/Card.test.tsx
docs/backend/utils/api_limits/decorators.md
docs/backend/services/image/processing_service.md
frontend/my-app/src/features/landing/index.ts
frontend/my-app/visual-regression.config.ts
Design/frontend/hooks_and_services.md
frontend/my-app/src/features/landing/components/ResultsSection.tsx
docs/frontend/components/ui/Toast.md
Design/frontend/old/ConceptDetailPage.tsx
frontend/my-app/src/features/refinement/components/RefinementForm.tsx
frontend/my-app/postcss.config.cjs
docs/frontend/features/concepts/detail/components/EnhancedImagePreview.md
frontend/my-app/src/components/TaskStatusBar.tsx
frontend/my-app/src/components/ui/**tests**/SkeletonLoader.test.tsx
frontend/my-app/src/features/concepts/recent/index.ts
frontend/my-app/src/components/ui/**tests**/Spinner.test.tsx
frontend/my-app/playwright-report/trace/xtermModule.Beg8tuEN.css
TODO/performance_opt.md
frontend/my-app/src/features/concepts/detail/ConceptDetailPage.tsx
docs/backend/api/README.md
frontend/my-app/src/hooks/**tests**/useApi.test.ts
Design/update_schema.md
docs/frontend/components/ui/SkeletonLoader.md
docs/backend/api/routes/concept/generation.md
docs/frontend/components/ui/ErrorMessage.md
docs/frontend/features/landing/LandingPage.md
Design/realtime_design.md
frontend/my-app/src/components/common/**tests**/QueryResultHandler.test.tsx
docs/backend/services/image/service.md
frontend/my-app/src/hooks/animation/useAnimatedMount.tsx
frontend/my-app/src/features/refinement/RefinementPage.tsx
docs/backend/core/limiter/keys.md
docs/frontend/hooks/useToast.md
docs/backend/README.md
Design/frontend_state_refactor_progress.md
Design/frontend/component_mockups/CombinedFooterReactComponent.tsx
docs/frontend/features/concepts/detail/components/ExportOptions.md
docs/backend/services/jigsawstack/client.md
frontend/my-app/src/services/**tests**/configService.test.ts
docs/backend/main.md
frontend/my-app/src/features/landing/components/RecentConceptsSection.tsx
Design/image_rate_limit.md
frontend/my-app/src/hooks/**tests**/mocks/supabaseMock.ts
docs/frontend/components/TaskStatusBar.md
Design/backend/data_models.md
frontend/my-app/src/utils/**tests**/logger.test.ts
docs/frontend/components/ui/Input.md
Design/frontend_state_management_refactor.md
Design/design_system.md
Design/frontend/component_mockups/Concept Visualizer_files/main.tsx
frontend/my-app/src/components/ui/**tests**/LoadingIndicator.test.tsx
docs/frontend/components/ui/Spinner.md
docs/backend/models/concept/request.md
docs/frontend/utils/validationUtils.md
frontend/my-app/src/hooks/index.ts
frontend/my-app/src/services/conceptService.ts
frontend/my-app/test-results/accessibility-results.json
frontend/my-app/src/services/rateLimitService.ts
TODO/Backup_TODO.md
docs/frontend/hooks/useErrorHandling.md
frontend/my-app/src/features/landing/components/index.ts
Design/rate_limit_production_enhancements.md
docs/frontend/types/README.md
Design/modal_preview_enhancement.md
frontend/my-app/playwright-report/trace/index.CFOW-Ezb.css
TODO/finished_task-14.md
frontend/my-app/src/features/refinement/index.ts
docs/backend/api/dependencies.md
Design/backend/supabase_integration.md
Design/refactoring_plan.md
docs/frontend/hooks/useRateLimitsQuery.md
docs/backend/api/routes/concept/example_error_handling.md
frontend/my-app/src/components/concept/**tests**/ConceptRefinementForm.test.tsx
docs/frontend/utils/logger.md
frontend/my-app/src/features/landing/types/index.ts
docs/frontend/components/concept/ConceptRefinementForm.md
Design/backend_scaling_vercel.md
Design/supabase_storage_security.md
frontend/my-app/playwright.config.ts
Design/backend/semantic_color_mapping.md
frontend/my-app/src/contexts/**tests**/RateLimitContext.test.tsx
frontend/my-app/src/contexts/**tests**/TaskContext.test.tsx
Design/frontend/old/ExportOptions.tsx
docs/backend/services/persistence/interface.md
frontend/my-app/src/hooks/useToast.tsx
docs/frontend/App.md
docs/frontend/hooks/animation/useAnimatedValue.md
frontend/my-app/src/services/**tests**/apiInterceptors.test.ts
docs/frontend/components/layout/MainLayout.md
frontend/my-app/src/features/concepts/detail/index.ts
docs/frontend/components/ui/LoadingIndicator.md
[error] frontend/my-app/src/hooks/**tests**/useRateLimitsQuery.test.ts: SyntaxError: '>' expected. (55:28)
[error] 53 | const createWrapper = () => {
[error] 54 | return ({ children }: { children: React.ReactNode }) => (
[error] > 55 | <QueryClientProvider client = {queryClient}>{children}</QueryClientProvider>
[error] | ^
[error] 56 | );
[error] 57 | };
[error] 58 |
docs/frontend/services/configService.md
frontend/my-app/src/components/layout/Header.tsx
frontend/my-app/src/hooks/useTaskSubscription.ts
frontend/my-app/vite.config.ts
docs/frontend/components/ui/ToastContainer.md
frontend/my-app/src/components/ui/ToastContainer.tsx
frontend/my-app/tests/e2e/accessibility.spec.ts
docs/backend/services/export/service.md
frontend/my-app/src/components/ui/**tests**/ErrorMessage.test.tsx
docs/frontend/utils/errorUtils.md
docs/backend/core/supabase/concept_storage.md
docs/backend/services/image/processing.md
docs/frontend/components/RateLimitsPanel/RateLimitsPanel.md
frontend/my-app/src/components/layout/index.ts
docs/frontend/utils/dev-logging.md
frontend/my-app/src/features/concepts/recent/**tests**/RecentConceptsPage.test.tsx
frontend/my-app/src/components/ui/OfflineStatus.tsx
frontend/my-app/src/features/concepts/detail/components/**tests**/EnhancedImagePreview.test.tsx
frontend/my-app/src/components/layout/**tests**/Header.test.tsx
docs/backend/models/README.md
docs/backend/utils/auth/user.md
Design/frontend/concept_creator.md
Design/final_refactor.md
frontend/my-app/src/features/concepts/recent/components/**tests**/ConceptList.test.tsx
frontend/my-app/src/components/ui/ColorPalette.tsx
Design/initial_concept.md
docs/frontend/contexts/RateLimitContext.md
frontend/my-app/src/features/concepts/detail/components/ExportOptions.css
frontend/my-app/src/components/ui/**tests**/ColorPalette.test.tsx
frontend/my-app/src/components/layout/Footer.tsx
frontend/my-app/tests/e2e/visual-regression.spec.ts
docs/frontend/components/ui/OptimizedImage.md
TODO/state_management.md
docs/frontend/contexts/README.md
frontend/my-app/src/hooks/animation/usePrefersReducedMotion.tsx
docs/frontend/hooks/useConceptQueries.md
docs/frontend/services/supabaseClient.md
frontend/my-app/src/contexts/TaskContext.tsx
frontend/my-app/src/features/landing/components/ConceptFormSection.tsx
docs/frontend/api/task.md
Design/fixing_SRA.md
frontend/my-app/src/components/ui/ErrorBoundary.tsx
frontend/my-app/src/config/apiEndpoints.ts
frontend/my-app/src/features/concepts/index.ts
docs/frontend/features/concepts/recent/components/RecentConceptsHeader.md
frontend/my-app/src/components/common/index.ts
frontend/my-app/src/services/**tests**/apiClient.test.ts
frontend/my-app/src/components/layout/MainLayout.tsx
docs/frontend/hooks/animation/usePrefersReducedMotion.md
frontend/my-app/playwright-report/trace/uiMode.CHJSAD7F.js
docs/backend/services/concept/generation.md
docs/backend/services/export/interface.md
docs/backend/core/supabase/client.md
docs/backend/api/middleware/README.md
frontend/my-app/src/utils/logger.ts
docs/backend/utils/jwt_utils.md
docs/backend/services/image_service.md
docs/backend/api/routes/concept/refinement.md
frontend/my-app/src/utils/**tests**/validationUtils.test.ts
docs/backend/api/middleware/auth_middleware.md
docs/frontend/services/rateLimitService.md
frontend/my-app/tests/e2e/fixtures.ts
docs/backend/api/routes/export/export_routes.md
Design/refactoring/session_storage_services.md
Design/design_concepts.md
frontend/my-app/src/services/supabaseClient.ts
frontend/my-app/src/components/concept/ConceptResult.module.css
frontend/my-app/eslint.config.js
docs/backend/services/persistence/concept_persistence_service.md
frontend/my-app/src/components/ui/**tests**/Input.test.tsx
docs/frontend/hooks/useSessionQuery.md
frontend/my-app/src/styles/global.css
TODO/old_tasks_v1_refactor.md
frontend/my-app/src/hooks/useExportImageMutation.ts
backend/app/api/ERROR_HANDLING.md
frontend/my-app/src/api/**tests**/task.test.ts
scripts/README.md
frontend/my-app/src/components/concept/**tests**/ConceptForm.test.tsx
frontend/my-app/src/components/concept/ConceptImage.tsx
frontend/my-app/src/App.tsx
frontend/my-app/src/styles/animations.css
docs/backend/api/routes/task/routes.md
docs/backend/services/concept/interface.md
frontend/my-app/src/components/concept/ConceptRefinementForm.tsx
docs/frontend/components/layout/Header.md
frontend/my-app/src/main.tsx
frontend/my-app/src/utils/**tests**/url.test.ts
Design/how-to-implement-jwt-security.md
Design/technical_explaination.md
frontend/my-app/src/utils/**tests**/formatUtils.test.ts
frontend/my-app/src/components/ui/Spinner.tsx
frontend/my-app/src/test-utils.tsx
frontend/my-app/src/components/layout/**tests**/Footer.test.tsx
docs/frontend/components/README.md
docs/frontend/services/README.md
TODO/TODO.md
docs/frontend/features/README.md
docs/backend/api/middleware/rate_limit_headers.md
frontend/my-app/src/services/apiClient.ts
frontend/my-app/src/config/queryKeys.ts
docs/backend/models/concept/response.md
docs/backend/core/config.md
frontend/my-app/src/services/**tests**/rateLimitService.test.ts
Design/frontend/component_mockups/ExportOptionsComponent.tsx
docs/backend/utils/logging/setup.md
docs/frontend/features/refinement/RefinementSelectionPage.md
frontend/my-app/src/features/refinement/components/ComparisonView.tsx
frontend/my-app/src/components/concept/**tests**/ConceptImage.test.tsx
docs/frontend/hooks/animation/useAnimatedMount.md
docs/frontend/features/concepts/README.md
frontend/my-app/src/hooks/useConfigQuery.ts
docs/backend/api/routes/health/limits.md
Design/frontend-supabase-integration.md
frontend/my-app/src/services/**tests**/conceptService.test.ts
frontend/my-app/src/features/landing/LandingPage.tsx
frontend/my-app/src/features/refinement/RefinementSelectionPage.tsx
frontend/my-app/src/components/ui/OptimizedImage.tsx
frontend/my-app/src/components/ui/FeatureSteps.tsx
frontend/my-app/tests/e2e/responsive.spec.ts
frontend/my-app/src/components/concept/index.ts
frontend/my-app/src/features/concepts/detail/**tests**/ConceptDetailPage.test.tsx
docs/backend/services/jigsawstack/service.md
Design/Deployment-refactor/gcp-deployment-plan-overview.md
frontend/my-app/src/components/ui/ApiToastListener.tsx
Design/frontend_state_refactor.md
docs/frontend/config/queryKeys.md
docs/frontend/features/landing/components/ConceptHeader.md
Design/how-to-implement-rls.md
docs/backend/models/export/request.md
[error] frontend/my-app/src/hooks/**tests**/useTaskSubscription.test.ts: SyntaxError: '>' expected. (81:28)
[error] 79 | const createWrapper = () => {
[error] 80 | return ({ children }: { children: React.ReactNode }) => (
[error] > 81 | <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
[error] | ^
[error] 82 | );
[error] 83 | };
[error] 84 |
Design/Refactoring-ExportOptions.md
docs/backend/api/routes/concept_storage/storage_routes.md
frontend/my-app/playwright-report/trace/uiMode.BatfzHMG.css
docs/backend/core/limiter/redis_store.md
frontend/my-app/src/api/task.ts
docs/backend/models/common/base.md
Design/frontend/shared_components.md
Design/data_cleanup_plan.md
frontend/my-app/src/components/ui/Card.tsx
frontend/my-app/src/features/refinement/components/RefinementHeader.tsx
docs/backend/utils/README.md
Design/frontend/old/ExportOptions.css
docs/frontend/config/README.md
Design/frontend/component_mockups/LightFooterComponent.tsx
docs/frontend/config/apiEndpoints.md
docs/backend/services/image/conversion.md
frontend/my-app/src/features/concepts/recent/components/RecentConceptsHeader.tsx
frontend/my-app/src/test-wrappers.tsx
frontend/my-app/playwright-report/trace/defaultSettingsView.5fN5lw10.css
docs/frontend/features/landing/components/ResultsSection.md
docs/frontend/components/ui/ApiToastListener.md
frontend/my-app/src/utils/stringUtils.ts
docs/frontend/contexts/TaskContext.md
Design/github_action_setup.md
docs/frontend/components/ui/OfflineStatus.md
docs/frontend/features/refinement/components/ComparisonView.md
docs/backend/services/jigsawstack/interface.md
Design/project_structure.md
docs/backend/core/middleware/README.md
docs/frontend/hooks/useTaskSubscription.md
Design/mobile_optimization.md
Design/rate-limit-state-refactor.md
frontend/my-app/src/hooks/**tests**/useTaskQueries.test.ts
docs/frontend/hooks/README.md
frontend/my-app/src/contexts/**tests**/AuthContext.test.tsx
TODO/service_refactor.md
frontend/my-app/src/components/index.ts
docs/backend/services/concept/palette.md
frontend/my-app/playwright-report/trace/assets/defaultSettingsView-DTenqiGw.js
frontend/my-app/src/features/concepts/recent/components/ConceptList.tsx
docs/frontend/components/ui/Card.md
docs/frontend/components/concept/ConceptForm.md
docs/backend/core/supabase/README.md
frontend/my-app/src/components/ui/**tests**/TextArea.test.tsx
frontend/my-app/accessibility.config.ts
frontend/my-app/src/components/ui/Input.tsx

eslint...................................................................Failed

- hook id: eslint
- exit code: 2

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Oops! Something went wrong! :(

ESLint: 9.25.0

ESLint couldn't find an eslint.config.(js|mjs|cjs) file.

From ESLint v9.0.0, the default configuration file is now eslint.config.js.
If you are using a .eslintrc.\* file, please follow the migration guide
to update your configuration file to the new format:

https://eslint.org/docs/latest/use/configure/migration-guide

If you still have problems after following the migration guide, please stop by
https://eslint.org/chat/help to chat with the team.

Check API routes for business logic......................................Passed
Check shared components for feature imports..........(no files to check)Skipped
TypeScript type checking.................................................Failed

- hook id: tsc
- exit code: 1

[41m [0m
[41m[37m This is not the tsc command you are looking for [0m
[41m [0m

To get access to the TypeScript compiler, [34mtsc[0m, from the command line either:

- Use [1mnpm install typescript[0m to first add TypeScript to your project [1mbefore[0m using npx
- Use [1myarn[0m to avoid accidentally running code from un-installed packages
