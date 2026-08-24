// CRACO's `style.postcss.plugins` shorthand generates postcss-loader v3's
// flat options shape ({ plugins: [...] }), but react-scripts 4 bundles
// postcss-loader v3, which only speaks PostCSS 7 - and Tailwind v3 requires
// PostCSS 8. Overriding postcss-loader to v4 (package.json "overrides")
// fixes the PostCSS version, but v4 expects a different, nested options
// shape ({ postcssOptions: { plugins: [...] } }), so patch the webpack
// config directly instead of relying on the CRACO shorthand.
module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      const oneOfRule = webpackConfig.module.rules.find((rule) => Array.isArray(rule.oneOf));
      if (oneOfRule) {
        oneOfRule.oneOf.forEach((rule) => {
          if (!Array.isArray(rule.use)) return;
          rule.use.forEach((useEntry) => {
            if (useEntry && useEntry.loader && useEntry.loader.includes('postcss-loader')) {
              useEntry.options = {
                postcssOptions: {
                  ident: 'postcss',
                  plugins: [require('tailwindcss'), require('autoprefixer')],
                },
              };
            }
          });
        });
      }
      return webpackConfig;
    },
  },
};
