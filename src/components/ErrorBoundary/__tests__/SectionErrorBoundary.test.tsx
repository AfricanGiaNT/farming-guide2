import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import SectionErrorBoundary from '../SectionErrorBoundary'

// Mock component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Section error')
  }
  return <div>Section content</div>
}

// Suppress console.error for these tests
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn()
})

afterAll(() => {
  console.error = originalError
})

describe('SectionErrorBoundary', () => {
  it('should render children when there is no error', () => {
    render(
      <SectionErrorBoundary sectionName="Test Section">
        <ThrowError shouldThrow={false} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText('Section content')).toBeInTheDocument()
  })

  it('should render error alert when child component throws', () => {
    render(
      <SectionErrorBoundary sectionName="Risk Assessment">
        <ThrowError shouldThrow={true} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText('Risk Assessment - Display Error')).toBeInTheDocument()
    expect(screen.getByText(/There was an error displaying the risk assessment section/)).toBeInTheDocument()
  })

  it('should render custom fallback message', () => {
    render(
      <SectionErrorBoundary 
        sectionName="Management Tips"
        fallbackMessage="Custom management tips error message"
      >
        <ThrowError shouldThrow={true} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText('Management Tips - Display Error')).toBeInTheDocument()
    expect(screen.getByText('Custom management tips error message')).toBeInTheDocument()
  })

  it('should handle different section names', () => {
    const { rerender } = render(
      <SectionErrorBoundary sectionName="Environmental Summary">
        <ThrowError shouldThrow={true} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText('Environmental Summary - Display Error')).toBeInTheDocument()

    rerender(
      <SectionErrorBoundary sectionName="AI-Enhanced Insights">
        <ThrowError shouldThrow={true} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText('AI-Enhanced Insights - Display Error')).toBeInTheDocument()
  })

  it('should use default fallback message when none provided', () => {
    render(
      <SectionErrorBoundary sectionName="Test Section">
        <ThrowError shouldThrow={true} />
      </SectionErrorBoundary>
    )

    expect(screen.getByText(/There was an error displaying the test section section/)).toBeInTheDocument()
  })
})
