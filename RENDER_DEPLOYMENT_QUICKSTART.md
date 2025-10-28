# Quick Start: Deploy to Render

## One-Time Setup

1. **Push code to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Add unified deployment configuration"
   git push
   ```

2. **Create Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables** in Render Dashboard:
   ```
   OPENWEATHERMAP_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   SUPABASE_URL=your_url_here
   SUPABASE_KEY=your_key_here
   DATABASE_URL=your_db_url_here (if using PostgreSQL)
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete (~5-10 minutes first time)

## What Happens During Deployment

1. ✅ Installs Node.js (v18.18.0)
2. ✅ Installs Python (v3.11.0)
3. ✅ Runs `bash build.sh` which:
   - Installs frontend dependencies
   - Builds React app to `dist/` folder
   - Sets API base URL to `/api`
4. ✅ Installs Python dependencies from `requirements.txt`
5. ✅ Starts Flask server with `python api_server.py`
6. ✅ Flask serves:
   - API at `/api/*`
   - Frontend at `/` and all other routes

## After Deployment

- **Your App URL**: `https://mlangizi-wa-ulimi.onrender.com`
- **API Health Check**: `https://mlangizi-wa-ulimi.onrender.com/api/health`
- **Frontend**: `https://mlangizi-wa-ulimi.onrender.com`

## Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `build.sh` is executable (it is)

**Frontend shows "Frontend not built"?**
- Check build logs for errors
- Verify `dist/` folder was created

**API returns 404?**
- Verify API routes are working: `/api/health`
- Check Flask logs in Render dashboard

## Files Created for Deployment

- `build.sh` - Build script for frontend
- `render.yaml` - Render deployment configuration
- `DEPLOYMENT.md` - Detailed deployment guide
- Modified `api_server.py` - Added static file serving

## Important Notes

⚠️ **Free Plan Limitations:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- Upgrade to paid plan for always-on service

✅ **Production API URL:**
- Frontend uses `/api` (relative path) in production
- No CORS issues since same domain

