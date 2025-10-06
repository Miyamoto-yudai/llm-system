import React, { useState } from 'react'
import { ChevronDownIcon, DocumentTextIcon, LightBulbIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

interface QuickTemplatesProps {
  onSelectTemplate: (text: string) => void
  textareaRef?: React.RefObject<HTMLTextAreaElement>
}

interface TemplateCategory {
  title: string
  icon: React.ReactNode
  templates: string[]
}

const templateCategories: TemplateCategory[] = [
  {
    title: '暴行・傷害事件',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      `暴行・傷害事件について相談させてください。

【事件の概要】
・発生日時：
・発生場所：
・事件の経緯：（喧嘩になった理由、どのような暴力があったか等）

【相手の怪我の状況】
・怪我の程度：（例：打撲、骨折、出血等）
・通院状況：
・診断書：（有無、診断内容）

【現在の状況】
・警察への通報：（有・無）
・被害届：（提出済・未提出・不明）
・逮捕：（逮捕済・在宅捜査・なし）
・取り調べ：（受けた場合の説明内容）

【前科・前歴】
・過去の犯罪歴：

【示談の状況】
・示談交渉：
・示談金：

【事件後の対応】
・謝罪：
・賠償の意思：

【知りたいこと】
`
    ]
  },
  {
    title: '交通違反・事故',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      `交通違反・事故について相談させてください。

【事件の概要】
・発生日時：
・発生場所：
・事故・違反の内容：
・飲酒：（有・無、飲酒量）
・速度：（速度違反の場合）

【被害・損害の状況】
・人身被害：（有・無、怪我の程度）
・物損：
・保険：（適用状況、保険会社への連絡）

【現在の状況】
・警察への届出：
・免許の状態：（通常・停止中・取消）
・罰金・反則金：
・取り調べ：

【前科・前歴】
・交通違反歴：
・その他の犯罪歴：

【示談の状況】
・示談交渉：
・保険会社の対応：

【事件後の対応】
・謝罪：
・賠償の意思：

【知りたいこと】
`
    ]
  },
  {
    title: '窃盗・万引き事件',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      `窃盗・万引き事件について相談させてください。

【事件の概要】
・発生日時：
・発生場所：
・盗んだ物：
・被害額：

【盗品の状況】
・返却：（済・未）
・弁償：（済・未、金額）

【現在の状況】
・警察への通報：（有・無）
・逮捕：（逮捕済・在宅捜査・なし）
・取り調べ：
・家宅捜索：（有・無）

【前科・前歴】
・窃盗・万引き歴：
・その他の犯罪歴：

【示談の状況】
・示談交渉：
・示談金：

【事件後の対応】
・謝罪：
・盗品の返却：
・弁償の意思：

【知りたいこと】
`
    ]
  },
  {
    title: '薬物事件',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      `薬物事件について相談させてください。

【事件の概要】
・発生日時：
・薬物の種類：
・行為：（所持・使用・譲渡）
・量：

【現在の状況】
・警察への通報：（有・無、発覚の経緯）
・逮捕：（逮捕済・在宅捜査・なし）
・取り調べ：
・尿検査・鑑定：（結果）

【使用状況】
・使用頻度：
・使用期間：
・入手経路：

【前科・前歴】
・薬物事件歴：
・その他の犯罪歴：

【治療・更生の状況】
・薬物依存症の治療歴：
・現在の通院状況：
・更生プログラム：

【事件後の対応】
・薬物の処分：
・治療の予定：

【知りたいこと】
`
    ]
  },
  {
    title: '詐欺・横領事件',
    icon: <DocumentTextIcon className="w-4 h-4" />,
    templates: [
      `詐欺・横領事件について相談させてください。

【事件の概要】
・発生期間：
・手口：（方法、内容）
・被害総額：
・被害者数：

【被害金の状況】
・返済状況：（返済済額）
・弁償：

【現在の状況】
・警察への通報：（有・無）
・被害届：（提出済・未提出・不明）
・逮捕：（逮捕済・在宅捜査・なし）
・取り調べ：

【前科・前歴】
・詐欺・横領歴：
・その他の犯罪歴：

【示談の状況】
・示談交渉：
・返済計画：

【事件後の対応】
・謝罪：
・返済の意思：
・弁償の申し出：

【知りたいこと】
`
    ]
  },
  {
    title: 'その他の刑事事件',
    icon: <LightBulbIcon className="w-4 h-4" />,
    templates: [
      `刑事事件について相談させてください。

【事件の概要】
・発生日時：
・発生場所：
・事件の内容：

・罪名：（分かる範囲で）

【被害・損害の状況】
・被害内容：
・被害額：

【現在の状況】
・警察への通報：（有・無）
・逮捕：（逮捕済・在宅捜査・なし）
・取り調べ：

【前科・前歴】
・過去の犯罪歴：

【示談の状況】
・示談交渉：
・賠償：

【事件後の対応】
・謝罪：
・弁償の意思：

【知りたいこと】
`
    ]
  }
]

const QuickTemplates: React.FC<QuickTemplatesProps> = ({ onSelectTemplate, textareaRef }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null)

  const handleTemplateClick = (template: string) => {
    onSelectTemplate(template)
    setIsOpen(false)
    setSelectedCategory(null)

    // Auto-focus textarea and move cursor to end
    setTimeout(() => {
      if (textareaRef?.current) {
        textareaRef.current.focus()
        const length = template.length
        textareaRef.current.setSelectionRange(length, length)
      }
    }, 100)
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