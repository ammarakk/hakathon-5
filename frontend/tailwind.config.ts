import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fdf2f8',
          100: '#fce7f3',
          200: '#fbcfe8',
          300: '#f9a8d4',
          400: '#f472b6',
          500: '#ec4899',
          600: '#db2777',
          700: '#be185d',
          800: '#9d174d',
          900: '#831843',
        },
        gold: {
          50: '#fdf6e3',
          100: '#fbe9a7',
          200: '#f8dd71',
          300: '#f5d13b',
          400: '#f2c505',
          500: '#d4a803',
          600: '#a68202',
          700: '#785c02',
          800: '#4a3501',
          900: '#1c0e01',
        },
        wood: {
          50: '#faf5f1',
          100: '#f0e3d8',
          200: '#e6c7bf',
          300: '#dcb0a6',
          400: '#d2998d',
          500: '#b87f75',
          600: '#9f655d',
          700: '#854b45',
          800: '#6c312d',
          900: '#521815',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Playfair Display', 'serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
