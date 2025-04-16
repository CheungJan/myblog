// 这个文件是一个简单的代理，将请求转发到 Flask 应用
const { createProxyMiddleware } = require('http-proxy-middleware');
const express = require('express');
const serverless = require('serverless-http');

const app = express();

// 将所有请求代理到 Flask 应用
app.use('/', createProxyMiddleware({
  target: 'http://localhost:5000',
  changeOrigin: true,
}));

// 导出 serverless 函数
module.exports.handler = serverless(app);
