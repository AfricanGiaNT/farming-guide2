/**
 * Tests for InteractiveRiskAssessment Component
 * Tests interactive risk assessment functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import InteractiveRiskAssessment from '../InteractiveRiskAssessment'

const mockRisks = [
  {
    id: 'risk1',
    text: 'Heavy rainfall expected in the next 7 days',
    category: 'weather' as const,
    severity: 'high' as const,
    priority: 9,
    actionableAdvice: 'Prepare drainage systems',
    confidence: 0.9,
  },
  {
    id: 'risk2',
    text: 'Potential pest infestation',
    category: 'pest' as const,
    severity: 'medium' as const,
    priority: 6,
    actionableAdvice: 'Monitor crop health regularly',
    confidence: 0.7,
  },
  {
    id: 'risk3',
    text: 'Fungal disease risk',
    category: 'disease' as const,
    severity: 'low' as const,
    priority: 4,
    actionableAdvice: 'Apply preventive fungicide',
    confidence: 0.6,
  },
]

describe('InteractiveRiskAssessment', () => {
  it('should render risk assessment with title', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    expect(screen.getByText('Risk Assessment')).toBeInTheDocument()
  })

  it('should display risk statistics', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    expect(screen.getByText('1 High')).toBeInTheDocument()
    expect(screen.getByText('1 Medium')).toBeInTheDocument()
    expect(screen.getByText('1 Low')).toBeInTheDocument()
  })

  it('should render all risks by default', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    expect(screen.getByText('Heavy rainfall expected in the next 7 days')).toBeInTheDocument()
    expect(screen.getByText('Potential pest infestation')).toBeInTheDocument()
    expect(screen.getByText('Fungal disease risk')).toBeInTheDocument()
  })

  it('should filter risks by severity', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showFilters={true} />)
    
    const severitySelect = screen.getByLabelText('Severity')
    fireEvent.mouseDown(severitySelect)
    
    const highOption = screen.getByText('High Risk')
    fireEvent.click(highOption)
    
    await waitFor(() => {
      expect(screen.getByText('Heavy rainfall expected in the next 7 days')).toBeInTheDocument()
      expect(screen.queryByText('Potential pest infestation')).not.toBeInTheDocument()
      expect(screen.queryByText('Fungal disease risk')).not.toBeInTheDocument()
    })
  })

  it('should filter risks by category', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showFilters={true} />)
    
    const categorySelect = screen.getByLabelText('Category')
    fireEvent.mouseDown(categorySelect)
    
    const weatherOption = screen.getByText('Weather')
    fireEvent.click(weatherOption)
    
    await waitFor(() => {
      expect(screen.getByText('Heavy rainfall expected in the next 7 days')).toBeInTheDocument()
      expect(screen.queryByText('Potential pest infestation')).not.toBeInTheDocument()
      expect(screen.queryByText('Fungal disease risk')).not.toBeInTheDocument()
    })
  })

  it('should sort risks by priority by default', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    const riskElements = screen.getAllByText(/risk/)
    // Should be sorted by priority (high to low)
    expect(riskElements[0]).toHaveTextContent('Heavy rainfall')
    expect(riskElements[1]).toHaveTextContent('Potential pest')
    expect(riskElements[2]).toHaveTextContent('Fungal disease')
  })

  it('should sort risks by severity when selected', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showFilters={true} />)
    
    const sortSelect = screen.getByLabelText('Sort By')
    fireEvent.mouseDown(sortSelect)
    
    const severityOption = screen.getByText('Severity')
    fireEvent.click(severityOption)
    
    await waitFor(() => {
      const riskElements = screen.getAllByText(/risk/)
      // Should be sorted by severity (high to low)
      expect(riskElements[0]).toHaveTextContent('Heavy rainfall')
      expect(riskElements[1]).toHaveTextContent('Potential pest')
      expect(riskElements[2]).toHaveTextContent('Fungal disease')
    })
  })

  it('should clear filters when clear button is clicked', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showFilters={true} />)
    
    // Apply a filter
    const severitySelect = screen.getByLabelText('Severity')
    fireEvent.mouseDown(severitySelect)
    const highOption = screen.getByText('High Risk')
    fireEvent.click(highOption)
    
    // Clear filters
    const clearButton = screen.getByRole('button', { name: /clear/i })
    fireEvent.click(clearButton)
    
    await waitFor(() => {
      expect(screen.getByText('Heavy rainfall expected in the next 7 days')).toBeInTheDocument()
      expect(screen.getByText('Potential pest infestation')).toBeInTheDocument()
      expect(screen.getByText('Fungal disease risk')).toBeInTheDocument()
    })
  })

  it('should limit displayed risks when maxDisplayed is set', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} maxDisplayed={2} />)
    
    expect(screen.getByText('Heavy rainfall expected in the next 7 days')).toBeInTheDocument()
    expect(screen.getByText('Potential pest infestation')).toBeInTheDocument()
    expect(screen.queryByText('Fungal disease risk')).not.toBeInTheDocument()
    
    expect(screen.getByText('Showing 2 of 3 risks')).toBeInTheDocument()
  })

  it('should expand risk details when clicked', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    const firstRisk = screen.getByText('Heavy rainfall expected in the next 7 days')
    const expandButton = firstRisk.closest('[class*="MuiCard"]')?.querySelector('button')
    
    if (expandButton) {
      fireEvent.click(expandButton)
      
      await waitFor(() => {
        expect(screen.getByText('💡 Recommended Action:')).toBeInTheDocument()
        expect(screen.getByText('Prepare drainage systems')).toBeInTheDocument()
      })
    }
  })

  it('should display actionable advice when available', async () => {
    render(<InteractiveRiskAssessment risks={mockRisks} />)
    
    const firstRisk = screen.getByText('Heavy rainfall expected in the next 7 days')
    const expandButton = firstRisk.closest('[class*="MuiCard"]')?.querySelector('button')
    
    if (expandButton) {
      fireEvent.click(expandButton)
      
      await waitFor(() => {
        expect(screen.getByText('💡 Recommended Action:')).toBeInTheDocument()
        expect(screen.getByText('Prepare drainage systems')).toBeInTheDocument()
      })
    }
  })

  it('should show no risks message when risks array is empty', () => {
    render(<InteractiveRiskAssessment risks={[]} />)
    
    expect(screen.getByText('No Significant Risks Detected')).toBeInTheDocument()
    expect(screen.getByText('Current conditions appear favorable for crop cultivation')).toBeInTheDocument()
  })

  it('should hide filters when showFilters is false', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showFilters={false} />)
    
    expect(screen.queryByLabelText('Severity')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Category')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Sort By')).not.toBeInTheDocument()
  })

  it('should hide priority when showPriority is false', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} showPriority={false} />)
    
    // Priority chips should not be visible
    expect(screen.queryByText('High Priority')).not.toBeInTheDocument()
    expect(screen.queryByText('Medium Priority')).not.toBeInTheDocument()
    expect(screen.queryByText('Low Priority')).not.toBeInTheDocument()
  })

  it('should call onRiskSelect when risk is clicked', () => {
    const onRiskSelect = jest.fn()
    render(<InteractiveRiskAssessment risks={mockRisks} onRiskSelect={onRiskSelect} />)
    
    const firstRisk = screen.getByText('Heavy rainfall expected in the next 7 days')
    fireEvent.click(firstRisk)
    
    expect(onRiskSelect).toHaveBeenCalledWith(mockRisks[0])
  })

  it('should render with custom title', () => {
    render(<InteractiveRiskAssessment risks={mockRisks} title="Custom Risk Assessment" />)
    
    expect(screen.getByText('Custom Risk Assessment')).toBeInTheDocument()
  })
})
