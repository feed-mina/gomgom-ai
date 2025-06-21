/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  reactStrictMode: true,
  compiler: {
    styledComponents: true,
  },
  images: {
    unoptimized: true,
    domains: [
      'example.com',
      'rev-static.yogiyo.co.kr',
    ],
  },
};

if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error('NEXT_PUBLIC_API_URL is not defined');
}

console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);

module.exports = nextConfig;
