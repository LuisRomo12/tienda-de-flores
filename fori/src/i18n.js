import { createI18n } from 'vue-i18n';

const messages = {
  es: {
    nav: {
      inicio: 'Inicio',
      catalogo: 'Catálogo',
      nosotros: 'Nosotros',
      contacto: 'Contacto'
    },
    prefs: {
      title: 'Preferencias',
      theme: 'Tema Visual',
      dark: 'Oscuro',
      light: 'Claro',
      language: 'Idioma',
      english: 'Inglés',
      spanish: 'Español',
      save: 'Guardar Preferencias',
      success: 'Preferencias actualizadas.',
      error: 'Hubo un error al actualizar.'
    }
  },
  en: {
    nav: {
      inicio: 'Home',
      catalogo: 'Catalog',
      nosotros: 'About',
      contacto: 'Contact'
    },
    prefs: {
      title: 'Preferences',
      theme: 'Visual Theme',
      dark: 'Dark',
      light: 'Light',
      language: 'Language',
      english: 'English',
      spanish: 'Spanish',
      save: 'Save Preferences',
      success: 'Preferences updated.',
      error: 'Error updating preferences.'
    }
  }
};

const i18n = createI18n({
  legacy: false, // Required for Composition API setup
  locale: 'es', // default locale
  fallbackLocale: 'en',
  messages
});

export default i18n;
