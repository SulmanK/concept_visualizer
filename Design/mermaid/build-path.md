%%{init:{
'theme':'default',
'flowchart':{ 'htmlLabels':true, 'nodeSpacing':100, 'rankSpacing':60 },
'securityLevel':'loose',
'themeCSS':'.label, .node text, .edgeLabel tspan{font-size:50px !important;}.cluster-label'
'themeCSS':'.cluster-label text{font-size:50px !important;}'
}}%%
graph TD
%% ───────── DevOps / IaC ─────────
subgraph DevOps["<span style='font-size:18px;font-weight:bold;'>DevOps &amp; Orchestration</span>"]
GitHubActions["<img src='https://static.vecteezy.com/system/resources/previews/024/555/259/original/github-logo-transparent-free-png.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GitHub Actions (CI/CD)"]
Terraform["<img src='https://opensenselabs.com/sites/default/files/inline-images/terraform.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Terraform (IaC)"]
GCSState["<img src='https://k21academy.com/wp-content/uploads/2021/02/Google-Cloud-Storage-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> GCS Bucket (Terraform State)"]
TerraformOutputs["📝 Terraform Outputs"]
GitHubSecrets["🔒 GitHub Secrets"]
end

    %% ───────── Artifacts / Registry ─────────
    ArtifactRegistry["<img src='https://sysdig.com/wp-content/uploads/logo-google-cloud-artifact-registry.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Artifact Registry (Docker Images)"]

    %% ───────── Deployment Targets ─────────
    FrontendApp["⚛️ Frontend Application (React, Vite)"]
    GCPState["🌐 GCP Resources"]

    %% (show a few representative GCP resources to hint where images go)
    APIVM["<img src='https://k21academy.com/wp-content/uploads/2021/01/Google_Compute_Engine-Logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> API Server"]
    WorkerCF["<img src='https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_87f5b15be060087098cc881c06279eac/google-cloud-functions.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Worker CF"]
    PubSub["<img src='https://iconape.com/wp-content/files/jg/62017/png/google-cloud-pub-sub-logo.png' style='width:75px;height:75px;object-fit:contain;vertical-align:middle;'/> Pub/Sub"]

    %% ─── Flows ───
    GitHubActions -- "Push Images"                 --> ArtifactRegistry
    GitHubActions -- "Plan / Apply"                --> Terraform
    GitHubActions -- "Deploy Frontend"             --> FrontendApp
    GitHubActions -- "Read Outputs"                --> TerraformOutputs
    TerraformOutputs -- "Populate"                 --> GitHubSecrets

    Terraform      -- "Stores State"               --> GCSState
    Terraform      -- "Provision"                  --> GCPState
    GCPState       -.- APIVM
    GCPState       -.- WorkerCF
    GCPState       -.- PubSub
    GCPState       -.- ArtifactRegistry

    GitHubActions -- "Deploy Infrastructure"       --> GCPState
    GitHubActions -- "Cron Triggers"               --> SupabaseEdgeFunc["⚡ Edge Function (Cleanup)"]

    %% ───────── Styles ─────────
    classDef default  fill:#fff,stroke:#333,stroke-width:2px;
    classDef devops   fill:#fff3e0,stroke:#fbbc05,stroke-width:2px,color:#333;
    classDef gcp      fill:#e3f2fd,stroke:#4285f4,stroke-width:2px,color:#333;

    class GitHubActions,Terraform,GCSState,TerrainformOutputs,GitHubSecrets devops;
    class ArtifactRegistry,APIVM,WorkerCF,PubSub,GCPState gcp;
