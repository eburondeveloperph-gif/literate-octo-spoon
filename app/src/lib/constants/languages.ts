/**
 * Supported languages for Qwen3-TTS
 * Based on: https://github.com/QwenLM/Qwen3-TTS
 *
 * Philippine languages added:
 * - tl: Tagalog/Filipino (national language of the Philippines)
 * - ilo: Ilocano (spoken in Northern Luzon, Philippines)
 */

export const SUPPORTED_LANGUAGES = {
  zh: 'Chinese',
  en: 'English',
  ja: 'Japanese',
  ko: 'Korean',
  de: 'German',
  fr: 'French',
  ru: 'Russian',
  pt: 'Portuguese',
  es: 'Spanish',
  it: 'Italian',
  tl: 'Tagalog/Filipino',
  ilo: 'Ilocano',
} as const;

export type LanguageCode = keyof typeof SUPPORTED_LANGUAGES;

export const LANGUAGE_CODES = Object.keys(SUPPORTED_LANGUAGES) as LanguageCode[];

export const LANGUAGE_OPTIONS = LANGUAGE_CODES.map((code) => ({
  value: code,
  label: SUPPORTED_LANGUAGES[code],
}));

/**
 * Philippine language codes for easy reference
 */
export const PHILIPPINE_LANGUAGES = ['tl', 'ilo'] as const;
export type PhilippineLanguageCode = (typeof PHILIPPINE_LANGUAGES)[number];
