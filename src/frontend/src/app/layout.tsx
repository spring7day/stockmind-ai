// 루트 레이아웃 — 헤더/푸터 포함 전체 앱 레이아웃

import type { Metadata } from 'next'
import Header from '@/components/layout/Header'
import Footer from '@/components/layout/Footer'
import './globals.css'

export const metadata: Metadata = {
  title: {
    default: 'StockMind AI — AI 기반 주식 심층 분석',
    template: '%s | StockMind AI',
  },
  description:
    'AI가 분석하는 한국 주식 심층 리포트. 기술적 분석, 펀더멘털, 숨겨진 인사이트, 뉴스 센티먼트를 한 곳에서.',
  keywords: ['주식', 'AI 분석', '주식 분석', '코스피', '코스닥', '주식 추천', '기술적 분석'],
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    siteName: 'StockMind AI',
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko" className="dark">
      <head>
        {/* Pretendard 웹폰트 */}
        <link
          rel="preconnect"
          href="https://cdn.jsdelivr.net"
          crossOrigin="anonymous"
        />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css"
        />
      </head>
      <body className="min-h-screen flex flex-col bg-background text-text-primary">
        {/* 상단 헤더 */}
        <Header />

        {/* 메인 콘텐츠 (헤더 높이 오프셋) */}
        <main className="flex-1 pt-16">
          {children}
        </main>

        {/* 하단 푸터 */}
        <Footer />
      </body>
    </html>
  )
}
