const path = require('path');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Add the alias configuration
      webpackConfig.resolve.alias = {
        ...webpackConfig.resolve.alias,
        '@': path.resolve(__dirname, 'src'),
      };
      return webpackConfig;
    },
  },
}; 