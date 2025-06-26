/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_KAKAO_APP_KEY: '2d22c7fa1d59eb77a5162a3948a0b6fe',
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
      'localhost',
    ],
  },
};

if (!process.env.NEXT_PUBLIC_API_URL) {
  throw new Error('NEXT_PUBLIC_API_URL is not defined');
}

console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);

module.exports = nextConfig;
