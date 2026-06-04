import type { NextApiRequest, NextApiResponse } from "next";
import httpProxy from "http-proxy";

export const config = {
  api: {
    bodyParser: false,
    externalResolver: true,
  },
};

const proxy = httpProxy.createProxyServer();

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const target = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  return new Promise<void>((resolve, reject) => {
    proxy.web(
      req,
      res,
      {
        target,
        changeOrigin: true,
      },
      (err) => {
        reject(err);
      }
    );

    proxy.once("proxyRes", () => {
      resolve();
    });
  });
}