/**
 * Month ordering utilities for consistent chronological display
 */

export const MONTH_ORDER = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
] as const;

export const MONTH_SHORT_ORDER = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
] as const;

/**
 * Get months in chronological order from a monthly data object
 * @param monthlyData Object with month names as keys
 * @returns Array of month names in chronological order
 */
export function getSortedMonths(monthlyData: Record<string, any>): string[] {
  return MONTH_ORDER.filter(month => monthlyData[month]);
}

/**
 * Get months in chronological order with short names
 * @param monthlyData Object with month names as keys
 * @returns Array of short month names in chronological order
 */
export function getSortedShortMonths(monthlyData: Record<string, any>): string[] {
  return MONTH_SHORT_ORDER.filter(month => {
    const fullMonth = MONTH_ORDER[MONTH_SHORT_ORDER.indexOf(month)];
    return monthlyData[fullMonth];
  });
}

/**
 * Convert month name to its chronological index (0-11)
 * @param monthName Full month name
 * @returns Index of the month (0 = January, 11 = December)
 */
export function getMonthIndex(monthName: string): number {
  return MONTH_ORDER.indexOf(monthName as any);
}

/**
 * Sort an array of objects with month names by chronological order
 * @param items Array of objects containing month information
 * @param monthKey Key that contains the month name in each object
 * @returns Sorted array in chronological order
 */
export function sortByMonth<T extends Record<string, any>>(
  items: T[],
  monthKey: keyof T
): T[] {
  return items.sort((a, b) => {
    const monthA = getMonthIndex(String(a[monthKey]));
    const monthB = getMonthIndex(String(b[monthKey]));
    return monthA - monthB;
  });
}

/**
 * Get agricultural season for a given month
 * @param monthName Full month name
 * @returns Season classification
 */
export function getSeasonForMonth(monthName: string): 'wet' | 'dry' | 'transition' {
  const monthIndex = getMonthIndex(monthName);
  
  // Malawi seasons:
  // Wet season: November - March (indices 10, 11, 0, 1, 2)
  // Dry season: April - October (indices 3, 4, 5, 6, 7, 8, 9)
  
  if (monthIndex >= 10 || monthIndex <= 2) {
    return 'wet';
  } else {
    return 'dry';
  }
}

/**
 * Get color class for season-based styling
 * @param monthName Full month name
 * @returns Tailwind CSS color class
 */
export function getSeasonColor(monthName: string): string {
  const season = getSeasonForMonth(monthName);
  
  switch (season) {
    case 'wet':
      return 'bg-blue-50 border-blue-200 text-blue-800';
    case 'dry':
      return 'bg-orange-50 border-orange-200 text-orange-800';
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800';
  }
}
