import React from 'react'

const Footer: React.FC = () => {
  return (
    <div className="bg-gray-900">
      <footer className="mx-auto max-w-screen-2xl px-4 md:px-8">
	<div className="mb-8 sm:mb-16 grid grid-cols-1 sm:grid-cols-2 gap-6 sm:gap-12 pt-6 sm:pt-10 md:grid-cols-4 lg:grid-cols-6 lg:gap-8 lg:pt-12">
	  <div className="col-span-full lg:col-span-2">
	    <div className="mb-4">
	      <a href="/" className="inline-flex items-center gap-2 text-xl font-bold text-gray-100 md:text-2xl" aria-label="logo">
		LawFlow
	      </a>
	    </div>

	    <div className="flex gap-4">
	    </div>
	    <div className="mb-8">
	      <h2 className="text-gray-300 font-bold mb-3 text-sm">免責事項</h2>
	      <div className="bg-gray-800 rounded-lg p-3 sm:p-4 max-h-40 sm:max-h-48 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
		<div className="text-gray-400 text-[10px] sm:text-xs space-y-2 sm:space-y-3 leading-relaxed">
		  <div className="pb-2 border-b border-gray-700">
		    <span className="font-semibold text-gray-300">1. サービスの性質</span>
		    <p className="mt-1">
		      本サービスは、ユーザーの入力した質問に対して、機械学習に基づいて確率的に応答の生成を行い回答を出力するものです。状況によっては、実在の人物、場所、または事実関係を正確に反映していない誤った回答となる可能性があります。また、法的な問題については正確に回答できない可能性があります。ユーザーは自己の責任において本サービスを利用するものとし、弁護士に相談するなどして、回答の正確性を確保するようにしてください。
		    </p>
		  </div>

		  <div className="pb-2 border-b border-gray-700">
		    <span className="font-semibold text-gray-300">2. 保証の否認</span>
		    <p className="mt-1 mb-2">運営組織は、本サービスに関し、以下の内容について保証を行うものではありません：</p>
		    <ul className="ml-2 sm:ml-4 space-y-1">
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">①</span><span>本サービスのサービス内容がユーザーの要求に合致すること又は有益であること</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">②</span><span>他のユーザーによる本サービスの利用が正確又は適正であり、本サービスに悪影響を与えないこと</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">③</span><span>本サービスが中断、中止又は廃止されないこと</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">④</span><span>本サービスがタイムリーに提供されること</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">⑤</span><span>本サービスにおいていかなるエラーも発生しないこと</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">⑥</span><span>ユーザーが本サービスを通じて取得する情報が正確かつ最新であること</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">⑦</span><span>本サービスにいかなる誤りもないこと</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">⑧</span><span>ユーザーが本サービスを利用して行った行為がユーザーの特定の目的に適合すること</span></li>
		      <li className="flex"><span className="mr-1 sm:mr-2 flex-shrink-0">⑨</span><span>本サービスを通じてユーザーが登録する情報が消失しないこと</span></li>
		    </ul>
		  </div>

		  <div className="pb-2 border-b border-gray-700">
		    <span className="font-semibold text-gray-300">3. 法律事務の非受託</span>
		    <p className="mt-1">
		      運営組織は、ユーザーの本サービスの利用により、ユーザーの法務業務を代行する又は法律上の専門的知識に基づいて具体的な紛争を背景とした法律的見解を提供する等法律事務の取り扱いを受託するものではありません。
		    </p>
		  </div>

		  <div>
		    <span className="font-semibold text-gray-300">4. 免責</span>
		    <p className="mt-1">
		      運営組織は、本サービスの利用に起因してユーザーに生じたあらゆる損害について一切の責任を負いません。
		    </p>
		  </div>
		</div>
	      </div>
	    </div>	      
	  </div>
	  
	  {/*
	  <div>
	  <div className="mb-4 font-bold uppercase tracking-widest text-gray-100">協力組織</div>
	    
	    <nav className="flex flex-col gap-4">
	      <div>
	      <a href="https://tokyo-keijibengosi.com/" className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">弁護士法人あいち刑事事件総合法律事務所</a>
	      </div>
	    </nav>
	  </div>
	  */}
	  <div></div>

	  <div className="col-span-1">
	    <div className="mb-4 font-bold uppercase tracking-widest text-gray-100 text-sm">法人情報</div>

	    <nav className="flex flex-col gap-2 sm:gap-4">
	      <div>
		<a href="/company" className="text-sm text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">会社概要</a>
	      </div>

	      <div>
		<a href="/terms" className="text-sm text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">利用規約</a>
	      </div>

	      <div>
		<a href="/privacy-policy" className="text-sm text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">プライバシーポリシー</a>
	      </div>

	      <div>
		<a href="/asct" className="text-sm text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">特定商取引に基づく表記</a>
	      </div>

	    </nav>
	  </div>
	  
	  
	</div>
	<div className="border-t border-gray-800 py-4 sm:py-8 text-center text-xs sm:text-sm text-gray-400">© 2024 - LawFlow. All rights reserved.</div>
      </footer>
    </div>
    
  )
}

export default Footer
