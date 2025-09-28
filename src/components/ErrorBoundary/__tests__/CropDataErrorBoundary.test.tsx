import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import CropDataErrorBoundary from '../CropDataErrorBoundary'

// Mock component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

// Suppress console.error for these tests
const originalError = console.error
beforeAll(() => {
  console.error = jest.fn()
})

afterAll(() => {
  console.error = originalError
})

describe('CropDataErrorBoundary', () => {
  it('should render children when there is no error', () => {
    render(
      <CropDataErrorBoundary>
        <ThrowError shouldThrow={false} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('No error')).toBeInTheDocument()
  })

  it('should render error UI when child component throws', () => {
    render(
      <CropDataErrorBoundary>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('Data Processing Error')).toBeInTheDocument()
    expect(screen.getByText(/There was an error processing the crop data/)).toBeInTheDocument()
    expect(screen.getByText('Try Again')).toBeInTheDocument()
    expect(screen.getByText('Reload Page')).toBeInTheDocument()
  })

  it('should render custom fallback title and message', () => {
    render(
      <CropDataErrorBoundary
        fallbackTitle="Custom Error Title"
        fallbackMessage="Custom error message"
      >
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('Custom Error Title')).toBeInTheDocument()
    expect(screen.getByText('Custom error message')).toBeInTheDocument()
  })

  it('should call onRetry when Try Again button is clicked', () => {
    const mockRetry = jest.fn()
    
    render(
      <CropDataErrorBoundary onRetry={mockRetry}>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    fireEvent.click(screen.getByText('Try Again'))
    expect(mockRetry).toHaveBeenCalledTimes(1)
  })

  it('should reset error state when Try Again is clicked', () => {
    const { rerender } = render(
      <CropDataErrorBoundary>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('Data Processing Error')).toBeInTheDocument()

    fireEvent.click(screen.getByText('Try Again'))

    // Rerender with no error
    rerender(
      <CropDataErrorBoundary>
        <ThrowError shouldThrow={false} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('No error')).toBeInTheDocument()
  })

  it('should show error details when showDetails is true', () => {
    render(
      <CropDataErrorBoundary showDetails={true}>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    expect(screen.getByText('Error Details')).toBeInTheDocument()
    expect(screen.getByText('Test error')).toBeInTheDocument()
    expect(screen.getByText('Component Stack:')).toBeInTheDocument()
  })

  it('should not show error details when showDetails is false', () => {
    render(
      <CropDataErrorBoundary showDetails={false}>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    expect(screen.queryByText('Error Details')).not.toBeInTheDocument()
    expect(screen.queryByText('Component Stack:')).not.toBeInTheDocument()
  })

  it('should reload page when Reload Page button is clicked', () => {
    const mockReload = jest.fn()
    Object.defineProperty(window, 'location', {
      value: { reload: mockReload },
      writable: true
    })

    render(
      <CropDataErrorBoundary>
        <ThrowError shouldThrow={true} />
      </CropDataErrorBoundary>
    )

    fireEvent.click(screen.getByText('Reload Page'))
    expect(mockReload).toHaveBeenCalledTimes(1)
  })
})
