// vue.config.js
const path = require('path');

module.exports = {
  configureWebpack: {
    resolve: {
      alias: {
        '@chessboardjs': path.resolve(__dirname, 'node_modules/chessboardjs/www/css'),
      },
    },
  },
};

