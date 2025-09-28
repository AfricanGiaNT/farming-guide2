import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { Search, MapPin, Sprout, GitCompare, AlertCircle, Clock, TrendingUp, Droplets, Shield, Loader2 } from 'lucide-react'
import { useVarietyInformation } from '../hooks/useCropRecommendations'

interface Variety {
  name: string
  maturity_days: number
  yield_potential: string
  drought_tolerance: string
  disease_resistance: string
  planting_time: string
  description: string
  weather_requirements?: string
  soil_requirements?: string
  growing_areas?: string
}

const Varieties: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedCrop, setSelectedCrop] = useState(searchParams.get('crop') || '')
  const [locationInput, setLocationInput] = useState('')
  const [compareMode, setCompareMode] = useState(false)
  const [selectedVarieties, setSelectedVarieties] = useState<string[]>([])

  // Parse coordinates from URL params
  const lat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : undefined
  const lon = searchParams.get('lon') ? parseFloat(searchParams.get('lon')!) : undefined

  const { data: varietyData, isLoading, error } = useVarietyInformation(selectedCrop, lat, lon)

  const cropOptions = [
    'Maize', 'Beans', 'Groundnuts', 'Sorghum', 'Cassava', 'Sweet Potato',
    'Soybeans', 'Pigeon Peas', 'Cowpeas', 'Rice', 'Millet', 'Wheat',
    'Tomato', 'Onion', 'Cabbage', 'Lettuce', 'Spinach', 'Carrot',
    'Pepper', 'Eggplant', 'Cucumber', 'Pumpkin', 'Watermelon',
  ]

  // Function to parse coordinates from location input
  const parseCoordinates = (input: string): { lat: number; lon: number } | null => {
    if (!input.trim()) return null
    
    // Try to match coordinate patterns like "-13.9833, 33.7833"
    const coordPattern = /(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)/
    const match = input.match(coordPattern)
    
    if (match) {
      const lat = parseFloat(match[1])
      const lon = parseFloat(match[2])
      if (!isNaN(lat) && !isNaN(lon)) {
        return { lat, lon }
      }
    }
    
    return null
  }

  const handleSearch = () => {
    if (selectedCrop) {
      // Parse location input and update URL params
      const coords = parseCoordinates(locationInput)
      setSearchParams(prev => {
        const newParams = new URLSearchParams(prev)
        newParams.set('crop', selectedCrop)
        if (coords) {
          newParams.set('lat', coords.lat.toString())
          newParams.set('lon', coords.lon.toString())
        } else {
          newParams.delete('lat')
          newParams.delete('lon')
        }
        return newParams
      })
    }
  }

  const handleVarietySelect = (varietyName: string) => {
    if (compareMode) {
      setSelectedVarieties(prev => {
        if (prev.includes(varietyName)) {
          return prev.filter(v => v !== varietyName)
        } else if (prev.length < 3) {
          return [...prev, varietyName]
        }
        return prev
      })
    }
  }

  const varieties = varietyData?.varieties || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Sprout className="text-green-600" />
          Crop Varieties
        </h1>
        <p className="text-gray-600">
          Search and compare different crop varieties to find the best fit for your farm
        </p>
      </div>

      {/* Search Interface */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            {/* Crop Selection */}
            <div className="md:col-span-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Crop
              </label>
              <div className="relative">
                <Sprout className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <select
                  value={selectedCrop}
                  onChange={(e) => setSelectedCrop(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
                >
                  <option value="">Choose a crop...</option>
                  {cropOptions.map(crop => (
                    <option key={crop} value={crop}>{crop}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Location Input */}
            <div className="md:col-span-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location (Optional)
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  value={locationInput}
                  onChange={(e) => setLocationInput(e.target.value)}
                  placeholder="e.g., -13.9833, 33.7833 or Lilongwe"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Add coordinates for location-specific recommendations
              </p>
            </div>

            {/* Search Button */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                &nbsp;
              </label>
              <button
                onClick={handleSearch}
                disabled={!selectedCrop}
                className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
              >
                <Search size={20} />
                Search
              </button>
            </div>

            {/* Compare Toggle */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                &nbsp;
              </label>
              <button
                onClick={() => setCompareMode(!compareMode)}
                className={`w-full px-4 py-3 rounded-lg transition-colors flex items-center justify-center gap-2 ${
                  compareMode 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                <GitCompare size={20} />
                Compare
              </button>
            </div>
          </div>

          {/* Location Context */}
          {lat && lon && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-2">
                <MapPin className="text-blue-600 mt-0.5" size={16} />
                <div>
                  <p className="text-sm text-blue-800">
                    📍 Showing location-specific recommendations for coordinates: {lat.toFixed(4)}, {lon.toFixed(4)}
                  </p>
                  <p className="text-xs text-blue-600 mt-1">
                    🌦️ Weather analysis and local growing conditions included in recommendations
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Instructions */}
          {!selectedCrop && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="text-green-600 mt-0.5" size={16} />
                <div>
                  <p className="text-sm text-green-800 mb-2">
                    💡 <strong>How to use:</strong>
                  </p>
                  <ol className="text-sm text-green-700 space-y-1 ml-4 list-decimal">
                    <li>Select a crop from the dropdown (e.g., Maize, Groundnuts, Beans)</li>
                    <li>Optionally add your location for better recommendations</li>
                    <li>Click "Search" to get detailed variety information</li>
                  </ol>
                  
                  <div className="mt-3 flex flex-wrap gap-2">
                    <span className="text-xs text-green-600">Quick examples:</span>
                    <button
                      onClick={() => {
                        setSelectedCrop('Maize')
                        setLocationInput('-13.9833, 33.7833')
                      }}
                      className="text-xs bg-white px-2 py-1 rounded border border-green-300 hover:bg-green-50"
                    >
                      Maize + Location
                    </button>
                    <button
                      onClick={() => {
                        setSelectedCrop('Groundnuts')
                        setLocationInput('')
                      }}
                      className="text-xs bg-white px-2 py-1 rounded border border-green-300 hover:bg-green-50"
                    >
                      Groundnuts
                    </button>
                    <button
                      onClick={() => {
                        setSelectedCrop('Beans')
                        setLocationInput('-13.9833, 33.7833')
                      }}
                      className="text-xs bg-white px-2 py-1 rounded border border-green-300 hover:bg-green-50"
                    >
                      Beans + Location
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && selectedCrop && (
        <div className="text-center py-12">
          <Loader2 className="animate-spin mx-auto mb-4 text-green-600" size={48} />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Searching for varieties...</h3>
          <p className="text-gray-500">
            🔍 Analyzing {selectedCrop.toLowerCase()} varieties from our knowledge base
            {lat && lon && <><br />🌦️ Including location-specific recommendations</>}
          </p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200">
          <CardContent className="p-6 text-center">
            <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
            <h3 className="text-lg font-medium text-red-900 mb-2">Unable to fetch varieties</h3>
            <p className="text-red-600">Please try again later or contact support if the problem persists.</p>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {!isLoading && selectedCrop && varieties.length > 0 && (
        <>
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {selectedCrop} Varieties ({varieties.length} found)
            </h2>
            {varietyData?.real_data && (
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                ✅ Real Data
              </span>
            )}
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {varieties.map((variety: Variety, index: number) => (
              <Card key={index} className="hover:shadow-lg transition-all duration-200">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <Sprout className="text-green-600" size={20} />
                      {variety.name}
                    </CardTitle>
                    {compareMode && (
                      <button
                        onClick={() => handleVarietySelect(variety.name)}
                        className={`p-2 rounded-full transition-colors ${
                          selectedVarieties.includes(variety.name)
                            ? 'bg-blue-100 text-blue-600'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        <GitCompare size={16} />
                      </button>
                    )}
                  </div>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  <p className="text-sm text-gray-600">{variety.description}</p>

                  {/* Key Metrics */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center gap-2">
                      <Clock className="text-gray-500" size={16} />
                      <div>
                        <p className="text-xs text-gray-500">Maturity</p>
                        <p className="text-sm font-medium">{variety.maturity_days} days</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <TrendingUp className="text-gray-500" size={16} />
                      <div>
                        <p className="text-xs text-gray-500">Yield Potential</p>
                        <p className="text-sm font-medium">
                          {variety.yield_potential !== 'Not specified' ? variety.yield_potential : 'Variable'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Characteristics */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <Shield className="text-green-600" size={16} />
                      Key Characteristics
                    </h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Droplets className="text-blue-500" size={14} />
                        <span className="text-sm">
                          <strong>Drought Tolerance:</strong> {variety.drought_tolerance !== 'Not specified' ? variety.drought_tolerance : 'Standard'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Shield className="text-red-500" size={14} />
                        <span className="text-sm">
                          <strong>Disease Resistance:</strong> {variety.disease_resistance !== 'Not specified' ? variety.disease_resistance : 'Standard'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Clock className="text-green-500" size={14} />
                        <span className="text-sm">
                          <strong>Planting Time:</strong> {variety.planting_time}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Additional Requirements */}
                  {(variety.weather_requirements !== 'Not specified' || 
                    variety.soil_requirements !== 'Not specified' || 
                    variety.growing_areas !== 'Not specified') && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Growing Requirements</h4>
                      <div className="space-y-1 text-xs text-gray-600">
                        {variety.weather_requirements !== 'Not specified' && (
                          <p><strong>Weather:</strong> {variety.weather_requirements}</p>
                        )}
                        {variety.soil_requirements !== 'Not specified' && (
                          <p><strong>Soil:</strong> {variety.soil_requirements}</p>
                        )}
                        {variety.growing_areas !== 'Not specified' && (
                          <p><strong>Best Areas:</strong> {variety.growing_areas}</p>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}

      {/* No Results */}
      {!isLoading && selectedCrop && varieties.length === 0 && !error && (
        <Card>
          <CardContent className="p-12 text-center">
            <Search className="mx-auto mb-4 text-gray-400" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No varieties found</h3>
            <p className="text-gray-500">
              No varieties found for "{selectedCrop}". Try a different crop or check your spelling.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Compare Mode Instructions */}
      {compareMode && selectedVarieties.length > 0 && (
        <div className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg">
          <p className="text-sm">
            📊 {selectedVarieties.length}/3 varieties selected for comparison
          </p>
          {selectedVarieties.length > 1 && (
            <button
              onClick={() => {
                // Here you could implement a comparison view
                alert(`Comparing: ${selectedVarieties.join(', ')}`)
              }}
              className="mt-2 bg-white text-blue-600 px-3 py-1 rounded text-sm hover:bg-gray-100"
            >
              Compare Now
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default Varieties