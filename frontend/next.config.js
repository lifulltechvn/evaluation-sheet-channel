/** @type {import('next').NextConfig} */
module.exports = {
  output: "standalone",
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || "http://backend:8000";
    return [{ source: "/api/:path*", destination: `${backendUrl}/v1/:path*` }];
  },
};  
