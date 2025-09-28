/**
 * Tests for EnhancedCropCard Component
 * Tests enhanced crop card functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import EnhancedCropCard from '../EnhancedCropCard'

const mockCrop = {
  crop_name: 'maize',
  score: 85,
  suitability_level: 'excellent' as const,
  rainfall_match: 'excellent' as const,
  temperature_match: 'good' as const,
  season_suitability: 'excellent' as const,
  sources: ['Malawi Agriculture Guide'],
  guide_recommendations: [
    'Plant in November-December for best results',
    'Use certified seeds for higher yields',
  ],
  varieties: ['SC627', 'DK8053', 'MH30'],
  planting_time: 'November-December',
  yield_potential: '4-6 tons/ha',
  description: 'Excellent for current conditions',
  ai_summary: 'Maize is highly suitable for current conditions',
  key_benefits: ['High yield potential', 'Good disease resistance'],
  potential_challenges: ['Requires adequate rainfall', 'Susceptible to pests'],
  actionable_steps: ['Prepare soil', 'Source quality seeds'],
  seasonal_advice: 'Best planted during rainy season',
  confidence_score: 0.9,
}

describe('EnhancedCropCard', () => {
  it('should render crop name and score', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    expect(screen.getByText('Maize')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('should display suitability level chip', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    expect(screen.getByText('Excellent')).toBeInTheDocument()
  })

  it('should show rank icon', () => {
    render(<EnhancedCropCard crop={mockCrop} rank={1} />)
    
    expect(screen.getByText('🥇')).toBeInTheDocument()
  })

  it('should display match indicators', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    expect(screen.getByText('Rainfall')).toBeInTheDocument()
    expect(screen.getByText('Temperature')).toBeInTheDocument()
    expect(screen.getByText('Season')).toBeInTheDocument()
  })

  it('should show quick info chips', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    expect(screen.getByText('Plant: November-December')).toBeInTheDocument()
    expect(screen.getByText('Yield: 4-6 tons/ha')).toBeInTheDocument()
    expect(screen.getByText('Confidence: 90%')).toBeInTheDocument()
  })

  it('should expand when expand button is clicked', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('Description')).toBeInTheDocument()
      expect(screen.getByText('Excellent for current conditions')).toBeInTheDocument()
    })
  })

  it('should collapse when expand button is clicked again', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    
    // Expand first
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.getByText('Description')).toBeInTheDocument()
    })
    
    // Collapse
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.queryByText('Description')).not.toBeInTheDocument()
    })
  })

  it('should display varieties when expanded', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('Recommended Varieties')).toBeInTheDocument()
      expect(screen.getByText('SC627')).toBeInTheDocument()
      expect(screen.getByText('DK8053')).toBeInTheDocument()
      expect(screen.getByText('MH30')).toBeInTheDocument()
    })
  })

  it('should display guide recommendations when expanded', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('Guide Recommendations')).toBeInTheDocument()
      expect(screen.getByText('Plant in November-December for best results')).toBeInTheDocument()
      expect(screen.getByText('Use certified seeds for higher yields')).toBeInTheDocument()
    })
  })

  it('should display AI insights when available', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('🤖 AI-Enhanced Insights')).toBeInTheDocument()
      expect(screen.getByText('"Maize is highly suitable for current conditions"')).toBeInTheDocument()
      expect(screen.getByText('✅ Key Benefits')).toBeInTheDocument()
      expect(screen.getByText('⚠️ Potential Challenges')).toBeInTheDocument()
      expect(screen.getByText('📋 Actionable Steps')).toBeInTheDocument()
      expect(screen.getByText('📅 Seasonal Advice')).toBeInTheDocument()
    })
  })

  it('should display sources when expanded', async () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={true} />)
    
    const expandButton = screen.getByRole('button', { name: /show more details/i })
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('Sources: Malawi Agriculture Guide')).toBeInTheDocument()
    })
  })

  it('should call onFavorite when favorite button is clicked', () => {
    const onFavorite = jest.fn()
    render(<EnhancedCropCard crop={mockCrop} onFavorite={onFavorite} />)
    
    const favoriteButton = screen.getByRole('button', { name: /add to favorites/i })
    fireEvent.click(favoriteButton)
    
    expect(onFavorite).toHaveBeenCalledWith('maize')
  })

  it('should show filled star when crop is favorite', () => {
    render(<EnhancedCropCard crop={mockCrop} isFavorite={true} />)
    
    expect(screen.getByRole('button', { name: /remove from favorites/i })).toBeInTheDocument()
  })

  it('should hide details when showDetails is false', () => {
    render(<EnhancedCropCard crop={mockCrop} showDetails={false} />)
    
    expect(screen.queryByRole('button', { name: /show more details/i })).not.toBeInTheDocument()
  })

  it('should render in compact mode', () => {
    render(<EnhancedCropCard crop={mockCrop} compact={true} />)
    
    expect(screen.getByText('Maize')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('should display correct score color for different scores', () => {
    const highScoreCrop = { ...mockCrop, score: 90 }
    const lowScoreCrop = { ...mockCrop, score: 30 }
    
    const { rerender } = render(<EnhancedCropCard crop={highScoreCrop} />)
    expect(screen.getByText('90%')).toBeInTheDocument()
    
    rerender(<EnhancedCropCard crop={lowScoreCrop} />)
    expect(screen.getByText('30%')).toBeInTheDocument()
  })

  it('should display correct rank icons', () => {
    const { rerender } = render(<EnhancedCropCard crop={mockCrop} rank={1} />)
    expect(screen.getByText('🥇')).toBeInTheDocument()
    
    rerender(<EnhancedCropCard crop={mockCrop} rank={2} />)
    expect(screen.getByText('🥈')).toBeInTheDocument()
    
    rerender(<EnhancedCropCard crop={mockCrop} rank={3} />)
    expect(screen.getByText('🥉')).toBeInTheDocument()
    
    rerender(<EnhancedCropCard crop={mockCrop} rank={4} />)
    expect(screen.getByText('#4')).toBeInTheDocument()
  })

  it('should handle missing optional fields gracefully', () => {
    const minimalCrop = {
      crop_name: 'maize',
      score: 85,
      suitability_level: 'excellent' as const,
      rainfall_match: 'excellent' as const,
      temperature_match: 'good' as const,
      season_suitability: 'excellent' as const,
    }
    
    render(<EnhancedCropCard crop={minimalCrop} />)
    
    expect(screen.getByText('Maize')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('should display progress bar with correct value', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '85')
  })

  it('should show correct match icons', () => {
    render(<EnhancedCropCard crop={mockCrop} />)
    
    // Check for match indicator icons
    expect(screen.getByText('🟢')).toBeInTheDocument() // excellent rainfall
    expect(screen.getByText('🟡')).toBeInTheDocument() // good temperature
    expect(screen.getByText('🟢')).toBeInTheDocument() // excellent season
  })
})
