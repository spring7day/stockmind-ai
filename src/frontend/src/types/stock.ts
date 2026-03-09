// StockMind AI — 주식 관련 TypeScript 타입 정의

/** 종목 기본 정보 */
export interface Stock {
  ticker: string        // 종목코드 (예: 005930)
  name: string          // 종목명 (예: 삼성전자)
  market: 'KOSPI' | 'KOSDAQ' | 'NASDAQ' | 'NYSE'
  sector?: string       // 업종
  currency: 'KRW' | 'USD'
}

/** 실시간 주가 데이터 */
export interface StockPrice {
  ticker: string
  currentPrice: number   // 현재가
  openPrice: number      // 시가
  highPrice: number      // 고가
  lowPrice: number       // 저가
  closePrice: number     // 전일 종가
  change: number         // 전일 대비 (절대값)
  changePercent: number  // 전일 대비 (%)
  volume: number         // 거래량
  marketCap?: number     // 시가총액
  updatedAt: string      // 마지막 업데이트 시각 (ISO 8601)
}

/** 종목 요약 (카드 표시용) */
export interface StockSummary extends Stock, StockPrice {}

/** OHLCV 캔들 데이터 (차트용) */
export interface CandleData {
  time: string   // 날짜 (YYYY-MM-DD)
  open: number
  high: number
  low: number
  close: number
  volume: number
}

/** AI 분석 탭 종류 */
export type AnalysisTab = 'technical' | 'fundamental' | 'insights' | 'sentiment'

/** AI 분석 결과 */
export interface AnalysisResult {
  tab: AnalysisTab
  ticker: string
  summary: string          // AI 분석 요약
  score?: number           // 점수 (0-100)
  signals?: Signal[]       // 매매 시그널
  details: string          // 상세 분석 내용 (마크다운)
  generatedAt: string      // 분석 생성 시각
  disclaimer: string       // 법적 고지 문구
}

/** 매매 시그널 */
export interface Signal {
  type: 'BUY' | 'SELL' | 'HOLD' | 'WATCH'
  strength: 'STRONG' | 'MODERATE' | 'WEAK'
  reason: string
  indicator?: string   // 근거 지표 (RSI, MACD 등)
}

/** 뉴스/공시 아이템 */
export interface NewsItem {
  id: string
  title: string
  source: string        // 출처 (연합뉴스, 조선비즈 등)
  url: string
  publishedAt: string   // 발행 시각
  sentiment: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'  // 감성 분석 결과
  sentimentScore: number  // -1.0 ~ 1.0
  summary?: string      // AI 요약
}

/** 펀더멘털 데이터 */
export interface Fundamentals {
  ticker: string
  per?: number      // PER (주가수익비율)
  pbr?: number      // PBR (주가순자산비율)
  roe?: number      // ROE (자기자본이익률, %)
  eps?: number      // EPS (주당순이익)
  bps?: number      // BPS (주당순자산)
  dividendYield?: number  // 배당수익률 (%)
  revenueGrowth?: number  // 매출 성장률 (%)
  operatingMargin?: number  // 영업이익률 (%)
  debtToEquity?: number   // 부채비율
  fiscalYear?: number     // 기준 회계연도
}

/** 관심 종목 */
export interface WatchlistItem {
  ticker: string
  name: string
  market: Stock['market']
  addedAt: string  // 추가 날짜
  note?: string    // 사용자 메모
}

/** API 응답 공통 래퍼 */
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

/** 페이지네이션 */
export interface Pagination {
  page: number
  limit: number
  total: number
  hasNext: boolean
}

/** 검색 결과 */
export interface SearchResult {
  ticker: string
  name: string
  market: Stock['market']
  matchScore: number   // 검색 일치도
}

/** 광고 잠금 해제 상태 */
export interface AdGateStatus {
  ticker: string
  unlockedAt: string   // 잠금 해제 시각
  expiresAt: string    // 만료 시각 (당일 자정)
}
