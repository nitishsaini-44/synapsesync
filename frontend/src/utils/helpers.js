/**
 * utils/helpers.js
 * ─────────────────
 * Shared frontend utility functions.
 * Import from here instead of defining one-off helpers in individual components.
 */

/**
 * Strips basic HTML tags and collapses whitespace for display purposes.
 * This is a lightweight client-side version of the backend's clean_email_body().
 * Used by LeadDetailModal to render email body text safely.
 */
export function cleanMessageForDisplay(text) {
  if (!text) return '';
  return text
    .replace(/<[^>]+>/g, ' ')     // strip HTML tags
    .replace(/\s+/g, ' ')          // collapse whitespace
    .trim();
}

/**
 * Formats a UTC ISO date string to a human-readable local time string.
 * Example: "2024-01-15T10:30:00Z" → "Jan 15, 2024, 10:30 AM"
 */
export function formatDate(isoString) {
  if (!isoString) return '';
  try {
    return new Date(isoString).toLocaleString(undefined, {
      year:   'numeric',
      month:  'short',
      day:    'numeric',
      hour:   '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}
