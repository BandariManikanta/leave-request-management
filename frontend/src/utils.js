export const REASON_MIN_LENGTH = 10;
export const REASON_MAX_LENGTH = 250;

// Local date as YYYY-MM-DD, matching the format of date inputs and the API.
export function todayIso() {
  const now = new Date();
  const localMidnight = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
  return localMidnight.toISOString().slice(0, 10);
}
