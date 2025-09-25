import React, { useState } from 'react'
import { ChevronDownIcon, DocumentTextIcon, LightBulbIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

interface QuickTemplatesProps {
  onSelectTemplate: (text: string) => void
}

interface TemplateCategory {
  title: string
  icon: React.ReactNode
  templates: string[]
}

const templateCategories: TemplateCategory[] = [
  {
    title: '刑事事件',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      '逮捕されそうなのですが、どう対応すればよいですか？',
      '家族が逮捕されました。今後の流れを教えてください。',
      '示談交渉について詳しく知りたいです。',
      '前科がつくとどのような影響がありますか？',
      '保釈申請の条件と手続きを教えてください。'
    ]
  },
  {
    title: '交通事故・違反',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      '飲酒運転で検挙されました。罰則について教えてください。',
      'ひき逃げの疑いをかけられています。どう対処すべきですか？',
      '無免許運転の罰則と今後の影響を知りたいです。',
      'スピード違反で免許停止になりそうです。対処法はありますか？',
      '交通事故の示談交渉のポイントを教えてください。'
    ]
  },
  {
    title: '暴力・傷害',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      '喧嘩で相手を怪我させてしまいました。罪に問われますか？',
      '暴行罪と傷害罪の違いを教えてください。',
      'DVで訴えられそうです。どう対応すべきですか？',
      '正当防衛が認められる条件を知りたいです。',
      '器物損壊で被害届を出されました。今後どうなりますか？'
    ]
  },
  {
    title: '財産犯罪',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      '万引きで捕まりました。初犯の場合の処分を教えてください。',
      '横領の疑いをかけられています。どう対処すべきですか？',
      '詐欺罪に該当するケースについて教えてください。',
      '窃盗と占有離脱物横領の違いは何ですか？',
      '背任罪について詳しく知りたいです。'
    ]
  },
  {
    title: '薬物犯罪',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      '大麻所持で逮捕されました。今後の流れを教えてください。',
      '薬物使用の初犯の場合、執行猶予はつきますか？',
      '覚醒剤取締法違反の罰則について教えてください。',
      '薬物依存症の治療は刑罰に影響しますか？',
      '違法薬物の譲渡と譲受の罪の違いを知りたいです。'
    ]
  },
  {
    title: 'その他の相談',
    icon: <LightBulbIcon className="w-4 h-4" />,
    templates: [
      '警察から任意の事情聴取を求められました。応じるべきですか？',
      '被害届と告訴の違いを教えてください。',
      '時効について詳しく知りたいです。',
      '弁護士に依頼するタイミングはいつが良いですか？',
      '刑事事件の費用について教えてください。'
    ]
  }
]

const QuickTemplates: React.FC<QuickTemplatesProps> = ({ onSelectTemplate }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)

  const handleTemplateClick = (template: string) => {
    onSelectTemplate(template)
    setIsOpen(false)
    setSelectedCategory(null)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          'flex items-center gap-2 px-4 py-2 rounded',
          'bg-white border border-gray-200',
          'hover:bg-gray-50',
          'transition-colors duration-200 text-sm font-medium text-gray-700',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
        )}
      >
        <DocumentTextIcon className="w-5 h-5 text-blue-600" />
        <span>テンプレートから選択</span>
        <ChevronDownIcon
          className={clsx(
            'w-4 h-4 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <div className="absolute left-0 mt-2 w-96 z-50 animate-fadeIn">
          <div className="bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden">
            {/* Categories */}
            <div className="p-3 border-b border-gray-100">
              <div className="grid grid-cols-2 gap-2">
                {templateCategories.map((category, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedCategory(index === selectedCategory ? null : index)}
                    className={clsx(
                      'flex items-center gap-2 px-3 py-2 rounded text-sm',
                      'transition-colors duration-200',
                      selectedCategory === index
                        ? 'bg-blue-50 text-blue-700 font-medium'
                        : 'hover:bg-gray-50 text-gray-600'
                    )}
                  >
                    {category.icon}
                    <span className="truncate">{category.title}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Templates */}
            {selectedCategory !== null && (
              <div className="max-h-64 overflow-y-auto p-3 animate-slideIn">
                <div className="space-y-1">
                  {templateCategories[selectedCategory].templates.map((template, index) => (
                    <button
                      key={index}
                      onClick={() => handleTemplateClick(template)}
                      className={clsx(
                        'w-full text-left px-3 py-2.5 rounded',
                        'text-sm text-gray-700 hover:bg-blue-50',
                        'hover:text-blue-700 transition-colors duration-150',
                        'focus:outline-none focus:bg-blue-50 focus:text-blue-700'
                      )}
                    >
                      {template}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Quick tips */}
            {selectedCategory === null && (
              <div className="p-4 bg-gray-50">
                <p className="text-xs text-gray-500">
                  💡 カテゴリーを選択して、よくある質問テンプレートを表示します
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setIsOpen(false)
            setSelectedCategory(null)
          }}
        />
      )}
    </div>
  )
}

export default QuickTemplates