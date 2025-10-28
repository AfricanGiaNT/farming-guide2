import React from 'react';
import { Box, Typography, Chip, Tooltip } from '@mui/material';
import { BugReport as BugIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';

interface DiseaseResistanceItem {
  name: string;
  icon?: string;
}

// Define known disease mappings with proper icons
const DISEASE_ICON_MAP: Record<string, string> = {
  'maize_streak_virus': '🦠',
  'northern_leaf_blight': '🍃',
  'gray_leaf_spot': '🍂',
  'rust': '🟤',
  'ear_rot': '🌽',
  'stalk_rot': '🪴',
  'downy_mildew': '💧',
  'fusarium': '🔬',
  'bacterial_blight': '🔬',
  'anthracnose': '🔴',
  'angular_leaf_spot': '◼️',
  'common_mosaic_virus': '🦠',
  'powdery_mildew': '⚪',
};

// Helper to convert disease name to display name
const formatDiseaseName = (name: string): string => {
  return name
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

// Helper to get the appropriate icon for a disease
const getDiseaseIcon = (diseaseName: string): string => {
  const normalizedName = diseaseName.toLowerCase().replace(/\s+/g, '_');
  return DISEASE_ICON_MAP[normalizedName] || '🛡️';
};

interface DiseaseResistanceDisplayProps {
  resistance: string[] | string | { items: string[], text: string, level: string };
  showIcons?: boolean;
  chipDisplay?: boolean;
  maxItems?: number;
}

const EnhancedDiseaseResistanceDisplay: React.FC<DiseaseResistanceDisplayProps> = ({
  resistance,
  showIcons = true,
  chipDisplay = false,
  maxItems = 3
}) => {
  // Handle the different formats the resistance data might come in
  let resistanceItems: string[] = [];
  let resistanceLevel: string = 'unknown';
  
  // Handle undefined or null
  if (!resistance) {
    resistanceItems = [];
    resistanceLevel = 'unknown';
  }
  // Handle arrays
  else if (Array.isArray(resistance)) {
    resistanceItems = resistance;
    resistanceLevel = resistance.length >= 3 ? 'high' : 
                      resistance.length >= 1 ? 'moderate' : 'low';
  } 
  // Handle strings
  else if (typeof resistance === 'string') {
    if (resistance.trim() === '') {
      resistanceItems = [];
    } else if (resistance.startsWith('[') && resistance.endsWith(']')) {
      try {
        resistanceItems = JSON.parse(resistance);
        // Ensure items are all strings
        resistanceItems = resistanceItems.map(item => String(item));
      } catch (e) {
        resistanceItems = [resistance];
      }
    } else {
      resistanceItems = [resistance];
    }
    resistanceLevel = 'unknown';
  } 
  // Handle our formatted object structure with items, text, level
  else if (resistance && typeof resistance === 'object' && 'items' in resistance) {
    resistanceItems = Array.isArray(resistance.items) ? resistance.items : [];
    resistanceLevel = typeof resistance.level === 'string' ? resistance.level : 'unknown';
  }
  // Handle any other object type (fallback)
  else if (typeof resistance === 'object') {
    try {
      resistanceItems = [JSON.stringify(resistance)];
    } catch(e) {
      resistanceItems = [];
    }
  }

  // Display message when no resistance data available
  if (resistanceItems.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary">
        No specific disease resistance information available
      </Typography>
    );
  }

  // Check if there are more items than we want to display
  const hasMoreItems = resistanceItems.length > maxItems;
  const displayItems = resistanceItems.slice(0, maxItems);
  const remainingCount = resistanceItems.length - maxItems;

  return (
    <>
      {chipDisplay ? (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
          {displayItems.map((disease, index) => (
            <Tooltip key={index} title={formatDiseaseName(disease)}>
              <Chip
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
              />
            </Tooltip>
          ))}
          {hasMoreItems && (
            <Tooltip title={`${remainingCount} more resistant diseases`}>
              <Chip
                label={`+${remainingCount}`}
                size="small"
                variant="outlined"
                color="default"
              />
            </Tooltip>
          )}
        </Box>
      ) : (
        <Box>
          {displayItems.map((disease, index) => (
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
          {hasMoreItems && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              And {remainingCount} more...
            </Typography>
          )}
        </Box>
      )}
    </>
  );
};

export default EnhancedDiseaseResistanceDisplay;
