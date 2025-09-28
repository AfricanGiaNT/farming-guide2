/**
 * Tests for ExpandableSection Component
 * Tests progressive disclosure functionality
 */

import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ExpandableSection from '../ExpandableSection'

describe('ExpandableSection', () => {
  const defaultProps = {
    title: 'Test Section',
    summary: 'This is a test summary',
    details: 'This is detailed information about the test section',
    category: 'important' as const,
  }

  it('should render with title and summary', () => {
    render(<ExpandableSection {...defaultProps} />)
    
    expect(screen.getByText('Test Section')).toBeInTheDocument()
    expect(screen.getByText('This is a test summary')).toBeInTheDocument()
  })

  it('should show expand/collapse button', () => {
    render(<ExpandableSection {...defaultProps} />)
    
    const expandButton = screen.getByRole('button')
    expect(expandButton).toBeInTheDocument()
  })

  it('should expand when clicked', async () => {
    render(<ExpandableSection {...defaultProps} />)
    
    const expandButton = screen.getByRole('button')
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByText('This is detailed information about the test section')).toBeInTheDocument()
    })
  })

  it('should collapse when clicked again', async () => {
    render(<ExpandableSection {...defaultProps} />)
    
    const expandButton = screen.getByRole('button')
    
    // Expand first
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.getByText('This is detailed information about the test section')).toBeInTheDocument()
    })
    
    // Collapse
    fireEvent.click(expandButton)
    await waitFor(() => {
      expect(screen.queryByText('This is detailed information about the test section')).not.toBeInTheDocument()
    })
  })

  it('should render with correct category styling', () => {
    render(<ExpandableSection {...defaultProps} category="critical" />)
    
    const section = screen.getByText('Test Section').closest('[class*="MuiCard"]')
    expect(section).toHaveStyle('background-color: rgba(244, 67, 54, 0.05)')
  })

  it('should display priority chip', () => {
    render(<ExpandableSection {...defaultProps} priority={8} />)
    
    expect(screen.getByText('High Priority')).toBeInTheDocument()
  })

  it('should display tooltip when provided', () => {
    render(<ExpandableSection {...defaultProps} tooltip="This is a helpful tooltip" />)
    
    const infoIcon = screen.getByTestId('InfoIcon')
    expect(infoIcon).toBeInTheDocument()
  })

  it('should render custom icon when provided', () => {
    const customIcon = <span data-testid="custom-icon">🌱</span>
    render(<ExpandableSection {...defaultProps} icon={customIcon} />)
    
    expect(screen.getByTestId('custom-icon')).toBeInTheDocument()
  })

  it('should render children when expanded', async () => {
    const children = <div data-testid="children-content">Additional content</div>
    render(
      <ExpandableSection {...defaultProps}>
        {children}
      </ExpandableSection>
    )
    
    const expandButton = screen.getByRole('button')
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      expect(screen.getByTestId('children-content')).toBeInTheDocument()
    })
  })

  it('should call onToggle callback when toggled', () => {
    const onToggle = jest.fn()
    render(<ExpandableSection {...defaultProps} onToggle={onToggle} />)
    
    const expandButton = screen.getByRole('button')
    fireEvent.click(expandButton)
    
    expect(onToggle).toHaveBeenCalledWith(true)
    
    fireEvent.click(expandButton)
    
    expect(onToggle).toHaveBeenCalledWith(false)
  })

  it('should start expanded when defaultExpanded is true', () => {
    render(<ExpandableSection {...defaultProps} defaultExpanded={true} />)
    
    expect(screen.getByText('This is detailed information about the test section')).toBeInTheDocument()
  })

  it('should render React node details', () => {
    const detailsNode = (
      <div>
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
      </div>
    )
    
    render(<ExpandableSection {...defaultProps} details={detailsNode} defaultExpanded={true} />)
    
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument()
    expect(screen.getByText('Paragraph 2')).toBeInTheDocument()
  })

  it('should handle long summary text with ellipsis', () => {
    const longSummary = 'This is a very long summary that should be truncated with ellipsis when not expanded to prevent the UI from becoming cluttered with too much text'
    
    render(<ExpandableSection {...defaultProps} summary={longSummary} />)
    
    const summaryElement = screen.getByText(longSummary)
    expect(summaryElement).toHaveStyle('-webkit-line-clamp: 2')
  })

  it('should show full summary when expanded', async () => {
    const longSummary = 'This is a very long summary that should be truncated with ellipsis when not expanded to prevent the UI from becoming cluttered with too much text'
    
    render(<ExpandableSection {...defaultProps} summary={longSummary} />)
    
    const expandButton = screen.getByRole('button')
    fireEvent.click(expandButton)
    
    await waitFor(() => {
      const summaryElement = screen.getByText(longSummary)
      expect(summaryElement).toHaveStyle('-webkit-line-clamp: none')
    })
  })
})
