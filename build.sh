#!/bin/bash
# Build script for Render deployment
# Builds frontend and prepares for unified deployment

set -e  # Exit on error

echo "🔨 Starting build process..."

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
npm install --legacy-peer-deps

# Set API base URL for production (relative path since same domain)
export VITE_API_BASE_URL="/api"

# Build frontend
echo "🏗️  Building frontend..."
# Use node directly to run vite to avoid permission issues
node node_modules/vite/bin/vite.js build

# Verify dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Build complete!"
echo "📁 Frontend built to: dist/"
echo "🌐 API base URL: /api"
echo "🚀 Ready for deployment!"

