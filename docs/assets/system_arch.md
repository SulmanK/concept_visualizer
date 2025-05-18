## System Architecture Diagram

```mermaid
graph TD
    %% -------- User & Client Tier --------
    User["👤 User (Browser)"]

    %% -------- Frontend Tier (Vercel) --------
    subgraph Frontend Platform (Vercel)
        FrontendApp["⚛️ Frontend Application (React, Vite)"]
    end

    %% -------- Backend Tier (GCP) --------
    subgraph Backend Platform (Google Cloud Platform)
        APIVM["💻 API Server (FastAPI on Compute Engine MIG)"]
        PubSub["<img src='https://www.gstatic.com/images/branding/product/2x/pubsub_48dp.png' width='20' alt='Pub/Sub icon' /> GCP Pub/Sub (Task Queue)"]
        WorkerCF["<img src='https://www.gstatic.com/images/branding/product/2x/functions_48dp.png' width='20' alt='Cloud Functions icon' /> Worker (Cloud Function Gen 2)"]
        ArtifactRegistry["<img src='https://www.gstatic.com/images/branding/product/2x/artifact_registry_48dp.png' width='20' alt='Artifact Registry icon' /> Artifact Registry (Docker Images)"]
        SecretManager["<img src='https://www.gstatic.com/images/branding/product/2x/secret_manager_48dp.png' width='20' alt='Secret Manager icon' /> Secret Manager"]
        GCSAssets["<img src='https://www.gstatic.com/images/branding/product/2x/storage_48dp.png' width='20' alt='GCS icon' /> GCS Bucket (Assets/Scripts)"]
        CloudMonitoring["<img src='https://www.gstatic.com/images/branding/product/2x/monitoring_48dp.png' width='20' alt='Cloud Monitoring icon' /> Cloud Monitoring"]
    end

    %% -------- External Services --------
    subgraph External Services
        Supabase["<img src='https://seeklogo.com/images/S/supabase-logo-DCC676FFE2-seeklogo.com.png' width='20' alt='Supabase icon' /> Supabase"]
        SupabaseDB["  🐘 PostgreSQL DB"]
        SupabaseAuth["  🔑 Auth"]
        SupabaseStorage["  📦 Storage (Concepts, Palettes)"]
        SupabaseEdgeFunc["  ⚡ Edge Function (Cleanup)"]
        JigsawStack["<img src='https://jigsawstack.com/favicon.ico' width='20' alt='JigsawStack icon' /> JigsawStack API (AI Generation)"]
        UpstashRedis["<img src='https://avatars.githubusercontent.com/u/76460935?s=200&v=4' width='20' alt='Upstash icon' /> Upstash Redis (Rate Limiting)"]
    end

    %% -------- CI/CD & IaC --------
    subgraph DevOps & Orchestration
        GitHubActions["<img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' width='20' alt='GitHub icon' /> GitHub Actions (CI/CD)"]
        Terraform["<img src='https://www.terraform.io/img/L_దాసు-40x40.svg' width='20' alt='Terraform icon' /> Terraform (IaC)"]
        GCSState["<img src='https://www.gstatic.com/images/branding/product/2x/storage_48dp.png' width='20' alt='GCS icon' /> GCS Bucket (Terraform State)"]
    end

    %% -------- Connections --------

    User -- "HTTPS" --> FrontendApp

    FrontendApp -- "API Calls (Proxied via Vercel Rewrites)" --> APIVM
    FrontendApp -- "Auth Calls" --> SupabaseAuth
    FrontendApp -- "Direct Storage (Optional, RLS)" --> SupabaseStorage

    APIVM -- "DB Queries/Mutations" --> SupabaseDB
    APIVM -- "Auth Validation" --> SupabaseAuth
    APIVM -- "Publish Tasks" --> PubSub
    APIVM -- "Access Secrets" --> SecretManager
    APIVM -- "Rate Limit Checks" --> UpstashRedis
    APIVM -- "Logs/Metrics" --> CloudMonitoring

    PubSub -- "Trigger (Task Message)" --> WorkerCF
    WorkerCF -- "DB Queries/Mutations" --> SupabaseDB
    WorkerCF -- "Read/Write Images" --> SupabaseStorage
    WorkerCF -- "AI Calls" --> JigsawStack
    WorkerCF -- "Access Secrets" --> SecretManager
    WorkerCF -- "Logs/Metrics" --> CloudMonitoring

    Supabase --> SupabaseDB
    Supabase --> SupabaseAuth
    Supabase --> SupabaseStorage
    Supabase --> SupabaseEdgeFunc

    GitHubActions -- "Build & Test" --> User
    GitHubActions -- "Push Images" --> ArtifactRegistry
    GitHubActions -- "Deploy Infrastructure (via Terraform)" --> GCPState["GCP Resources"]
    GCPState -.- APIVM
    GCPState -.- WorkerCF
    GCPState -.- PubSub
    GCPState -.- ArtifactRegistry
    GCPState -.- SecretManager
    GCPState -.- GCSAssets
    GCPState -.- CloudMonitoring
    GitHubActions -- "Deploy Frontend" --> FrontendApp
    GitHubActions -- "Triggers (e.g. cron)" --> SupabaseEdgeFunc
    GitHubActions -- "Reads" --> TerraformOutputs["Terraform Outputs"]
    TerraformOutputs -- "Populates" --> GitHubSecrets["GitHub Secrets"]

    Terraform -- "Manages" --> GCPState
    Terraform -- "Stores State" --> GCSState

    CloudMonitoring -- "Notifications" --> EmailAlerts["📧 Email Alerts"]


    classDef default fill:#fff,stroke:#333,stroke-width:2px;
    classDef gcp fill:#e3f2fd,stroke:#4285f4,stroke-width:2px,color:#333;
    classDef vercel fill:#f0f0f0,stroke:#000,stroke-width:2px,color:#333;
    classDef external fill:#e8f5e9,stroke:#34a853,stroke-width:2px,color:#333;
    classDef devops fill:#fff3e0,stroke:#fbbc05,stroke-width:2px,color:#333;

    class User,FrontendApp vercel;
    class APIVM,PubSub,WorkerCF,ArtifactRegistry,SecretManager,GCSAssets,CloudMonitoring,GCPState gcp;
    class Supabase,SupabaseDB,SupabaseAuth,SupabaseStorage,SupabaseEdgeFunc,JigsawStack,UpstashRedis external;
    class GitHubActions,Terraform,GCSState,TerraformOutputs,GitHubSecrets devops;
```
