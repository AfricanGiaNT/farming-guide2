# Mlangizi wa Ulimi - Frontend PRD (Simplified)

**Version:** 1.0  
**Date:** January 2025  
**Goal:** Get agricultural advisory frontend up and running quickly  

---

## 1. Overview

### 1.1 Objective
Create a mobile-first web frontend for the existing agricultural advisory system to expand beyond Telegram users.

### 1.2 Target Users
- **Primary:** Smallholder farmers in Malawi (basic smartphones, limited internet)
- **Secondary:** Extension workers and agricultural students

### 1.3 Success Metrics
- Page load: <3 seconds on 3G
- 90%+ mobile usability score
- 500 users by Month 12

---

## 2. Technology Stack

### 2.1 Core Technologies
- **Frontend:** React.js + TypeScript
- **Styling:** Tailwind CSS (mobile-first)
- **State:** React Context (simple state management)
- **PWA:** Service Workers for offline support
- **Maps:** Mapbox GL JS for location features
- **Charts:** Chart.js for data visualization

### 2.2 Deployment
- **Hosting:** Vercel or Netlify (easy deployment)
- **Domain:** Custom domain with SSL
- **CDN:** Built-in with hosting platform

## 3. Core Pages & Features

### 3.1 Essential Pages (MVP)
1. **Home Dashboard** - Weather widget + quick actions
2. **Weather Page** - Current conditions + 7-day forecast
3. **Crop Recommendations** - Location-based suggestions
4. **Variety Search** - Crop variety information
5. **Knowledge Search** - Document search interface

### 3.2 Page Structure
```
├── Home (Dashboard)
│   ├── Weather Widget
│   ├── Quick Actions (4 buttons)
│   └── Recent Activity
├── Weather
│   ├── Current Conditions
│   ├── 7-Day Forecast
│   └── Rainfall Chart
├── Crops
│   ├── Location Input
│   ├── Season Filter
│   └── Recommendation Cards
├── Varieties
│   ├── Search Bar
│   ├── Filter Options
│   └── Variety Cards
└── Search
    ├── Search Input
    ├── Category Filters
    └── Results List
```

## 4. UI Components & Design

### 4.1 Design System
- **Colors:** Green primary (#2E7D32), Blue secondary (#1976D2)
- **Typography:** System fonts (San Francisco, Roboto)
- **Icons:** Heroicons or Lucide React
- **Mobile-first:** 320px minimum width

### 4.2 Key Components
- **Navigation:** Bottom tab bar (mobile) + sidebar (desktop)
- **Cards:** Weather cards, crop recommendation cards
- **Forms:** Location input, search bars, filters
- **Charts:** Simple line/bar charts for weather data
- **Buttons:** Primary actions, secondary actions, icon buttons

## 5. Development Plan

### 5.1 Setup (Week 1)
- [ ] Create React + TypeScript project with Vite
- [ ] Set up Tailwind CSS
- [ ] Configure PWA with service worker
- [ ] Set up basic routing (React Router)
- [ ] Create component folder structure

### 5.2 Core Pages (Weeks 2-4)
- [ ] **Home Dashboard:** Weather widget + navigation
- [ ] **Weather Page:** Current + forecast display
- [ ] **Crop Page:** Location input + recommendation cards
- [ ] **Varieties Page:** Search + filter interface
- [ ] **Search Page:** Document search interface

### 5.3 Polish & Deploy (Week 5)
- [ ] Mobile responsiveness testing
- [ ] Performance optimization
- [ ] PWA offline functionality
- [ ] Deploy to Vercel/Netlify
- [ ] Domain setup and SSL

## 6. Mock Data Structure

### 6.1 API Response Examples
```javascript
// Weather Data
{
  "location": "Lilongwe",
  "current": {
    "temperature": 28,
    "humidity": 65,
    "rainfall": 0,
    "description": "Partly cloudy"
  },
  "forecast": [
    { "date": "2025-01-26", "temp_high": 30, "temp_low": 18, "rain_chance": 20 },
    // ... 6 more days
  ]
}

// Crop Recommendations
{
  "location": "Lilongwe",
  "season": "rainy",
  "recommendations": [
    {
      "crop": "maize",
      "score": 85,
      "varieties": ["SC627", "DK8053"],
      "planting_time": "November-December",
      "yield_potential": "4-6 tons/ha"
    },
    // ... more crops
  ]
}
```

### 6.2 Folder Structure
```
src/
├── components/
│   ├── ui/           # Basic UI components
│   ├── weather/      # Weather-specific components
│   ├── crops/        # Crop-related components
│   └── layout/       # Navigation, headers
├── pages/
│   ├── Home.tsx
│   ├── Weather.tsx
│   ├── Crops.tsx
│   ├── Varieties.tsx
│   └── Search.tsx
├── hooks/            # Custom React hooks
├── utils/            # Helper functions
└── types/            # TypeScript types
```

## 7. Quick Start Commands

### 7.1 Project Setup
```bash
# Create React app with Vite
npm create vite@latest mlangizi-frontend -- --template react-ts
cd mlangizi-frontend

# Install dependencies
npm install
npm install -D tailwindcss postcss autoprefixer
npm install react-router-dom
npm install lucide-react  # for icons
npm install chart.js react-chartjs-2  # for charts

# Initialize Tailwind
npx tailwindcss init -p
```

### 7.2 Essential Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "lucide-react": "^0.263.1",
    "chart.js": "^4.3.0",
    "react-chartjs-2": "^5.2.0"
  },
  "devDependencies": {
    "typescript": "^5.0.2",
    "tailwindcss": "^3.3.0",
    "vite": "^4.4.5",
    "vite-plugin-pwa": "^0.16.4"
  }
}
```

---

## 8. Next Steps

1. **Set up development environment** using the commands above
2. **Create basic page layouts** with mock data
3. **Implement navigation** between pages
4. **Add responsive design** with Tailwind
5. **Deploy to Vercel** for testing
6. **Connect to your backend APIs** when ready

---

**Total Estimated Timeline:** 5 weeks for MVP  
**Key Focus:** Simple, fast, mobile-first interface that works offline
