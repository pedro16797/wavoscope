import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

const isDev = window.location.origin.includes(':5173') || window.location.origin.includes(':5174');
const backendUrl = isDev ? 'http://127.0.0.1:8000' : '';

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false,
    },
    backend: {
      loadPath: `${backendUrl}/locales/{{lng}}.json`,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
