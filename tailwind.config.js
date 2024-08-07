/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.{py,html,js}'
  ],
  theme: {
    extend: {
      colors: {
        'custom-blue': '#16bdca',
        'disabled-blue': "#256266",
        'custom-gray': '#27282b',
        'custom-background': '#1A1A1E'
      },
      fontFamily: {
        bevan: ['Bevan', 'sans-serif'],
      },
    },
    plugins: [],
  }
}
