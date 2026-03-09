// StockMind AI — 백엔드 API 클라이언트
// 백엔드: FastAPI (localhost:8000)

import type {
  StockSummary,
  StockPrice,
  CandleData,
  AnalysisResult,
  AnalysisTab,
  NewsItem,
  Fundamentals,
  SearchResult,
  WatchlistItem,
} from '@/types/stock'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
// 백엔드 URL이 명시적으로 설정되지 않으면 목 모드 사용 (Vercel 배포 시 기본값)
const MOCK_MODE = process.env.NEXT_PUBLIC_ENABLE_MOCK_DATA === 'true' || !process.env.NEXT_PUBLIC_API_URL

/** API 에러 클래스 */
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/** 백엔드 ApiResponse 래퍼 타입 { success, data } */
interface ApiResponse<T> {
  success: boolean
  data: T
}

/** 기본 fetch 래퍼 — 백엔드는 Pydantic 모델을 직접 반환 (래퍼 없음) */
async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${path}`

  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new ApiError(response.status, `API 오류: ${response.statusText}`)
  }

  return response.json() as Promise<T>
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 백엔드 응답 타입 (snake_case → 내부 매핑용)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface BackendStockPrice {
  current: number
  open: number
  high: number
  low: number
  prev_close: number
  change: number
  change_pct: number
  volume: number
  trading_value?: number
}

interface BackendStockInfo {
  ticker: string
  name: string
  market: string
  sector?: string
  price?: BackendStockPrice
  fundamentals?: {
    market_cap?: number
    per?: number
    pbr?: number
    eps?: number
    roe?: number
    debt_ratio?: number
    dividend_yield?: number
  }
}

interface BackendAnalysisResult {
  ticker: string
  name: string
  technical: {
    trend: string
    support_levels: number[]
    resistance_levels: number[]
    moving_averages: Record<string, number>
    rsi?: number
    volume_trend: string
    summary: string
    signals: string[]
  }
  fundamental: {
    valuation: string
    growth_potential: string
    financial_health: string
    peer_comparison: string
    summary: string
    risks: string[]
    opportunities: string[]
  }
  hidden_insights: {
    smart_money_flow: string
    unusual_activity: string[]
    dark_pool_signals: string
    seasonal_patterns?: string
    catalyst_events: string[]
    summary: string
  }
  sentiment: {
    overall_sentiment: string
    news_sentiment: string
    disclosure_sentiment: string
    retail_interest: string
    social_buzz?: string
    summary: string
  }
  overall_summary: string
  disclaimer: string
  analyzed_at: string
  cached: boolean
}

interface BackendNewsResponse {
  ticker: string
  name: string
  items: BackendNewsItem[]
  fetched_at: string
}

interface BackendNewsItem {
  id?: string
  title: string
  source: string
  url?: string
  published_at?: string
  publishedAt?: string
  summary?: string
  sentiment?: string
  sentimentScore?: number
  is_disclosure: boolean
  isDisclosure?: boolean
}

interface BackendSearchResponse {
  query: string
  results: Array<{
    ticker: string
    name: string
    market: string
    current_price?: number
    change_pct?: number
  }>
  total: number
}

/** /popular 응답 내 각 항목 — 백엔드 StockSummaryResponse (camelCase) */
interface BackendStockSummaryItem {
  ticker: string
  name: string
  market: string
  sector?: string
  currency?: string
  currentPrice?: number
  openPrice?: number
  highPrice?: number
  lowPrice?: number
  closePrice?: number
  change?: number
  changePercent?: number
  volume?: number
  marketCap?: number
  updatedAt?: string
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 목 데이터 (백엔드 연결 전 개발용)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const MOCK_POPULAR_STOCKS: StockSummary[] = [
  {
    ticker: '005930',
    name: '삼성전자',
    market: 'KOSPI',
    sector: '반도체',
    currency: 'KRW',
    currentPrice: 78500,
    openPrice: 78000,
    highPrice: 79200,
    lowPrice: 77800,
    closePrice: 77600,
    change: 900,
    changePercent: 1.16,
    volume: 15234567,
    marketCap: 468_000_000_000_000,
    updatedAt: new Date().toISOString(),
  },
  {
    ticker: '000660',
    name: 'SK하이닉스',
    market: 'KOSPI',
    sector: '반도체',
    currency: 'KRW',
    currentPrice: 198000,
    openPrice: 196000,
    highPrice: 199500,
    lowPrice: 195500,
    closePrice: 201000,
    change: -3000,
    changePercent: -1.49,
    volume: 3456789,
    marketCap: 143_000_000_000_000,
    updatedAt: new Date().toISOString(),
  },
  {
    ticker: '035420',
    name: 'NAVER',
    market: 'KOSPI',
    sector: 'IT서비스',
    currency: 'KRW',
    currentPrice: 185500,
    openPrice: 184000,
    highPrice: 186500,
    lowPrice: 183500,
    closePrice: 183000,
    change: 2500,
    changePercent: 1.37,
    volume: 987654,
    marketCap: 30_400_000_000_000,
    updatedAt: new Date().toISOString(),
  },
  {
    ticker: '035720',
    name: '카카오',
    market: 'KOSPI',
    sector: 'IT서비스',
    currency: 'KRW',
    currentPrice: 44350,
    openPrice: 44000,
    highPrice: 44700,
    lowPrice: 43800,
    closePrice: 45100,
    change: -750,
    changePercent: -1.66,
    volume: 2345678,
    marketCap: 19_700_000_000_000,
    updatedAt: new Date().toISOString(),
  },
  {
    ticker: '005380',
    name: '현대차',
    market: 'KOSPI',
    sector: '자동차',
    currency: 'KRW',
    currentPrice: 231000,
    openPrice: 230000,
    highPrice: 232500,
    lowPrice: 229000,
    closePrice: 229500,
    change: 1500,
    changePercent: 0.65,
    volume: 567890,
    marketCap: 49_200_000_000_000,
    updatedAt: new Date().toISOString(),
  },
  {
    ticker: '373220',
    name: 'LG에너지솔루션',
    market: 'KOSPI',
    sector: '2차전지',
    currency: 'KRW',
    currentPrice: 342000,
    openPrice: 340000,
    highPrice: 345000,
    lowPrice: 339000,
    closePrice: 338000,
    change: 4000,
    changePercent: 1.18,
    volume: 345678,
    marketCap: 80_100_000_000_000,
    updatedAt: new Date().toISOString(),
  },
]

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 응답 변환 헬퍼
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function mapBackendPriceToFrontend(ticker: string, name: string, price: BackendStockPrice): StockPrice {
  return {
    ticker,
    currentPrice: price.current,
    openPrice: price.open,
    highPrice: price.high,
    lowPrice: price.low,
    closePrice: price.prev_close,
    change: price.change,
    changePercent: price.change_pct,
    volume: price.volume,
    updatedAt: new Date().toISOString(),
  }
}

function mapBackendNewsItem(item: BackendNewsItem, index: number): NewsItem {
  const sentimentMap: Record<string, NewsItem['sentiment']> = {
    '긍정': 'POSITIVE',
    '부정': 'NEGATIVE',
    '중립': 'NEUTRAL',
    'positive': 'POSITIVE',
    'negative': 'NEGATIVE',
    'neutral': 'NEUTRAL',
  }
  return {
    // 백엔드가 UUID id를 반환하면 사용, 없으면 index 기반 fallback
    id: item.id || String(index + 1),
    title: item.title,
    source: item.source,
    url: item.url || '#',
    // publishedAt 우선, 없으면 published_at, 그 다음 현재 시각
    publishedAt: item.publishedAt || item.published_at || new Date().toISOString(),
    sentiment: (item.sentiment && sentimentMap[item.sentiment.toLowerCase()]) || 'NEUTRAL',
    // 백엔드 sentimentScore가 있으면 사용, 없으면 0
    sentimentScore: item.sentimentScore ?? 0,
    summary: item.summary,
  }
}

function mapBackendAnalysisToTab(result: BackendAnalysisResult, tab: AnalysisTab): AnalysisResult {
  const tabSections: Record<AnalysisTab, { summary: string; details: string }> = {
    technical: {
      summary: result.technical.summary,
      details: [
        `## 기술적 분석\n`,
        `**추세:** ${result.technical.trend}`,
        `**거래량 추세:** ${result.technical.volume_trend}`,
        result.technical.rsi != null ? `**RSI:** ${result.technical.rsi.toFixed(1)}` : '',
        result.technical.support_levels.length > 0
          ? `**지지선:** ${result.technical.support_levels.map(p => p.toLocaleString()).join(', ')}원`
          : '',
        result.technical.resistance_levels.length > 0
          ? `**저항선:** ${result.technical.resistance_levels.map(p => p.toLocaleString()).join(', ')}원`
          : '',
        `\n### AI 요약\n${result.technical.summary}`,
        result.technical.signals.length > 0
          ? `\n### 주요 신호\n${result.technical.signals.map(s => `- ${s}`).join('\n')}`
          : '',
        `\n> ⚠️ ${result.disclaimer}`,
      ].filter(Boolean).join('\n'),
    },
    fundamental: {
      summary: result.fundamental.summary,
      details: [
        `## 펀더멘털 분석\n`,
        `**밸류에이션:** ${result.fundamental.valuation}`,
        `**성장 가능성:** ${result.fundamental.growth_potential}`,
        `**재무 건전성:** ${result.fundamental.financial_health}`,
        `**동종업계 비교:** ${result.fundamental.peer_comparison}`,
        `\n### AI 요약\n${result.fundamental.summary}`,
        result.fundamental.risks.length > 0
          ? `\n### 리스크 요소\n${result.fundamental.risks.map(r => `- ${r}`).join('\n')}`
          : '',
        result.fundamental.opportunities.length > 0
          ? `\n### 기회 요소\n${result.fundamental.opportunities.map(o => `- ${o}`).join('\n')}`
          : '',
        `\n> ⚠️ ${result.disclaimer}`,
      ].filter(Boolean).join('\n'),
    },
    insights: {
      summary: result.hidden_insights.summary,
      details: [
        `## 숨겨진 인사이트\n`,
        `**스마트 머니 흐름:** ${result.hidden_insights.smart_money_flow}`,
        `**기관/외국인 시그널:** ${result.hidden_insights.dark_pool_signals}`,
        result.hidden_insights.seasonal_patterns
          ? `**계절적 패턴:** ${result.hidden_insights.seasonal_patterns}`
          : '',
        result.hidden_insights.unusual_activity.length > 0
          ? `\n### 이상 징후\n${result.hidden_insights.unusual_activity.map(a => `- ${a}`).join('\n')}`
          : '',
        result.hidden_insights.catalyst_events.length > 0
          ? `\n### 예상 촉매 이벤트\n${result.hidden_insights.catalyst_events.map(e => `- ${e}`).join('\n')}`
          : '',
        `\n### AI 요약\n${result.hidden_insights.summary}`,
        `\n> ⚠️ ${result.disclaimer}`,
      ].filter(Boolean).join('\n'),
    },
    sentiment: {
      summary: result.sentiment.summary,
      details: [
        `## 뉴스 센티먼트 분석\n`,
        `**전반적 심리:** ${result.sentiment.overall_sentiment}`,
        `**뉴스 센티먼트:** ${result.sentiment.news_sentiment}`,
        `**공시 센티먼트:** ${result.sentiment.disclosure_sentiment}`,
        `**개인투자자 관심도:** ${result.sentiment.retail_interest}`,
        result.sentiment.social_buzz ? `**소셜 화제도:** ${result.sentiment.social_buzz}` : '',
        `\n### AI 요약\n${result.sentiment.summary}`,
        `\n> ⚠️ ${result.disclaimer}`,
      ].filter(Boolean).join('\n'),
    },
  }

  return {
    tab,
    ticker: result.ticker,
    summary: tabSections[tab].summary,
    details: tabSections[tab].details,
    generatedAt: result.analyzed_at,
    disclaimer: result.disclaimer,
  }
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// API 함수들
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/** 인기 종목 목록 조회 */
export async function getPopularStocks(): Promise<StockSummary[]> {
  if (MOCK_MODE) return MOCK_POPULAR_STOCKS

  try {
    // 백엔드 /popular는 ApiResponse<StockSummaryResponse[]> 래퍼로 반환
    // StockSummaryResponse 필드는 camelCase (currentPrice, changePercent 등)
    const response = await fetchApi<ApiResponse<BackendStockSummaryItem[]>>('/api/stocks/popular')
    const items = response.data
    return items.map((item) => ({
      ticker: item.ticker,
      name: item.name,
      market: item.market as StockSummary['market'],
      sector: item.sector,
      currency: (item.currency || 'KRW') as 'KRW' | 'USD',
      currentPrice: item.currentPrice ?? 0,
      openPrice: item.openPrice ?? 0,
      highPrice: item.highPrice ?? 0,
      lowPrice: item.lowPrice ?? 0,
      closePrice: item.closePrice ?? 0,
      change: item.change ?? 0,
      changePercent: item.changePercent ?? 0,
      volume: item.volume ?? 0,
      marketCap: item.marketCap,
      updatedAt: item.updatedAt || new Date().toISOString(),
    }))
  } catch {
    return MOCK_POPULAR_STOCKS
  }
}

/** 종목 기본 정보 (이름, 시장) 조회 */
export async function getStockInfo(ticker: string): Promise<{ name: string; market: string; ticker: string }> {
  if (MOCK_MODE) {
    const found = MOCK_POPULAR_STOCKS.find((s) => s.ticker === ticker)
    if (found) return { name: found.name, market: found.market, ticker }
    return { name: ticker, market: 'KOSPI', ticker }
  }
  const info = await fetchApi<BackendStockInfo>(`/api/stocks/${ticker}`)
  return { name: info.name, market: info.market, ticker: info.ticker }
}

/** 종목 실시간 가격 조회 */
export async function getStockPrice(ticker: string): Promise<StockPrice> {
  if (MOCK_MODE) {
    const found = MOCK_POPULAR_STOCKS.find((s) => s.ticker === ticker)
    if (found) return found
    return {
      ticker,
      currentPrice: 50000,
      openPrice: 49500,
      highPrice: 50500,
      lowPrice: 49000,
      closePrice: 49800,
      change: 200,
      changePercent: 0.4,
      volume: 1000000,
      updatedAt: new Date().toISOString(),
    }
  }

  // /price 전용 엔드포인트 사용 — ApiResponse<StockPriceResponse> 래퍼로 반환
  // StockPriceResponse는 이미 camelCase 필드로 프론트엔드와 1:1 매핑
  const response = await fetchApi<ApiResponse<StockPrice>>(`/api/stocks/${ticker}/price`)
  return response.data
}

/** 종목 차트 데이터 조회 */
export async function getStockChart(
  ticker: string,
  period: '1D' | '1W' | '1M' | '3M' | '1Y' = '3M'
): Promise<CandleData[]> {
  if (MOCK_MODE) {
    return generateMockCandleData(ticker, period)
  }

  try {
    return await fetchApi<CandleData[]>(`/api/stocks/${ticker}/chart?period=${period}`)
  } catch {
    // 차트 엔드포인트 없으면 목 데이터 폴백
    return generateMockCandleData(ticker, period)
  }
}

/** AI 분석 결과 조회 */
export async function getAnalysis(
  ticker: string,
  tab: AnalysisTab
): Promise<AnalysisResult> {
  if (MOCK_MODE) {
    return generateMockAnalysis(ticker, tab)
  }

  const result = await fetchApi<BackendAnalysisResult>(`/api/stocks/${ticker}/analysis`)
  return mapBackendAnalysisToTab(result, tab)
}

/** 뉴스/공시 조회 */
export async function getNews(
  ticker: string,
  page = 1
): Promise<NewsItem[]> {
  if (MOCK_MODE) {
    return generateMockNews(ticker)
  }

  // 백엔드 /news는 ApiResponse<NewsResponse> 래퍼로 반환
  const response = await fetchApi<ApiResponse<BackendNewsResponse>>(`/api/stocks/${ticker}/news?page=${page}`)
  return response.data.items.map((item, i) => mapBackendNewsItem(item, i))
}

/** 종목 검색 */
export async function searchStocks(query: string): Promise<SearchResult[]> {
  if (!query.trim()) return []

  if (MOCK_MODE) {
    return MOCK_POPULAR_STOCKS
      .filter(
        (s) =>
          s.name.includes(query) ||
          s.ticker.includes(query)
      )
      .map((s) => ({
        ticker: s.ticker,
        name: s.name,
        market: s.market,
        matchScore: 1.0,
      }))
  }

  const data = await fetchApi<BackendSearchResponse>(`/api/stocks/search?q=${encodeURIComponent(query)}`)
  return data.results.map((r) => ({
    ticker: r.ticker,
    name: r.name,
    market: r.market as SearchResult['market'],
    matchScore: 1.0,
  }))
}

/** 관심 종목 조회 */
export async function getWatchlist(): Promise<WatchlistItem[]> {
  // 관심 종목은 localStorage에 저장 (서버리스 구현)
  if (typeof window === 'undefined') return []

  const stored = localStorage.getItem('stockmind_watchlist')
  if (!stored) return []

  try {
    return JSON.parse(stored) as WatchlistItem[]
  } catch {
    return []
  }
}

/** 관심 종목 추가 */
export async function addToWatchlist(stock: Omit<WatchlistItem, 'addedAt'>): Promise<void> {
  const current = await getWatchlist()
  const exists = current.find((s) => s.ticker === stock.ticker)
  if (exists) return

  const updated: WatchlistItem[] = [
    ...current,
    { ...stock, addedAt: new Date().toISOString() },
  ]
  localStorage.setItem('stockmind_watchlist', JSON.stringify(updated))
}

/** 관심 종목 제거 */
export async function removeFromWatchlist(ticker: string): Promise<void> {
  const current = await getWatchlist()
  const updated = current.filter((s) => s.ticker !== ticker)
  localStorage.setItem('stockmind_watchlist', JSON.stringify(updated))
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// 목 데이터 생성 헬퍼
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

function generateMockCandleData(ticker: string, period: string): CandleData[] {
  const days = period === '1D' ? 1 : period === '1W' ? 7 : period === '1M' ? 30 : period === '3M' ? 90 : 365
  const candles: CandleData[] = []
  let price = 70000 + (ticker.charCodeAt(0) % 10) * 5000
  const now = new Date()

  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)

    // 주말 제외
    if (date.getDay() === 0 || date.getDay() === 6) continue

    const change = (Math.random() - 0.48) * price * 0.03
    const open = price
    const close = price + change
    const high = Math.max(open, close) * (1 + Math.random() * 0.01)
    const low = Math.min(open, close) * (1 - Math.random() * 0.01)

    candles.push({
      time: date.toISOString().split('T')[0],
      open: Math.round(open),
      high: Math.round(high),
      low: Math.round(low),
      close: Math.round(close),
      volume: Math.round(1000000 + Math.random() * 5000000),
    })

    price = close
  }

  return candles
}

function generateMockAnalysis(ticker: string, tab: AnalysisTab): AnalysisResult {
  const tabNames: Record<AnalysisTab, string> = {
    technical: '기술적 분석',
    fundamental: '펀더멘털 분석',
    insights: '숨겨진 인사이트',
    sentiment: '뉴스 센티먼트',
  }

  return {
    tab,
    ticker,
    summary: `${ticker} 종목에 대한 ${tabNames[tab]} 결과입니다. AI가 다양한 데이터를 종합 분석하였습니다.`,
    score: Math.round(50 + Math.random() * 40),
    signals: [
      { type: 'BUY', strength: 'MODERATE', reason: 'RSI 과매도 구간 진입', indicator: 'RSI' },
      { type: 'WATCH', strength: 'WEAK', reason: 'MACD 골든크로스 임박', indicator: 'MACD' },
    ],
    details: `## ${tabNames[tab]}\n\n### 핵심 지표\n\n현재 기술적 지표들은 단기 반등 가능성을 시사하고 있습니다.\n\n- **RSI**: 38.5 (과매도 구간 접근)\n- **MACD**: -125, 시그널 라인과의 수렴 중\n- **볼린저 밴드**: 하단 밴드 근접\n\n### AI 종합 의견\n\n단기적으로 지지선인 75,000원 구간에서 반등이 예상됩니다. 다만 글로벌 반도체 업황 회복 여부를 지속 모니터링해야 합니다.\n\n> ⚠️ 본 분석은 참고 목적이며, 투자 권유가 아닙니다.`,
    generatedAt: new Date().toISOString(),
    disclaimer: '본 AI 분석은 투자 참고 자료이며, 투자 권유 또는 투자 조언이 아닙니다. 최종 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.',
  }
}

function generateMockNews(ticker: string): NewsItem[] {
  return [
    {
      id: '1',
      title: `${ticker} 3분기 실적 시장 예상 상회...영업이익 전년比 15% 증가`,
      source: '연합뉴스',
      url: '#',
      publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      sentiment: 'POSITIVE',
      sentimentScore: 0.72,
      summary: '3분기 영업이익이 시장 컨센서스를 15% 상회하며 어닝 서프라이즈를 기록했습니다.',
    },
    {
      id: '2',
      title: '글로벌 반도체 업황 회복 지연 우려...관련주 약세',
      source: '한국경제',
      url: '#',
      publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      sentiment: 'NEGATIVE',
      sentimentScore: -0.45,
      summary: '글로벌 수요 둔화 우려로 반도체 관련주가 약세를 보이고 있습니다.',
    },
    {
      id: '3',
      title: '외국인 기관 순매수 전환...수급 개선 기대감',
      source: '매일경제',
      url: '#',
      publishedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      sentiment: 'POSITIVE',
      sentimentScore: 0.38,
      summary: '외국인과 기관이 동반 순매수로 전환하면서 수급 개선 기대감이 높아지고 있습니다.',
    },
  ]
}
