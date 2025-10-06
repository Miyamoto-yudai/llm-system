import React from 'react'
import clsx from 'clsx'

export interface TopicGenre {
  id: string
  label: string
  icon: string
  color: string
}

interface TopicSelectorProps {
  selectedGenre: string | null
  onSelectGenre: (genreId: string | null) => void
}

export const topicGenres: TopicGenre[] = [
  { id: 'criminal', label: '刑事事件全般', icon: '⚖️', color: 'blue' },
  { id: 'traffic', label: '交通事故・違反', icon: '🚗', color: 'yellow' },
  { id: 'violence', label: '暴力・傷害', icon: '🤕', color: 'red' },
  { id: 'property', label: '財産犯罪', icon: '💰', color: 'green' },
  { id: 'drugs', label: '薬物犯罪', icon: '💊', color: 'purple' },
  { id: 'other', label: 'その他', icon: '📋', color: 'gray' }
]

const getColorClasses = (color: string, isSelected: boolean) => {
  if (isSelected) {
    const colorMap: Record<string, string> = {
      blue: 'bg-blue-600 text-white shadow-md',
      yellow: 'bg-yellow-600 text-white shadow-md',
      red: 'bg-red-600 text-white shadow-md',
      green: 'bg-green-600 text-white shadow-md',
      purple: 'bg-purple-600 text-white shadow-md',
      gray: 'bg-gray-600 text-white shadow-md'
    }
    return colorMap[color] || colorMap.gray
  }
  return 'bg-white border border-gray-200 text-gray-700 hover:bg-gray-50'
}

const TopicSelector: React.FC<TopicSelectorProps> = ({ selectedGenre, onSelectGenre }) => {
  const handleGenreClick = (genreId: string) => {
    // Toggle selection: if already selected, deselect it
    if (selectedGenre === genreId) {
      onSelectGenre(null)
    } else {
      onSelectGenre(genreId)
    }
  }

  return (
    <div className="bg-gray-50 border-b border-gray-200 p-3">
      <div className="max-w-screen-lg mx-auto">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-gray-600 whitespace-nowrap">
            相談ジャンル:
          </span>
          <div className="flex gap-2 overflow-x-auto flex-1 scrollbar-hide">
            {topicGenres.map((genre) => (
              <button
                key={genre.id}
                onClick={() => handleGenreClick(genre.id)}
                className={clsx(
                  'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap',
                  'transition-all duration-200 flex items-center gap-1.5',
                  'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
                  getColorClasses(genre.color, selectedGenre === genre.id)
                )}
                title={`${genre.label}を選択`}
              >
                <span className="text-base">{genre.icon}</span>
                <span>{genre.label}</span>
              </button>
            ))}
          </div>
        </div>
        {selectedGenre && (
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-2">
            <span>✓ 選択中:</span>
            <span className="font-medium text-gray-700">
              {topicGenres.find(g => g.id === selectedGenre)?.label}
            </span>
            <button
              onClick={() => onSelectGenre(null)}
              className="text-blue-600 hover:text-blue-700 underline ml-2"
            >
              選択解除
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default TopicSelector
