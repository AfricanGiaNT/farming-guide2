# Deployment Guide - Render

This guide explains how to deploy both the frontend and backend together as a unified service on Render.

## Architecture

- **Frontend**: React + Vite (built to `dist/` folder)
- **Backend**: Flask API server (serves both API and static frontend files)
- **Deployment**: Single web service on Render

## Prerequisites

1. Render account
2. All environment variables ready:
   - `OPENWEATHERMAP_API_KEY`
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `DATABASE_URL` (if using PostgreSQL)

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Connect Repository**:
   - Go to Render Dashboard → New → Web Service
   - Connect your GitHub repository
   - Select the branch to deploy

2. **Configure Service**:
   - Render will automatically detect `render.yaml`
   - Verify the configuration:
     - Build Command: `bash build.sh`
     - Start Command: `python api_server.py`
     - Python Version: 3.11.0
     - Node Version: 18.18.0

3. **Set Environment Variables**:
   - Go to Environment tab in Render dashboard
   - Add all required environment variables:
     - `OPENWEATHERMAP_API_KEY`
     - `OPENAI_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`
     - `DATABASE_URL` (if needed)

4. **Deploy**:
   - Click "Create Web Service"
   - Render will:
     1. Install Node.js dependencies
     2. Run `build.sh` to build frontend
     3. Install Python dependencies
     4. Start the Flask server

### Option 2: Manual Configuration

1. **Create Web Service**:
   - Type: Web Service
   - Runtime: Python 3
   - Build Command: `bash build.sh`
   - Start Command: `python api_server.py`

2. **Environment Variables**:
   - Set all required API keys in the dashboard

3. **Deploy**

## Build Process

The build process (`build.sh`) does the following:

1. Installs frontend dependencies (`npm install`)
2. Builds frontend to `dist/` folder (`npm run build`)
3. Verifies the build succeeded

## How It Works

### Request Flow

1. **API Requests** (`/api/*`):
   - Handled by Flask API routes
   - Processed by backend services

2. **Static Assets** (`/assets/*`, `/favicon.ico`, etc.):
   - Served from `dist/` folder by Flask
   - Handled by `serve_frontend()` route

3. **Frontend Routes** (everything else):
   - Served `dist/index.html` for SPA routing
   - Client-side router handles navigation

### Flask Route Ordering

The Flask app registers routes in this order:
1. All API routes (`/api/*`)
2. Frontend catch-all routes (`/`, `/<path>`)

This ensures API routes are matched first before the frontend handler.

## Testing Locally

Before deploying, test the build process:

```bash
# Make build script executable (Linux/Mac)
chmod +x build.sh

# Run build
bash build.sh

# Start server
python api_server.py

# Visit http://localhost:8000
```

## Troubleshooting

### Frontend Not Loading

- Check that `dist/` folder exists after build
- Verify build completed successfully in Render logs
- Check that `serve_frontend()` route is registered

### API Routes Not Working

- Verify route ordering (API routes before frontend catch-all)
- Check Flask logs for route matching
- Test API endpoint directly: `https://your-app.onrender.com/api/health`

### Build Fails

- Check Node.js version (should be 18.x)
- Verify `package.json` and `vite.config.ts` are valid
- Check build logs for specific errors

### Environment Variables Not Loading

- Verify all variables are set in Render dashboard
- Check variable names match exactly
- Restart service after adding variables

## Post-Deployment

After successful deployment:

1. **Test API**: `https://your-app.onrender.com/api/health`
2. **Test Frontend**: `https://your-app.onrender.com`
3. **Monitor Logs**: Check Render logs for any errors
4. **Set Custom Domain** (optional): Configure in Render dashboard

## Notes

- Render provides free SSL certificates automatically
- Service will sleep after 15 minutes of inactivity (free plan)
- First request after sleep may be slow (cold start)
- Consider upgrading to a paid plan for always-on service

