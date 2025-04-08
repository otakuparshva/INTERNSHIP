import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      return {
        ...webpackConfig,
        resolve: {
          ...webpackConfig.resolve,
          alias: {
            ...webpackConfig.resolve.alias,
            '@': path.resolve(__dirname, 'src'),
          },
        },
      };
    },
  },
}; 