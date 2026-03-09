// StockMind AI — 광고 잠금해제 상태 관리
// 당일 한 번 광고를 보면 해당 종목의 전체 분석이 잠금해제됩니다

import type { AdGateStatus } from '@/types/stock'

const STORAGE_PREFIX = 'adgate_'

/** 오늘 자정 (만료 시각) 계산 */
function getTodayMidnight(): Date {
  const midnight = new Date()
  midnight.setHours(23, 59, 59, 999)
  return midnight
}

/** localStorage 키 생성 */
function getKey(ticker: string): string {
  const today = new Date().toISOString().split('T')[0]  // YYYY-MM-DD
  return `${STORAGE_PREFIX}${ticker}_${today}`
}

/** 특정 종목의 잠금해제 여부 확인 */
export function isUnlocked(ticker: string): boolean {
  if (typeof window === 'undefined') return false

  const key = getKey(ticker)
  const stored = localStorage.getItem(key)

  if (!stored) return false

  try {
    const status: AdGateStatus = JSON.parse(stored)
    const now = new Date()
    const expiresAt = new Date(status.expiresAt)

    // 만료 시각이 지났으면 잠금 상태로 변경
    if (now > expiresAt) {
      localStorage.removeItem(key)
      return false
    }

    return true
  } catch {
    // 파싱 오류 시 잠금 처리
    localStorage.removeItem(key)
    return false
  }
}

/** 종목 잠금 해제 처리 */
export function unlockTicker(ticker: string): void {
  if (typeof window === 'undefined') return

  const key = getKey(ticker)
  const now = new Date()
  const expiresAt = getTodayMidnight()

  const status: AdGateStatus = {
    ticker,
    unlockedAt: now.toISOString(),
    expiresAt: expiresAt.toISOString(),
  }

  localStorage.setItem(key, JSON.stringify(status))
}

/** 잠금해제 상태 조회 */
export function getUnlockStatus(ticker: string): AdGateStatus | null {
  if (typeof window === 'undefined') return null

  const key = getKey(ticker)
  const stored = localStorage.getItem(key)

  if (!stored) return null

  try {
    return JSON.parse(stored) as AdGateStatus
  } catch {
    return null
  }
}

/** 모든 잠금해제 상태 초기화 (디버깅용) */
export function clearAllUnlocks(): void {
  if (typeof window === 'undefined') return

  const keys = Object.keys(localStorage).filter((k) => k.startsWith(STORAGE_PREFIX))
  keys.forEach((k) => localStorage.removeItem(k))
}

/** 오늘 잠금 해제된 종목 목록 */
export function getTodayUnlockedTickers(): string[] {
  if (typeof window === 'undefined') return []

  const today = new Date().toISOString().split('T')[0]
  const prefix = `${STORAGE_PREFIX}`

  return Object.keys(localStorage)
    .filter((k) => k.startsWith(prefix) && k.includes(`_${today}`))
    .map((k) => {
      // 키 형식: adgate_{ticker}_{YYYY-MM-DD}
      const withoutPrefix = k.slice(prefix.length)
      const dateIndex = withoutPrefix.lastIndexOf(`_${today}`)
      return withoutPrefix.slice(0, dateIndex)
    })
    .filter(Boolean)
}
