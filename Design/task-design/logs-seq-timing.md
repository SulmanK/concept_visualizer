[
{
"insertId": "686a04020008c60c47d6eac4",
"httpRequest": {
"requestMethod": "POST",
"requestUrl": "https://concept-viz-prod-worker-prod-4zbx6k5utq-ue.a.run.app/?__GCP_CloudEventsMode=CUSTOM_PUBSUB_projects%2Fconcept-visualizer-prod-2%2Ftopics%2Fconcept-viz-prod-tasks-prod",
"requestSize": "2008",
"status": 200,
"responseSize": "130",
"userAgent": "APIs-Google; (+https://developers.google.com/webmasters/APIs-Google.html)",
"remoteIp": "66.102.8.70",
"serverIp": "34.143.77.2",
"latency": "203.678286565s",
"protocol": "HTTP/1.1"
},
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:01:42.410213Z",
"severity": "INFO",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/cloud_event_source": "//pubsub.googleapis.com/projects/concept-visualizer-prod-2/topics/concept-viz-prod-tasks-prod",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/cloud_event_id": "15474464854558691",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Frequests",
"trace": "projects/concept-visualizer-prod-2/traces/d0ee2831588664d26b619cd3cbcca119",
"receiveTimestamp": "2025-07-06T05:05:06.581156755Z",
"spanId": "33c9bb1a23bd38f2",
"traceSampled": true
},
{
"textPayload": "/layers/google.python.pip/pip/lib/python3.11/site-packages/google/**init**.py:16: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using this package or pin to Setuptools<81.",
"insertId": "686a03370006cf90066a19f2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:43.446352Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:43.455430763Z"
},
{
"textPayload": " import pkg_resources",
"insertId": "686a03370006cfb3142270cc",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:43.446387Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:43.455430763Z"
},
{
"textPayload": "2025-07-06 05:01:48 [INFO] concept-worker-main: Logging configured at level: INFO",
"insertId": "686a033c00094d965dd02d32",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:48.609686Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:48.780670461Z"
},
{
"textPayload": "2025-07-06 05:01:48 [INFO] concept-worker-main: Initializing services globally for worker instance...",
"insertId": "686a033c00094da4bbd23c00",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:48.609700Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:48.780670461Z"
},
{
"textPayload": "2025-07-06 05:01:48 [INFO] concept-worker-main: Attempting service initialization (attempt 1/3)",
"insertId": "686a033c00094e03d843d5ed",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:01:48.609795Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:48.780670461Z"
},
{
"textPayload": "2025-07-06 05:01:48 [INFO] app.services.jigsawstack.client: Initialized JigsawStack client with API URL: https://api.jigsawstack.com",
"insertId": "686a033c000d9a2361f2ece2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:48.891427Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:48 [INFO] concept-worker-main: Global services initialized successfully on attempt 1",
"insertId": "686a033c000d9a9aded47ed2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:48.891546Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "Default STARTUP TCP probe succeeded after 1 attempt for container \"worker\" on port 8080.",
"insertId": "686a033c000e166e2ec73de4",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:48.923246Z",
"severity": "INFO",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fvarlog%2Fsystem",
"receiveTimestamp": "2025-07-06T05:01:48.929011619Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: === Cloud Function invoked: handle_pubsub ===",
"insertId": "686a033d00010e7ca2af2cff",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:49.069244Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: Starting async message processing",
"insertId": "686a033d00011919035c37d4",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:01:49.071961Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: Processing Pub/Sub message - Task ID: be2bbc22-f598-4db3-a906-0d45dd04dfea, Type: concept_generation",
"insertId": "686a033d00011a9d645a995e",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:49.072349Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: [TASK be2bbc22-f598-4db3-a906-0d45dd04dfea] Starting message processing - Type: concept_generation, User: 79f3130b-bb2a-4411-9f5e-27aa607040db",
"insertId": "686a033d00011aed8334ec6f",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:01:49.072429Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: [TASK be2bbc22-f598-4db3-a906-0d45dd04dfea] Validating task type: concept_generation",
"insertId": "686a033d00011b4499308813",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:01:49.072516Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: [TASK be2bbc22-f598-4db3-a906-0d45dd04dfea] Creating GenerationTaskProcessor",
"insertId": "686a033d00011b9ccf903d26",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:01:49.072604Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept-worker-main: [TASK be2bbc22-f598-4db3-a906-0d45dd04dfea] Starting processor execution",
"insertId": "686a033d00011cec0f5dc14a",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:49.072940Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] GenerationTaskProcessor: Processing generation task be2bbc22-f598-4db3-a906-0d45dd04dfea",
"insertId": "686a033d00011cf3776fb051",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:01:49.072947Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.112430427Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] httpx: HTTP Request: PATCH https://pstdcfittpjhxzynbdbu.supabase.co/rest/v1/tasks_prod?id=eq.be2bbc22-f598-4db3-a906-0d45dd04dfea&user_id=eq.79f3130b-bb2a-4411-9f5e-27aa607040db&status=eq.pending \"HTTP/2 200 OK\"",
"insertId": "686a033d0006b73d2508ba53",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:01:49.440125Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.451821481Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] task_service: Successfully claimed task be2b\***\*",
"insertId": "686a033d0006daaad8937a58",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:01:49.449194Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.779415848Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] GenerationTaskProcessor: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Claimed and marked as PROCESSING at 1751778109.45 (0.38s elapsed)",
"insertId": "686a033d0006dae6ff5a9d8e",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:49.449254Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.779415848Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] GenerationTaskProcessor: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Generating base concept",
"insertId": "686a033d0006db1b62708ace",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:49.449307Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.779415848Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] concept_service: Generating concept with logo_description='John Wick', theme_description='Sanguine'",
"insertId": "686a033d0006db8839ab710d",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:01:49.449416Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.779415848Z"
},
{
"textPayload": "2025-07-06 05:01:49 [INFO] app.services.jigsawstack.client: Generating image with prompt: John Wick",
"insertId": "686a033d0006dc3389e8ea49",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:01:49.449587Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:01:49.779415848Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] httpx: HTTP Request: POST https://api.jigsawstack.com/v1/ai/image_generation \"HTTP/1.1 200 OK\"",
"insertId": "686a03490003450c4f95a6cb",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:01.214284Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] app.services.jigsawstack.client: Image generation successful (binary response)",
"insertId": "686a034900047432de31d16b",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:01.291890Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Image generated successfully: file:///tmp/temp_image_d8f22f8d-adda-4343-ad8d-65151f1f088e.png",
"insertId": "686a0349000484454aa78be1",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:01.296005Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Downloading image from URL: file:///tmp/temp_image_d8f22f8d-adda-4343-ad8d-65151f1f088e.png",
"insertId": "686a034900048458a215bee2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:01.296024Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Read image data from local file",
"insertId": "686a034900048a3c97332a47",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:01.297532Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Removed temporary file: /tmp/temp_image_d8f22f8d-adda-4343-ad8d-65151f1f088e.png",
"insertId": "686a034900048a996f6d5bdc",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:01.297625Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Successfully downloaded image, size: 813377 bytes",
"insertId": "686a034900048b61f7c9b583",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:01.297825Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] GenerationTaskProcessor: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Base concept generated at 1751778121.30 (Duration: 11.85s)",
"insertId": "686a034900048ba7a12154ed",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:01.297895Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] image_preparer: Using image data from concept service response, size: 813377 bytes",
"insertId": "686a034900048c250753a679",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:01.298021Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] GenerationTaskProcessor: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Starting concurrent base image storage and palette generation",
"insertId": "686a034900048c531c4c4d78",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:01.298067Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] image_storage: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Storing base image, size: 813377 bytes",
"insertId": "686a034900048db886e1aaf3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:01.298424Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.436421815Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] palette_generator: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Generating 7 color palettes",
"insertId": "686a0349000770d072dd5225",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:01.487632Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.772992398Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service: Generating 7 color palettes for: Sanguine",
"insertId": "686a0349000770e2aac5b003",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:01.487650Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.772992398Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] concept_service.palette: Generating 7 color palettes for: Sanguine",
"insertId": "686a0349000770e960e4d429",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:01.487657Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.772992398Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] app.services.jigsawstack.client: Generating 7 color palettes based on logo and theme descriptions",
"insertId": "686a03490007714bfc6469f3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:01.487755Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.772992398Z"
},
{
"textPayload": "2025-07-06 05:02:01 [INFO] app.services.jigsawstack.client: Sending request to prompt engine with combined logo and theme description",
"insertId": "686a03490007718925d4a47b",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:01.487817Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:01.772992398Z"
},
{
"textPayload": "2025-07-06 05:02:02 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/concept-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/20250706050201_bc52d0d4.png \"HTTP/1.1 200 OK\"",
"insertId": "686a034a0001ec0ee6f6e008",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:02.125966Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:02 [INFO] supabase_image: Uploaded image for user 79f3\*\*** at 79f3\***\*/20250706050201_bc52d0d4.png",
"insertId": "686a034a0001f316a9b9a7b0",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:02.127766Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:02 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a034a00051c86df6a5dbe",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:02.334982Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:02 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\***\*/20250706050201_bc52d0d4.png with 2678400s expiry",
"insertId": "686a034a00051f342a402d32",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:02.335668Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:02 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/20250706050201_bc52d0d4.png",
"insertId": "686a034a00051f3f0b4ddc30",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:02.335679Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:02 [INFO] image_storage: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Base image stored at 1751778122.34 (Duration: 1.04s)",
"insertId": "686a034a00051f47a955f954",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:02.335687Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:02.438071616Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] httpx: HTTP Request: POST https://api.jigsawstack.com/v1/prompt_engine/run \"HTTP/1.1 200 OK\"",
"insertId": "686a034f0007a4ec909ad2b9",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:07.500972Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.jigsawstack.client: Response status code: 200",
"insertId": "686a034f0007ad105d815456",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:07.503056Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.jigsawstack.client: Raw API response structure: ['success', 'result', 'message', '_usage']",
"insertId": "686a034f0007aeb64eed0b40",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:07.503478Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] concept_service.palette: Successfully generated 7 palettes",
"insertId": "686a034f0007aef55676b291",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:07.503541Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] palette_generator: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Color palettes generated at 1751778127.50 (Duration: 6.02s)",
"insertId": "686a034f0007af62597054dc",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:07.503650Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] palette_generator: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Generated 7 color palettes",
"insertId": "686a034f0007af8d4a266940",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:07.503693Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] GenerationTaskProcessor: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Concurrent image store & palette generation finished at 1751778127.50 (Duration: 6.21s)",
"insertId": "686a034f0007b0395c00f97a",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:07.503865Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] GenerationTaskProcessor: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Base image stored at path: 79f3130b-bb2a-4411-9f5e-27aa607040db/20250706050201_bc52d0d4.png",
"insertId": "686a034f0007b060741c8d17",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:07.503904Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] variation_creator: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Creating 7 palette variations",
"insertId": "686a034f0007b119171f44c2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:07.504089Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.image.service: Creating 7 palette variations for user: 79f3\***\*",
"insertId": "686a034f0007b14727da10c9",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:07.504135Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:07.764268102Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.image.service: Successfully validated base image for processing, size: 529012 bytes",
"insertId": "686a034f000daf86af76cfd9",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:07.896902Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:08.099184656Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.image.service: Using concurrency limit of 1 for palette variation processing",
"insertId": "686a034f000dafe0b22bf89c",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:07.896992Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:08.099184656Z"
},
{
"textPayload": "2025-07-06 05:02:07 [INFO] app.services.image.service: Starting controlled parallel processing of 7 palette variations (max 1 concurrent)",
"insertId": "686a034f000db02ef76f9ae8",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:02:07.897070Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:08.099184656Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=28.471",
"insertId": "686a036c0005a0f9cb0fcaf4",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:36.368889Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:36.375711982Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_73411bc2-d87c-45c5-8a32-b75a143763dd.png \"HTTP/1.1 200 OK\"",
"insertId": "686a036c000c119e7620b1d5",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:02:36.790942Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] supabase_image: Uploaded image for user 79f3\*\*** at 79f3\***\*/palette_20250706050207_73411bc2-d87c-45c5-8a32-b75a143763dd.png",
"insertId": "686a036c000c153662a9f628",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:36.791862Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:02:36 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a036c000d721262d9f176",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:02:36.881170Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_73411bc2-d87c-45c5-8a32-b75a143763dd.png with 2678400s expiry",
"insertId": "686a036c000d7225b6898b8c",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:36.881189Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_73411bc2-d87c-45c5-8a32-b75a143763dd.png",
"insertId": "686a036c000d736a9a729447",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:36.881514Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:02:36 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.513",
"insertId": "686a036c000d7376b18b7243",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:02:36.881526Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:02:37.039757901Z"
},
{
"textPayload": "2025-07-06 05:03:02 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=25.741",
"insertId": "686a03860009826c0c771368",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:02.623212Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:02.627235946Z"
},
{
"textPayload": "2025-07-06 05:03:02 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_9d24f831-776b-464a-ad68-6affa19f4237.png \"HTTP/1.1 200 OK\"",
"insertId": "686a0386000e821673cbff36",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:03:02.950806Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:02.960488836Z"
},
{
"textPayload": "2025-07-06 05:03:02 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_9d24f831-776b-464a-ad68-6affa19f4237.png",
"insertId": "686a0386000e851df9463d19",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:02.951581Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:02.960488836Z"
},
{
"textPayload": "2025-07-06 05:03:03 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a0387000102611db18e06",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:03.066145Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:03.293654073Z"
},
{
"textPayload": "2025-07-06 05:03:03 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_9d24f831-776b-464a-ad68-6affa19f4237.png with 2678400s expiry",
"insertId": "686a03870001027f5ce59ce8",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:03:03.066175Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:03.293654073Z"
},
{
"textPayload": "2025-07-06 05:03:03 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_9d24f831-776b-464a-ad68-6affa19f4237.png",
"insertId": "686a038700010409dee275f3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:03:03.066569Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:03.293654073Z"
},
{
"textPayload": "2025-07-06 05:03:03 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.443",
"insertId": "686a0387000104104d899c67",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:03.066576Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:03.293654073Z"
},
{
"textPayload": "2025-07-06 05:03:26 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=23.497",
"insertId": "686a039e00089972d2fad9ea",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:03:26.563570Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:26.569027973Z"
},
{
"textPayload": "2025-07-06 05:03:26 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_cf3b885e-8457-431d-82dc-a323e20d0c16.png \"HTTP/1.1 200 OK\"",
"insertId": "686a039e000d6c289faca68a",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:03:26.879656Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:26.902409926Z"
},
{
"textPayload": "2025-07-06 05:03:26 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_cf3b885e-8457-431d-82dc-a323e20d0c16.png",
"insertId": "686a039e000d6f82562bd5e7",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:03:26.880514Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:26.902409926Z"
},
{
"textPayload": "2025-07-06 05:03:27 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a039f0000026615ee8fa2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:27.000614Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:27.236836467Z"
},
{
"textPayload": "2025-07-06 05:03:27 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_cf3b885e-8457-431d-82dc-a323e20d0c16.png with 2678400s expiry",
"insertId": "686a039f0000028501667e05",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:03:27.000645Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:27.236836467Z"
},
{
"textPayload": "2025-07-06 05:03:27 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_cf3b885e-8457-431d-82dc-a323e20d0c16.png",
"insertId": "686a039f000003b9c8435eac",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:03:27.000953Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:27.236836467Z"
},
{
"textPayload": "2025-07-06 05:03:27 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.437",
"insertId": "686a039f0000048e8f119c9f",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:27.001166Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:27.236836467Z"
},
{
"textPayload": "2025-07-06 05:03:50 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=23.681",
"insertId": "686a03b6000a6b3046e744b3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:03:50.682800Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:50.685129357Z"
},
{
"textPayload": "2025-07-06 05:03:51 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_a1ce8d6c-aa10-49c8-8eb9-9e9dc77bc21b.png \"HTTP/1.1 200 OK\"",
"insertId": "686a03b700014c79b4a21e7f",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:51.085113Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:03:51 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_a1ce8d6c-aa10-49c8-8eb9-9e9dc77bc21b.png",
"insertId": "686a03b700014f71c5a77cfc",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:03:51.085873Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:03:51 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a03b7000316c4296511a3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:03:51.202436Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:03:51 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_a1ce8d6c-aa10-49c8-8eb9-9e9dc77bc21b.png with 2678400s expiry",
"insertId": "686a03b7000316e9a5280c48",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:51.202473Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:03:51 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_a1ce8d6c-aa10-49c8-8eb9-9e9dc77bc21b.png",
"insertId": "686a03b70003186a0db47ae8",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:03:51.202858Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:03:51 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.520",
"insertId": "686a03b7000318aea32d8788",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:03:51.202926Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:03:51.355086537Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=25.998",
"insertId": "686a03d1000310b951caf577",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:04:17.200889Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.204702680Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_de366d20-2396-4a7a-83f1-a445c5e9a86f.png \"HTTP/1.1 200 OK\"",
"insertId": "686a03d1000951c44fb6f27e",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:17.610756Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_de366d20-2396-4a7a-83f1-a445c5e9a86f.png",
"insertId": "686a03d1000955a3e7297486",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:04:17.611747Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:17 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a03d1000af07224f6c682",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:17.716914Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_de366d20-2396-4a7a-83f1-a445c5e9a86f.png with 2678400s expiry",
"insertId": "686a03d1000af07f786e2996",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:17.716927Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_de366d20-2396-4a7a-83f1-a445c5e9a86f.png",
"insertId": "686a03d1000af1f0db8b9668",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:04:17.717296Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:17 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.517",
"insertId": "686a03d1000af21f7ac132a8",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:17.717343Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:17.871830182Z"
},
{
"textPayload": "2025-07-06 05:04:43 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=26.228",
"insertId": "686a03eb000e6be0c7526e6c",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:04:43.945120Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:43.950502487Z"
},
{
"textPayload": "2025-07-06 05:04:44 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_1e6927b3-fc3e-44d4-95ec-c6054ab6e94f.png \"HTTP/1.1 200 OK\"",
"insertId": "686a03ec0004cddb574b56e3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:04:44.314843Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:04:44 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_1e6927b3-fc3e-44d4-95ec-c6054ab6e94f.png",
"insertId": "686a03ec0004d0b863d2a239",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:44.315576Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:04:44 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a03ec0006995da69d5893",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:04:44.432477Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:04:44 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_1e6927b3-fc3e-44d4-95ec-c6054ab6e94f.png with 2678400s expiry",
"insertId": "686a03ec0006996e6ea6da36",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:04:44.432494Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:04:44 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_1e6927b3-fc3e-44d4-95ec-c6054ab6e94f.png",
"insertId": "686a03ec00069ab56c84c6de",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:04:44.432821Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:04:44 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.488",
"insertId": "686a03ec00069af87eac58f2",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:04:44.432888Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:04:44.615951269Z"
},
{
"textPayload": "2025-07-06 05:05:05 [INFO] app.services.image.service: TIMING_PROCESS_PALETTE sec=21.291",
"insertId": "686a0401000b0be4f4b0d538",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:05.723940Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:05.728927427Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] httpx: HTTP Request: POST https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/palette-images-prod/79f3130b-bb2a-4411-9f5e-27aa607040db/palette_20250706050207_74cf42e2-286c-4bf5-93c6-ba907fd681d0.png \"HTTP/1.1 200 OK\"",
"insertId": "686a04020000f7ea7083ce3a",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:05:06.063466Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_image: Uploaded image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_74cf42e2-286c-4bf5-93c6-ba907fd681d0.png",
"insertId": "686a04020000fb61a736e330",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.064353Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [WARNING] supabase_image: Missing /storage/v1/ in signed URL from Supabase, adding it manually",
"insertId": "686a04020002961c75fc8df3",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:05:06.169500Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_image: Generated signed URL for 79f3**\*\*\*\***/palette_20250706050207_74cf42e2-286c-4bf5-93c6-ba907fd681d0.png with 2678400s expiry",
"insertId": "686a0402000296342319d877",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.169524Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] app.services.persistence.image_persistence_service: Stored image for user 79f3\***\* at 79f3\*\***/palette_20250706050207_74cf42e2-286c-4bf5-93c6-ba907fd681d0.png",
"insertId": "686a0402000297942ab4c1bf",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.169876Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] app.services.image.service: TIMING_UPLOAD sec=0.446",
"insertId": "686a0402000297cf1a17feaf",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.169935Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] app.services.image.service: Successfully created 7 of 7 palette variations in 178.67 seconds (avg 25.52 seconds per variation)",
"insertId": "686a04020002989ac1fb9443",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:05:06.170138Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] variation_creator: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Created 7 palette variations at 1751778306.17 (Duration: 178.67s)",
"insertId": "686a040200029bf844d65d61",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.171Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_storage: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Storing concept data with 7 palette variations",
"insertId": "686a040200029c309753a497",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:05:06.171056Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_persistence_service: Storing concept for user: 79f3\***\*",
"insertId": "686a040200029c8ac7ed27c8",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.171146Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_concept: Attempting to store concept with service role key for user: 79f3\*\***, path: 79f3\***\*/20250706050201_bc52d0d4.png",
"insertId": "686a040200029cdefe3f12bf",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.171230Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_concept: Successfully stored concept with service role key: 201",
"insertId": "686a0402000415e247896e71",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.267746Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_persistence_service: Stored concept with ID: dec1\*\***",
"insertId": "686a0402000416dd5ef694ed",
"resource": {
"type": "cloud_run_revision",
"labels": {
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.267997Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_concept: Attempting to store 7 color variations with service role key",
"insertId": "686a04020004177a03158d83",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:05:06.268154Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] supabase_concept: Successfully stored 7 color variations with service role key",
"insertId": "686a04020005a16b6a99b09f",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.369003Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_persistence_service: Stored 7 color variations",
"insertId": "686a04020005a28b9ec2e50f",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"service_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"location": "us-east1"
}
},
"timestamp": "2025-07-06T05:05:06.369291Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_storage: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Stored concept with ID: dec1e601-2c77-4baf-9cd7-7e50b604d0be",
"insertId": "686a04020005a2cb602b6f25",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.369355Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept_storage: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Concept data stored at 1751778306.37 (Duration: 0.20s)",
"insertId": "686a04020005a2fddd837526",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.369405Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] GenerationTaskProcessor: [WORKER_TIMING] Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Completed successfully at 1751778306.37 (Total Duration: 197.30s)",
"insertId": "686a04020005a34f1523537a",
"resource": {
"type": "cloud_run_revision",
"labels": {
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.369487Z",
"labels": {
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.394606454Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] httpx: HTTP Request: PATCH https://pstdcfittpjhxzynbdbu.supabase.co/rest/v1/tasks_prod?id=eq.be2bbc22-f598-4db3-a906-0d45dd04dfea \"HTTP/2 200 OK\"",
"insertId": "686a040200088d8557d80d35",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"project_id": "concept-visualizer-prod-2",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.560517Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-drz-cloudfunctions-location": "us-east1",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] task_service: Successfully updated task be2b\*\*\*\* status to 'completed'",
"insertId": "686a04020008995c05350ff0",
"resource": {
"type": "cloud_run_revision",
"labels": {
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.563548Z",
"labels": {
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"goog-drz-cloudfunctions-location": "us-east1",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] GenerationTaskProcessor: Task be2bbc22-f598-4db3-a906-0d45dd04dfea: Completed successfully with result dec1e601-2c77-4baf-9cd7-7e50b604d0be",
"insertId": "686a04020008996754958950",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.563559Z",
"labels": {
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept-worker-main: [TASK be2bbc22-f598-4db3-a906-0d45dd04dfea] Processor completed successfully",
"insertId": "686a0402000899d0abfc837d",
"resource": {
"type": "cloud_run_revision",
"labels": {
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"project_id": "concept-visualizer-prod-2"
}
},
"timestamp": "2025-07-06T05:05:06.563664Z",
"labels": {
"goog-managed-by": "cloudfunctions",
"goog-drz-cloudfunctions-location": "us-east1",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept-worker-main: Successfully completed processing for task be2bbc22-f598-4db3-a906-0d45dd04dfea",
"insertId": "686a0402000899e199b1b911",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"revision_name": "concept-viz-prod-worker-prod-00004-wan",
"location": "us-east1",
"configuration_name": "concept-viz-prod-worker-prod",
"service_name": "concept-viz-prod-worker-prod"
}
},
"timestamp": "2025-07-06T05:05:06.563681Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"goog-managed-by": "cloudfunctions",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
},
{
"textPayload": "2025-07-06 05:05:06 [INFO] concept-worker-main: === Cloud Function completed successfully ===",
"insertId": "686a04020008a64c1b00382c",
"resource": {
"type": "cloud_run_revision",
"labels": {
"project_id": "concept-visualizer-prod-2",
"service_name": "concept-viz-prod-worker-prod",
"configuration_name": "concept-viz-prod-worker-prod",
"location": "us-east1",
"revision_name": "concept-viz-prod-worker-prod-00004-wan"
}
},
"timestamp": "2025-07-06T05:05:06.566860Z",
"labels": {
"goog-drz-cloudfunctions-location": "us-east1",
"goog-drz-cloudfunctions-id": "concept-viz-prod-worker-prod",
"instanceId": "0069c7a988ea8178d45168747425623410990947f023483b722c2966269947f2fd518568c635ff2ae601869e2274f93ce9e53e3c50d365978043dfc9c808323247928b49cc50ec539b5f5015cd32",
"run.googleapis.com/base_image_versions": "us-docker.pkg.dev/serverless-runtimes/google-22-full/runtimes/python311:python311_20250630_3_11_13_RC00",
"goog-managed-by": "cloudfunctions"
},
"logName": "projects/concept-visualizer-prod-2/logs/run.googleapis.com%2Fstderr",
"receiveTimestamp": "2025-07-06T05:05:06.727526527Z"
}
]
