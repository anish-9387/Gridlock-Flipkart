import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#FEF2ED',
          100: '#FDE1D2',
          200: '#FBBFA4',
          300: '#F8976E',
          400: '#F57547',
          500: '#E85D2A',
          600: '#D94A1F',
          700: '#B43818',
          800: '#912F1A',
          900: '#752A1A',
          950: '#40120B',
        },
        impact: {
          low: '#059669',
          medium: '#D97706',
          high: '#EA580C',
          critical: '#DC2626',
        },
        surface: {
          DEFAULT: '#F5F0EB',
          card: '#FFFFFF',
          sidebar: '#FAF7F2',
          hover: '#F0EBE5',
          subtle: '#FCFAF7',
          border: '#E7E2DC',
          'border-light': '#EDE9E4',
        },
        ink: {
          DEFAULT: '#1C1917',
          secondary: '#78716C',
          muted: '#A8A29E',
        },
      },
      boxShadow: {
        card: '0 1px 3px rgba(28,25,23,0.05), 0 1px 2px rgba(28,25,23,0.06)',
        'card-hover': '0 4px 14px rgba(28,25,23,0.08), 0 1px 4px rgba(28,25,23,0.04)',
        'card-lg': '0 8px 30px rgba(28,25,23,0.06), 0 2px 8px rgba(28,25,23,0.03)',
        sidebar: '1px 0 0 rgba(28,25,23,0.04)',
      },
      borderRadius: {
        card: '14px',
        button: '10px',
        input: '10px',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
