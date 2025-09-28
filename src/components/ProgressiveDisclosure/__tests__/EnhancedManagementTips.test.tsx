/**
 * Tests for EnhancedManagementTips Component
 * Tests enhanced management tips functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import EnhancedManagementTips from '../EnhancedManagementTips'

const mockCategorizedTips = {
  planting: [
    'Plant seeds in well-prepared soil',
    'Use certified seeds for better yields',
    'Ensure proper spacing between plants',
  ],
  maintenance: [
    'Monitor soil moisture regularly',
    'Apply fertilizer at recommended rates',
    'Control weeds early in the season',
    'Monitor for pest and disease signs',
  ],
  harvest: [
    'Harvest when crops are mature',
    'Store harvested crops properly',
  ],
  general: [
    'Follow recommended planting schedule',
    'Maintain good field hygiene',
  ],
}

const mockTipArray = [
  { text: 'Plant seeds in well-prepared soil', category: 'planting', priority: 8, actionable: true },
  { text: 'Monitor soil moisture regularly', category: 'maintenance', priority: 7, actionable: true },
  { text: 'Harvest when crops are mature', category: 'harvest', priority: 6, actionable: true },
  { text: 'Follow recommended planting schedule', category: 'general', priority: 5, actionable: false },
]

describe('EnhancedManagementTips', () => {
  it('should render with default title', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    expect(screen.getByText('Management Tips')).toBeInTheDocument()
  })

  it('should render with custom title', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} title="Custom Tips" />)
    
    expect(screen.getByText('Custom Tips')).toBeInTheDocument()
  })

  it('should display total tips count', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    expect(screen.getByText('11 Total Tips')).toBeInTheDocument()
  })

  it('should render all categories', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    expect(screen.getByText('🌱 Planting Phase')).toBeInTheDocument()
    expect(screen.getByText('💧 Maintenance Phase')).toBeInTheDocument()
    expect(screen.getByText('🌾 Harvest Phase')).toBeInTheDocument()
    expect(screen.getByText('💡 General Tips')).toBeInTheDocument()
  })

  it('should show category tip counts', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    expect(screen.getByText('3 tips')).toBeInTheDocument() // planting
    expect(screen.getByText('4 tips')).toBeInTheDocument() // maintenance
    expect(screen.getByText('2 tips')).toBeInTheDocument() // harvest
    expect(screen.getByText('2 tips')).toBeInTheDocument() // general
  })

  it('should expand planting category by default', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    expect(screen.getByText('Plant seeds in well-prepared soil')).toBeInTheDocument()
    expect(screen.getByText('Use certified seeds for better yields')).toBeInTheDocument()
    expect(screen.getByText('Ensure proper spacing between plants')).toBeInTheDocument()
  })

  it('should expand category when clicked', async () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    const maintenanceHeader = screen.getByText('💧 Maintenance Phase')
    const expandButton = maintenanceHeader.closest('[class*="MuiCard"]')?.querySelector('button')
    
    if (expandButton) {
      fireEvent.click(expandButton)
      
      await waitFor(() => {
        expect(screen.getByText('Monitor soil moisture regularly')).toBeInTheDocument()
        expect(screen.getByText('Apply fertilizer at recommended rates')).toBeInTheDocument()
        expect(screen.getByText('Control weeds early in the season')).toBeInTheDocument()
        expect(screen.getByText('Monitor for pest and disease signs')).toBeInTheDocument()
      })
    }
  })

  it('should collapse category when clicked again', async () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} />)
    
    const maintenanceHeader = screen.getByText('💧 Maintenance Phase')
    const expandButton = maintenanceHeader.closest('[class*="MuiCard"]')?.querySelector('button')
    
    if (expandButton) {
      // Expand first
      fireEvent.click(expandButton)
      await waitFor(() => {
        expect(screen.getByText('Monitor soil moisture regularly')).toBeInTheDocument()
      })
      
      // Collapse
      fireEvent.click(expandButton)
      await waitFor(() => {
        expect(screen.queryByText('Monitor soil moisture regularly')).not.toBeInTheDocument()
      })
    }
  })

  it('should display priority chips when showPriority is true', () => {
    render(<EnhancedManagementTips tips={mockTipArray} showPriority={true} />)
    
    expect(screen.getByText('High Priority')).toBeInTheDocument()
    expect(screen.getByText('Medium Priority')).toBeInTheDocument()
  })

  it('should hide priority chips when showPriority is false', () => {
    render(<EnhancedManagementTips tips={mockTipArray} showPriority={false} />)
    
    expect(screen.queryByText('High Priority')).not.toBeInTheDocument()
    expect(screen.queryByText('Medium Priority')).not.toBeInTheDocument()
  })

  it('should display actionable tips with checkmark icon', () => {
    render(<EnhancedManagementTips tips={mockTipArray} />)
    
    // Check for actionable tips (priority >= 7)
    const actionableTips = screen.getAllByTestId('CheckCircleIcon')
    expect(actionableTips.length).toBeGreaterThan(0)
  })

  it('should display non-actionable tips with info icon', () => {
    render(<EnhancedManagementTips tips={mockTipArray} />)
    
    // Check for non-actionable tips
    const infoTips = screen.getAllByTestId('InfoIcon')
    expect(infoTips.length).toBeGreaterThan(0)
  })

  it('should limit tips per category when maxTipsPerCategory is set', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} maxTipsPerCategory={2} />)
    
    // Should show "more tips available" message
    expect(screen.getByText('+1 more tips available')).toBeInTheDocument() // maintenance has 4, showing 2
  })

  it('should call onTipClick when tip is clicked', () => {
    const onTipClick = jest.fn()
    render(<EnhancedManagementTips tips={mockCategorizedTips} onTipClick={onTipClick} />)
    
    const firstTip = screen.getByText('Plant seeds in well-prepared soil')
    fireEvent.click(firstTip)
    
    expect(onTipClick).toHaveBeenCalledWith('Plant seeds in well-prepared soil', 'planting')
  })

  it('should show no tips message when tips are empty', () => {
    render(<EnhancedManagementTips tips={{ planting: [], maintenance: [], harvest: [], general: [] }} />)
    
    expect(screen.getByText('No Management Tips Available')).toBeInTheDocument()
    expect(screen.getByText('Management tips will appear here when crop recommendations are loaded')).toBeInTheDocument()
  })

  it('should convert array format to categorized format', () => {
    render(<EnhancedManagementTips tips={mockTipArray} />)
    
    expect(screen.getByText('🌱 Planting Phase')).toBeInTheDocument()
    expect(screen.getByText('💧 Maintenance Phase')).toBeInTheDocument()
    expect(screen.getByText('🌾 Harvest Phase')).toBeInTheDocument()
    expect(screen.getByText('💡 General Tips')).toBeInTheDocument()
  })

  it('should hide icons when showIcons is false', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} showIcons={false} />)
    
    // Icons should not be visible in headers
    expect(screen.queryByTestId('AgricultureIcon')).not.toBeInTheDocument()
    expect(screen.queryByTestId('WaterDropIcon')).not.toBeInTheDocument()
  })

  it('should show icons when showIcons is true', () => {
    render(<EnhancedManagementTips tips={mockCategorizedTips} showIcons={true} />)
    
    // Icons should be visible in headers
    expect(screen.getByTestId('AgricultureIcon')).toBeInTheDocument()
    expect(screen.getByTestId('WaterDropIcon')).toBeInTheDocument()
  })

  it('should handle tips without category', () => {
    const tipsWithoutCategory = [
      { text: 'Plant seeds in well-prepared soil' }, // No category specified
    ]
    
    render(<EnhancedManagementTips tips={tipsWithoutCategory} />)
    
    // Should default to general category
    expect(screen.getByText('💡 General Tips')).toBeInTheDocument()
    expect(screen.getByText('Plant seeds in well-prepared soil')).toBeInTheDocument()
  })
})
