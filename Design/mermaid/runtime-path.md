%%{init:{
'theme':'default',
'flowchart':{ 'htmlLabels':true, 'nodeSpacing':100, 'rankSpacing':60 },
'securityLevel':'loose',
'themeCSS':'.label, .node text, .edgeLabel tspan{font-size:50px !important;}.cluster-label'
'themeCSS':'.cluster-label text{font-size:50px !important;}'
}}%%

graph LR

%% ─────────── Client ───────────
User["👤 User (Browser)"]

%% ─────────── Front-end (Vercel) ───────────
subgraph FE["<span style='font-size:18px;font-weight:bold;'>Frontend<br/>(Vercel)</span>"]
direction TB
FrontendApp["⚛️ Frontend Application<br/>(React, Vite)"]
end

%% ─────────── Backend (Google Cloud) ───────────
subgraph GCP["<span style='font-size:18px;font-weight:bold;'>Backend Platform<br/>(Google Cloud)</span>"]
direction TB
APIVM["<img src='https://k21academy.com/wp-content/uploads/2021/01/Google_Compute_Engine-Logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> API Server (FastAPI on Compute Engine MIG)"]
PubSub["<img src='https://iconape.com/wp-content/files/jg/62017/png/google-cloud-pub-sub-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCP Pub/Sub (Task Queue)"]
WorkerCF["<img src='https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_87f5b15be060087098cc881c06279eac/google-cloud-functions.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Worker (Cloud Function Gen 2)"]
SecretManager["<img src='https://cdn-images-1.medium.com/v2/resize:fit:480/0*eT9wK2hiaOnGLGI9' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Secret Manager"]
GCSAssets["<img src='https://k21academy.com/wp-content/uploads/2021/02/Google-Cloud-Storage-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCS Bucket (Assets/Scripts)"]
CloudMonitoring["<img src='https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_64f2fd5c445a1d358eb2327ac4b2b501/google-cloud-monitoring.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Cloud Monitoring"]
end

%% (put this inside the Runtime diagram, replacing the previous Supabase block)
subgraph External["<span style='font-size:18px;font-weight:bold;'>External Services</span>"]
direction TB

%% ── Supabase cluster with padding ──
%% Two invisible spacer-nodes add ~1 line of top/bottom padding.
classDef blank fill:transparent,stroke:none;

subgraph SB["<img src='https://companieslogo.com/img/orig/supabase-554aca1c.png?t=1701239800' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Supabase"]
direction LR
SBPadTop[" "]:::blank
SupabaseDB["🐘 DB"]
SupabaseAuth["🔑 Auth"]
SupabaseStorage["📦 Storage"]
SBPadBot[" "]:::blank
end

SupabaseEdgeFunc["⚡ Edge Function (Cleanup)"]
UpstashRedis["<img src='https://upstash.com/logo/upstash-icon-white-bg.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Upstash&nbsp;Redis<br/>(Rate&nbsp;Limiting)"]
JigsawStack["<img src='https://pipedream.com/s.v0/app_Z2hx0z/logo/orig' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> JigsawStack&nbsp;API<br/>(AI&nbsp;Generation)"]
end

%% ─────────── Alerts ───────────
EmailAlerts["📧 Email Alerts"]

%% ─── Flows ───
User -- "HTTPS" --> FrontendApp

    %% Front-end → Back-end / Supabase
    FrontendApp   -- "API Calls"        --> APIVM
    FrontendApp   -- "Auth"             --> SupabaseAuth
    FrontendApp   -- "RLS Storage"      --> SupabaseStorage

    %% API Server interactions
    APIVM         -- "DB Queries"       --> SupabaseDB
    APIVM         -- "Auth Validate"    --> SupabaseAuth
    APIVM         -- "Publish Task"     --> PubSub
    APIVM         -- "Secrets"          --> SecretManager
    APIVM         -- "Rate-limit"       --> UpstashRedis
    APIVM         -- "Metrics"          --> CloudMonitoring

    %% Pub/Sub → Worker
    PubSub        -- "Trigger"          --> WorkerCF

    %% Worker interactions
    WorkerCF      -- "DB Ops"           --> SupabaseDB
    WorkerCF      -- "Read/Write"       --> SupabaseStorage
    WorkerCF      -- "AI Call"          --> JigsawStack
    WorkerCF      -- "Secrets"          --> SecretManager
    WorkerCF      -- "Metrics"          --> CloudMonitoring

    %% Monitoring
    CloudMonitoring -- "Alerts"         --> EmailAlerts

%% ─────────── Styling ───────────
classDef default fill:#fff,stroke:#333,stroke-width:2px;
classDef gcp fill:#e3f2fd,stroke:#4285f4,stroke-width:2px,color:#333;
classDef vercel fill:#f0f0f0,stroke:#000,stroke-width:2px,color:#333;
classDef external fill:#e8f5e9,stroke:#34a853,stroke-width:2px,color:#333;

    class User,FrontendApp vercel;
    class APIVM,PubSub,WorkerCF,SecretManager,GCSAssets,CloudMonitoring gcp;
    class SupabaseDB,SupabaseAuth,SupabaseStorage,SupabaseEdgeFunc,UpstashRedis,JigsawStack external;
