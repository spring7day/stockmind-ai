'use client'

// HomeSearchClient — 홈 페이지 검색창 (헤더 검색창에 포커스)

export default function HomeSearchClient() {
  return (
    <div className="relative max-w-lg mx-auto">
      <button
        type="button"
        onClick={() => {
          const headerInput = document.querySelector('header input') as HTMLInputElement
          headerInput?.focus()
        }}
        className="flex items-center gap-3 w-full bg-card border border-border hover:border-primary/50 rounded-xl px-4 py-4 transition-colors cursor-pointer group"
      >
        <svg
          className="w-5 h-5 text-text-muted group-hover:text-primary transition-colors"
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
        <span className="text-text-muted group-hover:text-text-secondary transition-colors">
          종목명 또는 종목코드로 검색 (예: 삼성전자, 005930)
        </span>
        <span className="ml-auto text-xs px-2 py-1 rounded-lg bg-surface border border-border text-text-muted hidden sm:block">
          ⌘K
        </span>
      </button>
    </div>
  )
}
