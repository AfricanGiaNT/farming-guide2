import React, { useMemo } from 'react';
import { Box, Typography, Chip, Stack, Paper } from '@mui/material';
import { BugReport, LocalHospital } from '@mui/icons-material';

interface PestDiseaseManagementProps {
  pestManagement?: {
    items: string[];
    preview: string;
    count: number;
  } | string | string[] | null;
  diseaseManagement?: {
    items: string[];
    preview: string;
    count: number;
  } | string | string[] | null;
  compact?: boolean;
}

// Helper function to normalize data format
const normalizeManagementData = (data: any): { items: string[]; preview: string; count: number } => {
  if (!data) {
    return { items: [], preview: 'Not specified', count: 0 };
  }

  // Already formatted
  if (typeof data === 'object' && data !== null && 'items' in data && 'preview' in data && 'count' in data) {
    const count = data.count || 0;
    const preview = data.preview || 'Not specified';
    
    // Note: Sometimes items array arrives empty despite count > 0 due to JSON serialization
    // We handle this by reconstructing from preview below
    
    // Filter out empty, null, or invalid items - be very strict
    let items = [];
    if (Array.isArray(data.items)) {
      items = data.items
        .filter(item => {
          // Check if item exists and is a valid string
          if (!item) return false;
          if (typeof item !== 'string') return false;
          const trimmed = item.trim();
          return trimmed.length > 0 && trimmed !== 'undefined' && trimmed !== 'null';
        })
        .map(item => item.trim());
    }
    
    // Critical fix: If count > 0 but items array is empty/invalid, reconstruct from preview
    if (count > 0 && items.length === 0 && preview && preview !== 'Not specified') {
      return {
        items: [preview],
        preview: preview,
        count: 1
      };
    }
    
    // If we have valid items, use them
    if (items.length > 0) {
      return {
        items,
        preview: items[0],
        count: items.length
      };
    }
    
    // Final fallback: if we have a preview but no items, use the preview
    if (preview && preview !== 'Not specified') {
      return {
        items: [preview],
        preview: preview,
        count: 1
      };
    }
    
    return {
      items: [],
      preview: 'Not specified',
      count: 0
    };
  }

  // Array of strings
  if (Array.isArray(data)) {
    const items = data.filter(item => item && typeof item === 'string' && item.trim());
    return {
      items,
      preview: items[0] || 'Not specified',
      count: items.length
    };
  }

  // Plain string - parse it
  if (typeof data === 'string' && data.trim()) {
    const cleanData = data.trim().toLowerCase();
    if (cleanData === 'none' || cleanData === 'null' || cleanData === 'not specified' || cleanData === 'na' || cleanData === 'n/a') {
      return { items: [], preview: 'Not specified', count: 0 };
    }

    // Try to split by common delimiters
    let items: string[] = [];
    
    // Try newlines first
    if (data.includes('\n')) {
      items = data.split('\n').map(line => line.trim()).filter(line => line);
    }
    // Try bullet points or dashes
    else if (data.includes('•') || data.includes('- ')) {
      const delimiter = data.includes('•') ? '•' : '- ';
      items = data.split(delimiter).map(item => item.trim()).filter(item => item);
    }
    // Try semicolons
    else if (data.includes(';')) {
      items = data.split(';').map(item => item.trim()).filter(item => item);
    }
    // Try commas (but check if it's actually a list or just one long sentence)
    else if (data.includes(',')) {
      items = data.split(',').map(item => item.trim()).filter(item => item);
      // If we only got one item or items are very long, probably not meant to be split
      if (items.length === 1 || items.every(item => item.length > 150)) {
        items = [data.trim()];
      }
    }
    // Single item
    else {
      items = [data.trim()];
    }

    // Clean up items - remove empty and duplicates
    items = items
      .filter(item => item && item.length > 0)
      .filter((item, index, self) => self.indexOf(item) === index)
      .slice(0, 20); // Limit to 20 items max

    return {
      items,
      preview: items[0] || 'Not specified',
      count: items.length
    };
  }

  return { items: [], preview: 'Not specified', count: 0 };
};

const PestDiseaseManagement: React.FC<PestDiseaseManagementProps> = ({
  pestManagement,
  diseaseManagement,
  compact = false
}) => {
  // No internal expand state - always show content when not compact

  // Normalize the data
  const normalizedPest = useMemo(() => normalizeManagementData(pestManagement), [pestManagement]);
  const normalizedDisease = useMemo(() => normalizeManagementData(diseaseManagement), [diseaseManagement]);

  // Get preview text (one from each category)
  const getPreviewText = () => {
    const previews = [];
    if (normalizedPest.preview && normalizedPest.preview !== 'Not specified') {
      let pestText = normalizedPest.preview;
      // If preview is very short and we have multiple items, enhance it
      if (normalizedPest.count > 1 && normalizedPest.preview.length < 40) {
        pestText = `${normalizedPest.preview} (+${normalizedPest.count - 1} more)`;
      }
      previews.push(pestText);
    }
    if (normalizedDisease.preview && normalizedDisease.preview !== 'Not specified') {
      let diseaseText = normalizedDisease.preview;
      // If preview is very short and we have multiple items, enhance it
      if (normalizedDisease.count > 1 && normalizedDisease.preview.length < 40) {
        diseaseText = `${normalizedDisease.preview} (+${normalizedDisease.count - 1} more)`;
      }
      previews.push(diseaseText);
    }
    return previews.length > 0 ? previews.join(' • ') : 'Not specified';
  };

  const hasData = normalizedPest.count > 0 || normalizedDisease.count > 0;

  if (compact) {
    // For compact view, show only a very brief summary - just item count
    const totalItems = normalizedPest.count + normalizedDisease.count;
    let summaryText = 'Not specified';
    
    if (totalItems > 0) {
      const parts = [];
      if (normalizedPest.count > 0) {
        parts.push(`${normalizedPest.count} pest ${normalizedPest.count === 1 ? 'item' : 'items'}`);
      }
      if (normalizedDisease.count > 0) {
        parts.push(`${normalizedDisease.count} disease ${normalizedDisease.count === 1 ? 'item' : 'items'}`);
      }
      summaryText = parts.join(', ');
    }
    
    return (
      <Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
          Pest & Disease Management
        </Typography>
        <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
          {summaryText}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 600, mb: 2 }}>
        Pest & Disease Management
      </Typography>

      {/* Show preview text only if no detailed content */}
      {!hasData && (
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            fontStyle: 'italic',
            opacity: 0.7,
            mb: 2
          }}
        >
          {getPreviewText()}
        </Typography>
      )}

      {/* Expanded content - always shown when not compact and has data */}
      {hasData && (
        <Box sx={{ mt: 1 }}>
          {/* Pest Management Section */}
          {normalizedPest.count > 0 && normalizedPest.items.length > 0 && (
            <Paper 
              elevation={0} 
              sx={{ 
                mb: 3, 
                p: 2, 
                backgroundColor: 'warning.50',
                borderLeft: '3px solid',
                borderColor: 'warning.main'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <BugReport sx={{ mr: 1, color: 'warning.main', fontSize: '1.3rem' }} />
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'warning.dark' }}>
                  Pest Management {normalizedPest.count > 1 && `(${normalizedPest.count} items)`}
                </Typography>
              </Box>
              <Stack spacing={1.5}>
                {normalizedPest.items.slice(0, 6).map((item, index) => (
                  <Box
                    key={index}
                    sx={{
                      pl: 2,
                      borderLeft: '3px solid',
                      borderColor: 'warning.main',
                      py: 1,
                      borderRadius: '0 4px 4px 0',
                      backgroundColor: 'background.paper'
                    }}
                  >
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: 'text.primary',
                        lineHeight: 1.7,
                        fontSize: '0.9rem'
                      }}
                    >
                      {item}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Paper>
          )}

          {/* Disease Management Section */}
          {normalizedDisease.count > 0 && normalizedDisease.items.length > 0 && (
            <Paper 
              elevation={0} 
              sx={{ 
                mb: 2, 
                p: 2, 
                backgroundColor: 'error.50',
                borderLeft: '3px solid',
                borderColor: 'error.main'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                <LocalHospital sx={{ mr: 1, color: 'error.main', fontSize: '1.3rem' }} />
                <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'error.dark' }}>
                  Disease Management {normalizedDisease.count > 1 && `(${normalizedDisease.count} items)`}
                </Typography>
              </Box>
              <Stack spacing={1.5}>
                {normalizedDisease.items.slice(0, 6).map((item, index) => (
                  <Box
                    key={index}
                    sx={{
                      pl: 2,
                      borderLeft: '3px solid',
                      borderColor: 'error.main',
                      py: 1,
                      borderRadius: '0 4px 4px 0',
                      backgroundColor: 'background.paper'
                    }}
                  >
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: 'text.primary',
                        lineHeight: 1.7,
                        fontSize: '0.9rem'
                      }}
                    >
                      {item}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            </Paper>
          )}

          {/* No data message */}
          {normalizedPest.count === 0 && normalizedDisease.count === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
              No specific pest and disease management information available for this variety.
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default PestDiseaseManagement;
