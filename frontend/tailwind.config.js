/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#D72660',
          hover: '#C11E54',
          light: '#FCE7EF',
        },
        surface: {
          bg: '#FAFAFA',
          card: '#FFFFFF',
        },
        border: '#EAEAEA',
        divider: '#F3F3F3',
        heading: '#111111',
        body: '#555555',
        muted: '#888888',
        success: {
          DEFAULT: '#3FA46A',
          light: '#EEFBF3',
        },
        warning: {
          DEFAULT: '#FFB547',
          light: '#FFF8EC',
        },
        error: {
          DEFAULT: '#F05656',
          light: '#FEF0F0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'card': '22px',
        'button': '14px',
        'input': '14px',
        'modal': '24px',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0,0,0,.03)',
        'card-hover': '0 4px 16px rgba(0,0,0,.06)',
        'modal': '0 20px 50px rgba(0,0,0,.08)',
        'input-focus': '0 0 0 4px rgba(215,38,96,.08)',
      },
      maxWidth: {
        'layout': '1600px',
      },
      letterSpacing: {
        'tight-custom': '-0.01em',
      },
    },
  },
  plugins: [],
}
