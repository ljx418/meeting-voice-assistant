"use strict";

const proxyUrl =
  process.env.STITCH_MCP_PROXY_URL ||
  process.env.HTTPS_PROXY ||
  process.env.HTTP_PROXY ||
  process.env.ALL_PROXY;

if (proxyUrl) {
  const undiciPath =
    process.env.STITCH_MCP_UNDICI_PATH ||
    "/Users/Zhuanz/.npm/_npx/829c6278c197c365/node_modules/undici";
  const { ProxyAgent, setGlobalDispatcher } = require(undiciPath);
  setGlobalDispatcher(new ProxyAgent(proxyUrl));
}
