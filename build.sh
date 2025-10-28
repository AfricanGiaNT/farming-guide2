#!/bin/bash
# Build script for Render deployment
# Builds frontend and prepares for unified deployment

set -e  # Exit on error

echo "🔨 Starting build process..."

# Clean install frontend dependencies
echo "📦 Installing frontend dependencies..."
rm -rf node_modules package-lock.json
npm install

# Set API base URL for production (relative path since same domain)
export VITE_API_BASE_URL="/api"

# Build frontend using npm script
echo "🏗️  Building frontend..."
npm run build

# Verify dist directory exists
if [ ! -d "dist" ]; then
    echo "❌ Error: Frontend build failed - dist directory not found"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build complete!"
echo "📁 Frontend built to: dist/"
echo "🌐 API base URL: /api"
echo "🐍 Python dependencies installed"
echo "🚀 Ready for deployment!"

