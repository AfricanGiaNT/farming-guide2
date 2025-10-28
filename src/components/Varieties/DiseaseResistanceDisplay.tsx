import React from 'react';
import { Box, Typography, Chip, Stack } from '@mui/material';
import { BugReport as BugIcon } from '@mui/icons-material';

// Define known disease mappings with proper icons and human-readable names
const DISEASE_DISPLAY_MAP: Record<string, {icon: string, displayName: string}> = {
  'maize_streak_virus': { icon: '🦠', displayName: 'Maize Streak Virus' },
  'northern_leaf_blight': { icon: '🍃', displayName: 'Northern Leaf Blight' },
  'gray_leaf_spot': { icon: '🍂', displayName: 'Gray Leaf Spot' },
  'rust': { icon: '🟤', displayName: 'Rust' },
  'ear_rot': { icon: '🌽', displayName: 'Ear Rot' },
  'stalk_rot': { icon: '🪴', displayName: 'Stalk Rot' },
  'downy_mildew': { icon: '💧', displayName: 'Downy Mildew' },
  'fusarium': { icon: '🔬', displayName: 'Fusarium' },
  'bacterial_blight': { icon: '🔬', displayName: 'Bacterial Blight' },
  'anthracnose': { icon: '🔴', displayName: 'Anthracnose' },
  'angular_leaf_spot': { icon: '◼️', displayName: 'Angular Leaf Spot' },
  'common_mosaic_virus': { icon: '🦠', displayName: 'Common Mosaic Virus' },
  'powdery_mildew': { icon: '⚪', displayName: 'Powdery Mildew' },
};

// Helper to convert disease name to display name
const formatDiseaseName = (name: string): string => {
  const normalized = name.toLowerCase().replace(/[\[\]"']/g, '').trim();
  
  if (DISEASE_DISPLAY_MAP[normalized]) {
    return DISEASE_DISPLAY_MAP[normalized].displayName;
  }
  
  // If not in our map, format as title case
  return normalized
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper to get icon for disease
const getDiseaseIcon = (name: string): string => {
  const normalized = name.toLowerCase().replace(/[\[\]"']/g, '').trim();
  return DISEASE_DISPLAY_MAP[normalized]?.icon || '🛡️';
};

// Parse disease resistance data
const parseDiseaseResistance = (resistance: any): string[] => {
  if (!resistance) return [];
  
  // Handle nested structure - if the data is inside a 'resistance' property
  if (typeof resistance === 'object' && resistance !== null && 'resistance' in resistance) {
    console.log('🔍 parseDiseaseResistance - Found nested structure, unwrapping:', resistance);
    return parseDiseaseResistance(resistance.resistance);
  }
  
  // Handle empty objects - they might be serialized incorrectly
  if (typeof resistance === 'object' && resistance !== null && Object.keys(resistance).length === 0) {
    console.log('🔍 parseDiseaseResistance - Received empty object, returning empty array');
    return [];
  }
  
  console.log('🔍 parseDiseaseResistance - Input:', {
    resistance,
    type: typeof resistance,
    isArray: Array.isArray(resistance),
    isObject: typeof resistance === 'object' && resistance !== null
  });
  
  if (typeof resistance === 'string') {
    // Try to parse as JSON if it looks like an array string
    if (resistance.trim().startsWith('[') && resistance.trim().endsWith(']')) {
      try {
        return JSON.parse(resistance);
      } catch (e) {
        // If parse fails, treat as a single disease
        return [resistance];
      }
    } 
    
    // Check for comma-separated list
    if (resistance.includes(',')) {
      return resistance.split(',').map(item => item.trim());
    }
    
    // Single disease name
    return [resistance];
  }
  
  // Object with items property
  if (typeof resistance === 'object' && resistance !== null) {
    if (Array.isArray(resistance)) {
      console.log('🔍 parseDiseaseResistance - Returning array:', resistance);
      return resistance;
    }
    if ('items' in resistance && Array.isArray(resistance.items)) {
      console.log('🔍 parseDiseaseResistance - Returning items array:', resistance.items);
      return resistance.items;
    }
    // If it has a text property but no items, return empty (or try to parse text)
    if ('text' in resistance && !('items' in resistance)) {
      console.log('🔍 parseDiseaseResistance - Has text but no items, trying to parse text:', resistance.text);
      // Try to parse the text as JSON or split by comma
      const textValue = resistance.text || '';
      if (typeof textValue === 'string') {
        if (textValue.trim().startsWith('[') && textValue.trim().endsWith(']')) {
          try {
            return JSON.parse(textValue);
          } catch (e) {
            // Fall through to splitting
          }
        }
        if (textValue.includes(',')) {
          return textValue.split(',').map(item => item.trim()).filter(Boolean);
        }
        if (textValue.trim() !== '') {
          return [textValue];
        }
      }
      return [];
    }
  }
  
  console.log('🔍 parseDiseaseResistance - No match, returning empty array');
  return [];
};

interface DiseaseResistanceDisplayProps {
  resistance: any;
  variant?: 'compact' | 'chips' | 'list';
  showIcons?: boolean;
  title?: string;
  maxItems?: number;
}

const DiseaseResistanceDisplay: React.FC<DiseaseResistanceDisplayProps> = ({
  resistance,
  variant = 'compact',
  showIcons = true,
  title = 'Common diseases',
  maxItems = 3
}) => {
  const diseases = parseDiseaseResistance(resistance);
  
  if (diseases.length === 0) {
    // Return a span instead of Box to avoid nesting issues with Typography
    return (
      <span>
        {title && (
          <>
            <Typography component="span" variant="caption" color="text.secondary" display="block" gutterBottom>
              {title}
            </Typography>
            <br />
          </>
        )}
        <Typography component="span" variant="body2" color="text.secondary">
          No specific resistance data
        </Typography>
      </span>
    );
  }
  
  const hasMore = diseases.length > maxItems;
  const displayDiseases = diseases.slice(0, maxItems);
  
  // Compact display (for overview cards)
  if (variant === 'compact') {
    return (
      <Box>
        {title && (
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            {title}
          </Typography>
        )}
        <Stack direction="row" spacing={0.5} flexWrap="wrap" alignItems="center">
          {displayDiseases.map((disease, index) => (
            <Box key={index} sx={{ display: 'inline-flex', alignItems: 'center', mr: 1 }}>
              {showIcons && <span style={{ marginRight: '4px' }}>{getDiseaseIcon(disease)}</span>}
              <Typography variant="body2" component="span">
                {formatDiseaseName(disease)}
              </Typography>
              {index < displayDiseases.length - 1 && <span style={{ marginLeft: '4px' }}>,</span>}
            </Box>
          ))}
          {hasMore && (
            <Typography variant="body2" color="text.secondary" component="span">
              +{diseases.length - maxItems} more
            </Typography>
          )}
        </Stack>
      </Box>
    );
  }
  
  // Chip display (for detail views)
  if (variant === 'chips') {
    return (
      <Box>
        {title && (
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            {title}
          </Typography>
        )}
        <Stack direction="row" spacing={0.5} flexWrap="wrap">
          {displayDiseases.map((disease, index) => (
            <Chip 
              key={index}
              icon={showIcons ? <BugIcon fontSize="small" /> : undefined}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {showIcons && <span>{getDiseaseIcon(disease)}</span>}
                  <span>{formatDiseaseName(disease)}</span>
                </Box>
              }
              size="small"
              variant="outlined"
              color="warning"
              sx={{ mb: 0.5 }}
            />
          ))}
          {hasMore && (
            <Chip 
              label={`+${diseases.length - maxItems} more`}
              size="small" 
              variant="outlined" 
              color="default"
              sx={{ mb: 0.5 }}
            />
          )}
        </Stack>
      </Box>
    );
  }
  
  // List display (for detail views)
  return (
    <Box>
      {title && (
        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          {title}
        </Typography>
      )}
      <Stack direction="column" spacing={0.5}>
        {displayDiseases.map((disease, index) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            {showIcons && (
              <Box component="span" sx={{ mr: 1, display: 'inline-flex' }}>
                {getDiseaseIcon(disease)}
              </Box>
            )}
            <Typography variant="body2">
              {formatDiseaseName(disease)}
            </Typography>
          </Box>
        ))}
        {hasMore && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            And {diseases.length - maxItems} more...
          </Typography>
        )}
      </Stack>
    </Box>
  );
};

export default DiseaseResistanceDisplay;

