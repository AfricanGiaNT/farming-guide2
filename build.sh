#!/bin/bash
# Build script for Render deployment
# Builds frontend and prepares for unified deployment

set -e  # Exit on error

echo "🔨 Starting build process..."

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Set API base URL for production (relative path since same domain)
export VITE_API_BASE_URL="/api"

# Build frontend
echo "🏗️  Building frontend..."
# Use npx to ensure proper permissions
npx vite build

# Verify dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed - dist directory not found"
    exit 1
fi

echo "✅ Build complete!"
echo "📁 Frontend built to: dist/"
echo "🌐 API base URL: /api"
echo "🚀 Ready for deployment!"

