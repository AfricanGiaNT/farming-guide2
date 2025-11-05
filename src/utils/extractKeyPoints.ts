/**
 * Utility function to extract key points from long text
 * Converts verbose production information into scannable bullet points
 */
export function extractKeyPoints(text: string | null | undefined, maxPoints: number = 5): string[] {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    return []
  }

  // First, detect if text has multiple "Label: content" patterns (like "Disease Management: ... Pest Management: ...")
  // Common labels in agricultural data
  const labelPattern = /(Disease Management|Pest Management|Drought Tolerance|General Notes|Production Notes|Land Preparation|Manure Application|Planting Information|Fertilizer Application|Weeding|Storing):/gi
  
  // Check if text has multiple labels
  const labels = text.match(labelPattern)
  
  if (labels && labels.length > 1) {
    // Split by label patterns (keeping the label with its content)
    const parts: string[] = []
    let lastIndex = 0
    
    // Find all label positions
    const labelMatches = [...text.matchAll(new RegExp(labelPattern.source, 'gi'))]
    
    for (let i = 0; i < labelMatches.length; i++) {
      const match = labelMatches[i]
      const startPos = match.index!
      const label = match[0]
      
      // Get content until next label or end
      const endPos = i < labelMatches.length - 1 ? labelMatches[i + 1].index! : text.length
      const content = text.substring(startPos, endPos).trim()
      
      if (content.length > 0) {
        // Clean up the content - remove the label if it appears multiple times
        let cleaned = content
        // Remove duplicate labels within the content
        cleaned = cleaned.replace(new RegExp(`^${label}\\s*`, 'i'), '')
        // Split by periods/semicolons if content is long
        if (cleaned.length > 100) {
          const subParts = cleaned.split(/[.;]/).map(p => p.trim()).filter(p => p.length > 15)
          subParts.forEach(part => {
            if (part.length > 0) {
              parts.push(`${label.trim()} ${part}`)
            }
          })
        } else {
          parts.push(`${label.trim()} ${cleaned}`)
        }
      }
    }
    
    if (parts.length > 0) {
      return parts.slice(0, maxPoints).map(p => {
        // Clean up and format
        let point = p.trim()
        // Remove duplicate colons
        point = point.replace(/:\s*:/g, ':')
        // Ensure proper ending
        if (!/[.!?]$/.test(point)) {
          point += '.'
        }
        return point
      })
    }
  }

  // If no multiple labels, proceed with normal extraction
  // First, try splitting by double newlines (paragraph breaks) - this is common in our data
  let paragraphs = text.split(/\n\n+/).map(p => p.trim()).filter(p => p.length > 20)
  
  // If no paragraphs, split by single newlines
  if (paragraphs.length === 0) {
    paragraphs = text.split(/\n/).map(p => p.trim()).filter(p => p.length > 20)
  }
  
  // Remove only EXACT duplicates or very high similarity (>90%) - keep paragraphs with unique details
  // This is important because paragraphs might have similar structure but different specific details (e.g., different pH ranges)
  if (paragraphs.length > 1) {
    const unique: string[] = []
    paragraphs.forEach(para => {
      // Check if this paragraph is substantially different from existing ones
      const isDuplicate = unique.some(existing => {
        // Check for exact match first
        if (para.toLowerCase().trim() === existing.toLowerCase().trim()) return true
        // Calculate similarity (simple word overlap)
        const paraWords = para.toLowerCase().split(/\s+/).filter(w => w.length > 3)
        const existingWords = existing.toLowerCase().split(/\s+/).filter(w => w.length > 3)
        if (paraWords.length === 0 || existingWords.length === 0) return false
        const commonWords = paraWords.filter(w => existingWords.includes(w))
        const similarity = commonWords.length / Math.max(paraWords.length, existingWords.length)
        // Only consider duplicates if >90% similar (very strict) to preserve unique details
        return similarity > 0.90
      })
      if (!isDuplicate) {
        unique.push(para)
      }
    })
    paragraphs = unique.length > 0 ? unique : paragraphs
  }
  
  // If still no paragraphs, split by sentences
  // Also look for key phrases that indicate important points (like "should be done", "include", "requires")
  if (paragraphs.length === 0) {
    // Split by sentences, but also look for transition phrases
    const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
    
    // Group sentences that start with key phrases together
    const grouped: string[] = []
    let currentGroup = ''
    
    sentences.forEach(sentence => {
      // Key phrases that start important points
      const keyPhrasePattern = /^(Plowing|Harrowing|Ridging|Soil|Field|Timing|Specific|Depth|pH|Preparation|Requirements|should|must|include|involves|The soil|Land preparation|Soil should|Fields should)/i
      
      if (keyPhrasePattern.test(sentence)) {
        // If we have a current group, save it
        if (currentGroup) {
          grouped.push(currentGroup.trim())
        }
        currentGroup = sentence
      } else if (currentGroup) {
        // Continue the current group if it's not too long
        if (currentGroup.length < 200) {
          currentGroup += '. ' + sentence
        } else {
          grouped.push(currentGroup.trim())
          currentGroup = sentence
        }
      } else {
        // Standalone sentence
        grouped.push(sentence)
      }
    })
    
    // Add the last group
    if (currentGroup) {
      grouped.push(currentGroup.trim())
    }
    
    if (grouped.length > 0) {
      paragraphs = grouped
    } else {
      paragraphs = sentences
    }
  }

  // Now process each paragraph/sentence
  const sentences: string[] = []
  paragraphs.forEach(para => {
    // If paragraph contains colons (like "Disease Management: ..."), split by colon but keep label
    if (para.includes(':')) {
      const colonIndex = para.indexOf(':')
      const label = para.substring(0, colonIndex).trim()
      const content = para.substring(colonIndex + 1).trim()
      
      if (content.length > 0) {
        // Split content by periods/semicolons to get individual points
        const contentParts = content.split(/[.;]/).map(p => p.trim()).filter(p => p.length > 10)
        if (contentParts.length > 0) {
          contentParts.forEach(part => {
            if (part.length > 0 && !part.toLowerCase().includes(label.toLowerCase())) {
              sentences.push(`${label}: ${part}`)
            }
          })
        } else {
          // If no splits, use the whole thing
          sentences.push(para)
        }
      } else {
        sentences.push(para)
      }
    } else {
      // Split paragraph into sentences - this is the most reliable method
      // Split by periods, exclamation marks, question marks
      const paraSentences = para.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 20)
      if (paraSentences.length > 0) {
        sentences.push(...paraSentences)
      } else {
        // If no sentence splits, try splitting by semicolons or commas in long paragraphs
        if (para.length > 150) {
          const semiParts = para.split(/[;]/).map(p => p.trim()).filter(p => p.length > 30)
          if (semiParts.length > 1) {
            sentences.push(...semiParts)
          } else {
            sentences.push(para)
          }
        } else {
          sentences.push(para)
        }
      }
    }
  })
  
  // Remove duplicate sentences (exact or very high similarity) - but preserve sentences with unique details
  const uniqueSentences: string[] = []
  sentences.forEach(sentence => {
    const isDuplicate = uniqueSentences.some(existing => {
      // Check for exact match
      if (sentence.toLowerCase().trim() === existing.toLowerCase().trim()) return true
      // Check for very high similarity (>90% word overlap) - strict threshold to preserve unique details
      const sentenceWords = sentence.toLowerCase().split(/\s+/).filter(w => w.length > 3)
      const existingWords = existing.toLowerCase().split(/\s+/).filter(w => w.length > 3)
      if (sentenceWords.length === 0 || existingWords.length === 0) return false
      const commonWords = sentenceWords.filter(w => existingWords.includes(w))
      const similarity = commonWords.length / Math.max(sentenceWords.length, existingWords.length)
      // Only consider duplicates if >90% similar (very strict) to preserve unique measurements/details
      return similarity > 0.90
    })
    if (!isDuplicate) {
      uniqueSentences.push(sentence)
    }
  })
  
  // Use unique sentences - this ensures we get all unique details even from similar paragraphs
  const finalSentences = uniqueSentences.length > 0 ? uniqueSentences : sentences

  // Filter out very short sentences, but keep at least some
  let validSentences = finalSentences.filter(s => s.length > 15)
  
  // If we filtered too many, lower the threshold
  if (validSentences.length === 0) {
    validSentences = finalSentences.filter(s => s.length > 10)
  }
  
  // If still nothing, use any sentences that are at least 5 chars
  if (validSentences.length === 0) {
    validSentences = finalSentences.filter(s => s.length > 5)
  }
  
  // If STILL nothing, try splitting paragraphs directly into sentences
  if (validSentences.length === 0 && paragraphs.length > 0) {
    // Split each paragraph into sentences
    paragraphs.forEach(para => {
      const paraSentences = para.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 20)
      if (paraSentences.length > 0) {
        validSentences.push(...paraSentences)
      }
    })
  }
  
  // Final fallback - split the original text any way we can
  if (validSentences.length === 0) {
    // Try splitting by periods, then by newlines, then by semicolons
    const fallback = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 20)
    if (fallback.length === 0) {
      const fallback2 = text.split(/\n+/).map(s => s.trim()).filter(s => s.length > 20)
      if (fallback2.length > 0) {
        validSentences = fallback2
      }
    } else {
      validSentences = fallback
    }
  }
  
  // ABSOLUTE last resort - return the text split by sentences (even if short)
  if (validSentences.length === 0) {
    const absoluteFallback = text.split(/[.!?\n]+/).map(s => s.trim()).filter(s => s.length > 10)
    if (absoluteFallback.length > 0) {
      validSentences = absoluteFallback
    } else {
      // If we STILL have nothing, return at least the first sentence/paragraph
      const firstPart = paragraphs.length > 0 ? paragraphs[0] : text.substring(0, 200)
      return [firstPart.length > 200 ? firstPart.substring(0, 197) + '...' : firstPart]
    }
  }

  // Extract key points - prioritize sentences with:
  // 1. Numbers/measurements (rates, quantities, temperatures, etc.)
  // 2. Time periods (weeks, months, days)
  // 3. Specific actions (should, must, recommend)
  // 4. Important keywords (application, timing, frequency, etc.)
  
  const keyPhrases = [
    /\d+\s*(kg|tons|hectare|ha|cm|m|°C|%|mm)/i, // Measurements
    /\d+\s*(weeks?|months?|days?|hours?)/i, // Time periods
    /(should|must|recommend|required|typically|usually|generally|ideally)/i, // Action words
    /(application|timing|frequency|rate|spacing|depth|moisture|temperature|humidity)/i, // Keywords
  ]

  // Score sentences based on key phrases
  const scoredSentences = validSentences.map((sentence, index) => {
    let score = 0
    let matchedPhrases: string[] = []

    keyPhrases.forEach((pattern, i) => {
      if (pattern.test(sentence)) {
        score += (i < 2 ? 3 : 1) // Measurements and time get higher scores
        matchedPhrases.push(pattern.toString())
      }
    })
    
    // Additional scoring for land preparation specific terms
    const landPrepTerms = /(plowing|harrowing|ridging|depth|soil|pH|field preparation|timing|aeration|drainage|moisture|organic matter)/gi
    const landPrepMatches = sentence.match(landPrepTerms)
    if (landPrepMatches) {
      score += landPrepMatches.length * 2 // Land prep terms are very important
    }
    
    // Bonus for sentences with specific measurements (cm, kg, tons, etc.)
    if (/\d+\s*(cm|kg|tons|ha|hectare|m|weeks|days|pH)/i.test(sentence)) {
      score += 2
    }

    // Bonus for first few sentences (usually most important)
    if (index < 3) score += 1
    
    // Bonus for sentences that contain action words (should, must, include, requires)
    if (/(should|must|include|requires|involves|recommended|ideally)/i.test(sentence)) {
      score += 1
    }

    return { sentence, score, index }
  })

  // Sort by score (highest first)
  scoredSentences.sort((a, b) => b.score - a.score)

  // For land preparation, we want MORE details, so increase limit if we have many scored sentences
  let limit = maxPoints
  if (maxPoints >= 8) {
    // For land preparation (8+ points requested), try to get more if available
    const highScoring = scoredSentences.filter(s => s.score > 2)
    if (highScoring.length > maxPoints) {
      limit = Math.min(maxPoints + 2, highScoring.length) // Add 2 more if we have high-scoring sentences
    }
  }
  
  // Take top sentences, but use the adjusted limit
  const topSentences = scoredSentences.slice(0, limit)

  // Sort back by original order for better flow
  topSentences.sort((a, b) => a.index - b.index)

  // Format as bullet points (remove leading/trailing whitespace, ensure proper capitalization)
  return topSentences.map(item => {
    let point = item.sentence.trim()
    // Capitalize first letter if not already
    if (point.length > 0 && point[0] !== point[0].toUpperCase()) {
      point = point[0].toUpperCase() + point.slice(1)
    }
    // Ensure it ends with punctuation
    if (!/[.!?]$/.test(point)) {
      point += '.'
    }
    return point
  })
}

/**
 * Extract a concise summary from text (first 2-3 sentences or up to 150 chars)
 */
export function extractSummary(text: string | null | undefined, maxLength: number = 150): string {
  if (!text || typeof text !== 'string' || text.trim().length === 0) {
    return ''
  }

  // Split by sentences
  const sentences = text.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0)
  
  if (sentences.length === 0) {
    return text.substring(0, maxLength) + (text.length > maxLength ? '...' : '')
  }

  // Take first 2 sentences, or first sentence if it's long enough
  let summary = sentences[0]
  if (sentences.length > 1 && summary.length < maxLength * 0.7) {
    summary += '. ' + sentences[1]
  }

  // Truncate if too long
  if (summary.length > maxLength) {
    summary = summary.substring(0, maxLength - 3) + '...'
  }

  return summary
}

