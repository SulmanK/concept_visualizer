%%{init: {
'theme': 'default',
'flowchart': { 'htmlLabels': true },
'securityLevel': 'loose',
'themeCSS': '.label, .node text, .edgeLabel, .edgeLabel tspan { font-size: 50px !important; }'
'themeCSS': '.cluster-label, .cluster-label text { font-size: 50px !important; }'
}}%%

graph TD
%% -------- User & Client Tier --------
User["👤 User (Browser)"]

    %% -------- Frontend Tier (Vercel) --------
    subgraph DevOps["<span style='font-size:18px;font-weight:bold;'>DevOps &amp; Orchestration</span>"]
        FrontendApp["⚛️ Frontend Application (React, Vite)"]
    end

    %% -------- Backend Tier (Google Cloud Platform) --------
    subgraph GCP["<span style='font-size:18px;font-weight:bold;'>Backend Platform (Google Cloud Platform)</span>"]
        APIVM["<img src='https://k21academy.com/wp-content/uploads/2021/01/Google_Compute_Engine-Logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> API Server (FastAPI on Compute Engine MIG)"]
        PubSub["<img src='https://iconape.com/wp-content/files/jg/62017/png/google-cloud-pub-sub-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCP Pub/Sub (Task Queue)"]
        WorkerCF["<img src='https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_87f5b15be060087098cc881c06279eac/google-cloud-functions.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Worker (Cloud Function Gen 2)"]
        ArtifactRegistry["<img src='https://sysdig.com/wp-content/uploads/logo-google-cloud-artifact-registry.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Artifact Registry (Docker Images)"]
        SecretManager["<img src='https://cdn-images-1.medium.com/v2/resize:fit:480/0*eT9wK2hiaOnGLGI9' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Secret Manager"]
        GCSAssets["<img src='https://k21academy.com/wp-content/uploads/2021/02/Google-Cloud-Storage-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCS Bucket (Assets/Scripts)"]
        CloudMonitoring["<img src='https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_64f2fd5c445a1d358eb2327ac4b2b501/google-cloud-monitoring.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Cloud Monitoring"]
        GCPState["🌐 GCP Resources"]
    end

    %% -------- External Services --------
    subgraph External["<span style='font-size:18px;font-weight:bold;'>External Services</span>"]
        Supabase["<img src='https://companieslogo.com/img/orig/supabase-554aca1c.png?t=1701239800' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Supabase"]
        SupabaseDB["🐘 PostgreSQL DB"]
        SupabaseAuth["🔑 Auth"]
        SupabaseStorage["📦 Storage (Concepts, Palettes)"]
        SupabaseEdgeFunc["⚡ Edge Function (Cleanup)"]
        JigsawStack["<img src='https://pipedream.com/s.v0/app_Z2hx0z/logo/orig' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> JigsawStack API (AI Generation)"]
        UpstashRedis["<img src='https://upstash.com/logo/upstash-icon-white-bg.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Upstash Redis (Rate Limiting)"]
    end

    %% -------- CI/CD & IaC --------
    subgraph DevOps["<span style='font-size:18px;font-weight:bold;'>DevOps &amp; Orchestration</span>"]
        GitHubActions["<img src='https://static.vecteezy.com/system/resources/previews/024/555/259/original/github-logo-transparent-free-png.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GitHub Actions (CI/CD)"]
        Terraform["<img src='https://opensenselabs.com/sites/default/files/inline-images/terraform.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Terraform (IaC)"]
        GCSState["<img src='https://k21academy.com/wp-content/uploads/2021/02/Google-Cloud-Storage-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCS Bucket (Terraform State)"]
        TerraformOutputs["📝 Terraform Outputs"]
        GitHubSecrets["🔒 GitHub Secrets"]
    end

    %% -------- Connections --------

    %% User to Frontend
    User -- "HTTPS" --> FrontendApp

    %% Frontend to Backend & Supabase
    FrontendApp -- "API Calls (proxied)" --> APIVM
    FrontendApp -- "Auth Calls" --> SupabaseAuth
    FrontendApp -- "Direct Storage (RLS)" --> SupabaseStorage

    %% API Server Interactions
    APIVM -- "DB Queries/Mutations" --> SupabaseDB
    APIVM -- "Auth Validation" --> SupabaseAuth
    APIVM -- "Publish Tasks" --> PubSub
    APIVM -- "Access Secrets" --> SecretManager
    APIVM -- "Rate Limit Checks" --> UpstashRedis
    APIVM -- "Logs & Metrics" --> CloudMonitoring

    %% Worker Interactions
    PubSub -- "Trigger" --> WorkerCF
    WorkerCF -- "DB Ops" --> SupabaseDB
    WorkerCF -- "Read/Write Images" --> SupabaseStorage
    WorkerCF -- "AI Calls" --> JigsawStack
    WorkerCF -- "Access Secrets" --> SecretManager
    WorkerCF -- "Logs & Metrics" --> CloudMonitoring

    %% Supabase Internal
    Supabase --> SupabaseDB
    Supabase --> SupabaseAuth
    Supabase --> SupabaseStorage
    Supabase --> SupabaseEdgeFunc

    %% CI/CD & IaC
    GitHubActions -- "Push Images" --> ArtifactRegistry
    GitHubActions -- "Deploy Infrastructure (Terraform)" --> GCPState
    GitHubActions -- "Deploy Frontend" --> FrontendApp
    GitHubActions -- "Cron Triggers" --> SupabaseEdgeFunc
    GitHubActions -- "Read Outputs" --> TerraformOutputs
    TerraformOutputs -- "Populate" --> GitHubSecrets

    Terraform -- "Manages" --> GCPState
    Terraform -- "Stores State" --> GCSState

    %% Infra topology
    GCPState -.- APIVM
    GCPState -.- WorkerCF
    GCPState -.- PubSub
    GCPState -.- ArtifactRegistry
    GCPState -.- SecretManager
    GCPState -.- GCSAssets
    GCPState -.- CloudMonitoring

    %% Monitoring
    CloudMonitoring -- "Email Alerts" --> EmailAlerts["📧 Email Alerts"]

    %% Style Definitions
    classDef default fill:#fff,stroke:#333,stroke-width:2px;
    classDef gcp fill:#e3f2fd,stroke:#4285f4,stroke-width:2px,color:#333;
    classDef vercel fill:#f0f0f0,stroke:#000,stroke-width:2px,color:#333;
    classDef external fill:#e8f5e9,stroke:#34a853,stroke-width:2px,color:#333;
    classDef devops fill:#fff3e0,stroke:#fbbc05,stroke-width:2px,color:#333;

    class User,FrontendApp vercel;
    class APIVM,PubSub,WorkerCF,ArtifactRegistry,SecretManager,GCSAssets,CloudMonitoring,GCPState gcp;
    class Supabase,SupabaseDB,SupabaseAuth,SupabaseStorage,SupabaseEdgeFunc,JigsawStack,UpstashRedis external;
    class GitHubActions,Terraform,GCSState,TerraformOutputs,GitHubSecrets devops;
