Set up Environment Variables for Preview Deployments
Make sure you add the environment variables to the "Preview" environment in Vercel:
Go to "Settings" → "Environment Variables"
Add these variables to the "Preview" environment:
VITE_API_URL: http://35.211.60.188/api
VITE_SUPABASE_URL: Your dev Supabase URL
VITE_SUPABASE_ANON_KEY: Your dev Supabase anon key
VITE_ENVIRONMENT: development
Update Backend CORS Configuration
You'll need to update your backend CORS settings to allow requests from the Vercel preview URL:
Find your backend CORS configuration (likely in backend/app/core/config.py or a similar file)
Add https://\*.vercel.app to the allowed origins
Deploy the updated backend
This setup will ensure that:
Your develop branch gets its own preview URL
Your frontend can communicate with your backend API
CORS issues are avoided
Do you need help with any specific part of this process?
