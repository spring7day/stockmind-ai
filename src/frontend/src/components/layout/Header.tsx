'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { searchStocks } from '@/lib/api'
import type { SearchResult } from '@/types/stock'

export default function Header() {
  const router = useRouter()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // 검색어 변경 시 API 호출 (디바운스 300ms)
  const handleSearchChange = useCallback((value: string) => {
    setQuery(value)

    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (!value.trim()) {
      setResults([])
      setShowDropdown(false)
      return
    }

    debounceRef.current = setTimeout(async () => {
      setIsSearching(true)
      try {
        const data = await searchStocks(value)
        setResults(data)
        setShowDropdown(data.length > 0)
      } catch {
        setResults([])
      } finally {
        setIsSearching(false)
      }
    }, 300)
  }, [])

  // 종목 선택
  const handleSelect = useCallback(
    (ticker: string) => {
      setQuery('')
      setResults([])
      setShowDropdown(false)
      router.push(`/stock/${ticker}`)
    },
    [router]
  )

  // 엔터키로 검색
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && results.length > 0) {
        handleSelect(results[0].ticker)
      }
      if (e.key === 'Escape') {
        setShowDropdown(false)
      }
    },
    [results, handleSelect]
  )

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background border-b border-border h-16">
      <div className="max-w-7xl mx-auto px-4 h-full flex items-center gap-4">
        {/* 로고 */}
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <Image
            src="/logo.svg"
            alt="StockMind AI"
            width={28}
            height={28}
            className="text-primary"
          />
          <span className="font-bold text-lg text-text-primary hidden sm:block">
            StockMind<span className="text-primary"> AI</span>
          </span>
        </Link>

        {/* 검색창 */}
        <div ref={searchRef} className="flex-1 max-w-xl relative">
          <div className="relative">
            {/* 검색 아이콘 */}
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>

            <input
              type="text"
              value={query}
              onChange={(e) => handleSearchChange(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => results.length > 0 && setShowDropdown(true)}
              placeholder="종목명 또는 종목코드 검색"
              className="w-full bg-card border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary transition-colors"
            />

            {/* 로딩 스피너 */}
            {isSearching && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>

          {/* 검색 드롭다운 */}
          {showDropdown && results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-xl overflow-hidden z-50 animate-fade-in">
              {results.map((result) => (
                <button
                  key={result.ticker}
                  onClick={() => handleSelect(result.ticker)}
                  className="w-full flex items-center justify-between px-4 py-3 hover:bg-surface transition-colors text-left"
                >
                  <div>
                    <span className="text-sm font-medium text-text-primary">
                      {result.name}
                    </span>
                    <span className="ml-2 text-xs text-text-muted">{result.ticker}</span>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded bg-border text-text-secondary">
                    {result.market}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* 네비게이션 */}
        <nav className="flex items-center gap-1 shrink-0">
          <Link
            href="/watchlist"
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-card transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
              />
            </svg>
            <span className="hidden md:block">관심 종목</span>
          </Link>
        </nav>
      </div>
    </header>
  )
}
