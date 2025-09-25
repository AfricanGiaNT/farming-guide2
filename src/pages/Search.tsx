import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Search as SearchIcon, Filter, FileText, Tag, TrendingUp, ChevronDown, ChevronUp, Bug, Sprout, Globe, BarChart3 } from 'lucide-react';
import { mockSearchResults } from '../utils/mockData';
import { SearchCategory } from '../types';

const Search: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<SearchCategory>('all');
  const [showTips, setShowTips] = useState(false);

  const categories: { value: SearchCategory; label: string; icon: typeof FileText; count: number }[] = [
    { value: 'all', label: 'All Topics', icon: FileText, count: 156 },
    { value: 'pests', label: 'Pest Control', icon: Bug, count: 42 },
    { value: 'crops', label: 'Crops', icon: Sprout, count: 38 },
    { value: 'soil', label: 'Soil Care', icon: Globe, count: 28 },
    { value: 'markets', label: 'Markets', icon: BarChart3, count: 24 }
  ];

  const popularSearchesByCategory = {
    'Pest Control': [
      { term: 'Fall armyworm control', icon: '🐛' },
      { term: 'Pest management', icon: '🛡️' }
    ],
    'Crops': [
      { term: 'Maize varieties', icon: '🌽' },
      { term: 'Crop rotation', icon: '🔄' }
    ],
    'Soil': [
      { term: 'Soil fertility', icon: '🌱' },
      { term: 'Fertilizer application', icon: '💧' }
    ]
  };

  const filteredResults = mockSearchResults.filter(result => {
    const matchesSearch = searchTerm === '' || 
      result.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      result.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'all' || result.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const handlePopularSearch = (term: string) => {
    setSearchTerm(term);
  };

  const getCategoryIcon = (category: string) => {
    const iconMap: Record<string, string> = {
      crops: '🌱',
      pests: '🐛',
      soil: '🌍',
      weather: '🌤️',
      markets: '📈'
    };
    return iconMap[category] || '📄';
  };

  const getRelevanceColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-8">
      {/* Header with better spacing */}
      <div className="text-center md:text-left">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-3">Find Farming Solutions</h1>
        <p className="text-gray-600 text-lg leading-relaxed">
          Search guides, tips, and expert advice for better farming
        </p>
      </div>

      {/* Prominent Search Bar */}
      <Card className="shadow-lg border-2 border-green-100">
        <CardContent className="p-6">
          <div className="relative">
            <SearchIcon size={24} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-green-600" />
            <input
              type="text"
              placeholder="What farming challenge can we help you solve?"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all"
            />
          </div>
        </CardContent>
      </Card>

      {/* Simplified Category Filters */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Browse by Topic</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
                className={`p-4 rounded-xl text-center transition-all duration-200 min-h-[80px] ${
                  selectedCategory === category.value
                    ? 'bg-green-100 text-green-700 border-2 border-green-300 shadow-md scale-105'
                    : 'bg-white text-gray-700 border-2 border-gray-200 hover:bg-gray-50 hover:border-gray-300'
                }`}
              >
                <Icon size={24} className="mx-auto mb-2" />
                <div className="text-sm font-medium">{category.label}</div>
                <div className="text-xs text-gray-500 mt-1">{category.count} guides</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Popular Searches - Moved Up and Improved */}
      {searchTerm === '' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">Quick Solutions</h3>
          {Object.entries(popularSearchesByCategory).map(([categoryName, searches]) => (
            <Card key={categoryName} className="bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200">
              <CardContent className="p-6">
                <h4 className="font-semibold text-orange-800 mb-4 flex items-center gap-2">
                  <TrendingUp size={18} />
                  {categoryName}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {searches.map((search, index) => (
                    <button
                      key={index}
                      onClick={() => handlePopularSearch(search.term)}
                      className="flex items-center gap-3 p-3 bg-white rounded-lg hover:bg-orange-50 transition-all duration-200 text-left shadow-sm hover:shadow-md"
                    >
                      <span className="text-xl">{search.icon}</span>
                      <span className="font-medium text-gray-800">{search.term}</span>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Search Results */}
      {(searchTerm !== '' || selectedCategory !== 'all') && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              {filteredResults.length} solutions found
              {searchTerm && (
                <span className="text-green-600 ml-2">for "{searchTerm}"</span>
              )}
            </h3>
          </div>

          <div className="space-y-4">
            {filteredResults.length > 0 ? (
              filteredResults.map((result) => (
                <Card key={result.id} className="hover:shadow-lg transition-all duration-200 cursor-pointer border-l-4 border-l-green-500">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-start gap-4">
                        <div className="bg-green-100 p-3 rounded-lg">
                          <span className="text-2xl">{getCategoryIcon(result.category)}</span>
                        </div>
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 hover:text-green-600 transition-colors mb-2">
                            {result.title}
                          </h3>
                          <p className="text-sm text-green-600 capitalize font-medium mb-2">
                            {result.category} guide
                          </p>
                          <p className="text-gray-600 leading-relaxed">{result.excerpt}</p>
                        </div>
                      </div>
                      <span className={`text-xs font-bold px-2 py-1 rounded-full ${getRelevanceColor(result.relevanceScore)} bg-gray-100`}>
                        {result.relevanceScore}%
                      </span>
                    </div>

                    {/* Tags with better spacing */}
                    <div className="flex items-center gap-3 flex-wrap pt-4 border-t border-gray-100">
                      <Tag size={16} className="text-gray-400" />
                      {result.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-50 text-blue-700 text-sm rounded-full font-medium"
                        >
                          {tag}
                        </span>
                      ))}
                      {result.tags.length > 3 && (
                        <span className="text-sm text-gray-500 font-medium">
                          +{result.tags.length - 3} more topics
                        </span>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="text-center py-16">
                <div className="bg-gray-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <SearchIcon size={32} className="text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">No solutions found</h3>
                <p className="text-gray-500 mb-6 max-w-md mx-auto leading-relaxed">
                  Try different words or browse our popular topics above.
                </p>
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setSelectedCategory('all');
                  }}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
                >
                  Browse All Topics
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Collapsible Search Tips */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <button
            onClick={() => setShowTips(!showTips)}
            className="flex items-center justify-between w-full text-left"
          >
            <h3 className="font-semibold text-blue-800 flex items-center gap-2">
              💡 Need help searching?
            </h3>
            {showTips ? (
              <ChevronUp size={20} className="text-blue-600" />
            ) : (
              <ChevronDown size={20} className="text-blue-600" />
            )}
          </button>
          
          {showTips && (
            <div className="mt-6 grid md:grid-cols-3 gap-6 text-blue-700">
              <div className="space-y-2">
                <h4 className="font-medium">Use simple words</h4>
                <p className="text-sm leading-relaxed">
                  Try "maize pest" instead of "maize stem borer control methods"
                </p>
                <div className="bg-blue-100 p-2 rounded text-xs">
                  Example: "maize pest" ✓
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium">Pick a topic</h4>
                <p className="text-sm leading-relaxed">
                  Use the topic buttons to find guides faster
                </p>
                <div className="bg-blue-100 p-2 rounded text-xs">
                  Click "Pest Control" first
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium">Try popular searches</h4>
                <p className="text-sm leading-relaxed">
                  See what other farmers search for most
                </p>
                <div className="bg-blue-100 p-2 rounded text-xs">
                  Check "Quick Solutions" above
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Search;