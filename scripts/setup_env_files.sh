#!/bin/bash
# Setup script to create the necessary .env files for branch-based environment switching

echo "Setting up environment files for branch-based switching..."

# Create backend directory if it doesn't exist
mkdir -p backend

# Create frontend directory if it doesn't exist
mkdir -p frontend/my-app

# Backend .env.example
cat > backend/.env.example << 'EOL'
# Backend Environment Variables Example
# Copy this file to .env.develop or .env.main and fill in appropriate values

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1
DEBUG=True  # Set to False in production
LOGGING_LEVEL=DEBUG  # Set to INFO or WARNING in production

# JigsawStack API (if used)
JIGSAWSTACK_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/concept_visualizer

# Security
SECRET_KEY=your_secret_key_here  # Change this in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Other External Services
# Add service-specific keys here
EOL

# Backend .env.develop
cat > backend/.env.develop << 'EOL'
# Backend Development Environment Variables
# This file is automatically copied to .env when on the develop branch

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1
DEBUG=True
LOGGING_LEVEL=DEBUG

# JigsawStack API (if used)
JIGSAWSTACK_API_KEY=dev_api_key_here

# Database Configuration
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/concept_visualizer_dev

# Security
SECRET_KEY=dev_secret_key_for_local_development_only
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Other External Services
# Add development service-specific keys here
EOL

# Backend .env.main
cat > backend/.env.main << 'EOL'
# Backend Production/Main Environment Variables
# This file is automatically copied to .env when on the main branch
# IMPORTANT: Replace placeholder values with actual production values securely

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1
DEBUG=False
LOGGING_LEVEL=INFO

# JigsawStack API (if used)
JIGSAWSTACK_API_KEY=YOUR_PRODUCTION_API_KEY_HERE

# Database Configuration
DATABASE_URL=postgresql://YOUR_PRODUCTION_DB_USER:YOUR_PRODUCTION_DB_PASSWORD@your-prod-db-host:5432/concept_visualizer_prod

# Security
SECRET_KEY=YOUR_PRODUCTION_SECRET_KEY_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://your-production-domain.com

# Other External Services
# Add production service-specific keys here
EOL

# Frontend .env.example
cat > frontend/my-app/.env.example << 'EOL'
# Frontend Environment Variables Example
# Copy this file to .env.develop or .env.main and fill in appropriate values

# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=development

# Feature flags
VITE_ENABLE_DEBUG_TOOLS=true

# External services
VITE_ANALYTICS_ID=your_analytics_id_here
EOL

# Frontend .env.develop
cat > frontend/my-app/.env.develop << 'EOL'
# Frontend Development Environment Variables
# This file is automatically copied to .env when on the develop branch

# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_ENV=development

# Feature flags
VITE_ENABLE_DEBUG_TOOLS=true

# External services
VITE_ANALYTICS_ID=dev_analytics_id_here
EOL

# Frontend .env.main
cat > frontend/my-app/.env.main << 'EOL'
# Frontend Production/Main Environment Variables
# This file is automatically copied to .env when on the main branch
# IMPORTANT: Replace placeholder values with actual production values securely

# API Configuration
VITE_API_BASE_URL=https://your-production-domain.com/api/v1
VITE_APP_ENV=production

# Feature flags
VITE_ENABLE_DEBUG_TOOLS=false

# External services
VITE_ANALYTICS_ID=YOUR_PRODUCTION_ANALYTICS_ID_HERE
EOL

echo "Environment files created successfully!"
echo ""
echo "Next steps:"
echo "1. Review and update the created .env.develop and .env.main files with your actual values"
echo "2. Make sure the post-checkout hook is executable: chmod +x .git/hooks/post-checkout"
echo "3. Switch branches to see the hook in action: git checkout develop OR git checkout main"
echo ""
echo "Remember: The .env files are automatically managed by the post-checkout hook. Do not manually edit the .env files directly!"
