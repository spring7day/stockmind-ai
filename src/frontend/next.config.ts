import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Docker 컨테이너에서 standalone 빌드 사용
  output: 'standalone',
  // 백엔드 API 프록시 설정
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ]
  },
  // 이미지 최적화 설정
  images: {
    domains: ['localhost'],
  },
}

export default nextConfig
