#!/usr/bin/env node
// Read the build log of a Dokploy application deployment (latest, or a given deploymentId).
// Usage (run in the project dir): DOKPLOY_ENV=dev node deployment_log.mjs [deploymentId]
// Config: .dokploy.<env>.env + .env (DOKPLOY_URL, DOKPLOY_API_KEY, DOKPLOY_APP_ID). REST has no log API; uses the /listen-deployment WebSocket.
// REST 没有日志接口，这里复用 Dokploy 控制台使用的 /listen-deployment WebSocket。
import { readFileSync } from "node:fs";

function loadEnv(path) {
  try {
    for (const line of readFileSync(path, "utf8").split("\n")) {
      const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
      if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].trim();
    }
  } catch {}
}
loadEnv(`.dokploy.${process.env.DOKPLOY_ENV ?? "dev"}.env`);
loadEnv(".env");
const { DOKPLOY_URL: url, DOKPLOY_API_KEY: key, DOKPLOY_APP_ID: app } = process.env;
if (!url || !key || !app) throw new Error("缺少 DOKPLOY_URL / DOKPLOY_API_KEY / DOKPLOY_APP_ID");

const headers = { "x-api-key": key };
const list = await (await fetch(`${url}/api/deployment.all?applicationId=${app}`, { headers })).json();
const wanted = process.argv[2];
const dep = wanted ? list.find((d) => d.deploymentId === wanted) : list[0];
if (!dep) throw new Error("未找到部署记录");
console.error(`deployment ${dep.deploymentId} status=${dep.status} created=${dep.createdAt}`);

const params = new URLSearchParams({ logPath: dep.logPath });
const serverId = dep.buildServerId ?? dep.serverId;
if (serverId) params.set("serverId", serverId);
const ws = new WebSocket(`${url.replace(/^http/, "ws")}/listen-deployment?${params}`, { headers });
ws.onmessage = (e) => process.stdout.write(String(e.data));
ws.onclose = () => process.exit(0);
ws.onerror = () => { console.error("WebSocket 连接失败"); process.exit(1); };
setTimeout(() => process.exit(0), 10000);
