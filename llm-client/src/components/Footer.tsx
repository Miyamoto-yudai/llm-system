const Footer: React.FC = () => {
  return (
    <div className="bg-gray-900">
      <footer className="mx-auto max-w-screen-2xl px-4 md:px-8">
	<div className="mb-16 grid grid-cols-2 gap-12 pt-10 md:grid-cols-4 lg:grid-cols-6 lg:gap-8 lg:pt-12">
	  <div className="col-span-full lg:col-span-2">
	    <div className="mb-4 lg:-mt-2">
	      <a href="/" className="inline-flex items-center gap-2 text-xl font-bold text-gray-100 md:text-2xl" aria-label="logo">
		{/*
		    <svg width="95" height="94" viewBox="0 0 95 94" className="h-auto w-5 text-indigo-500" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
		    <path d="M96 0V47L48 94H0V47L48 0H96Z" />
		    </svg>
		  */}

		LawFlow
	      </a>
	    </div>

	    <div className="flex gap-4">
	    </div>
	    <h2 className="text-gray-400">免責事項</h2>
	      <div className="mb-6 text-gray-400 sm:pr-8 text-xs">
		<p>１．本サービスは、ユーザーの入力した質問に対して、機械学習に基づいて確率的に応答の生成を行い回答を出力するものです。状況によっては、実在の人物、場所、または事実関係を正確に反映していない誤った回答となる可能性があります。また、法的な問題については正確に回答できない可能性があります。ユーザーは自己の責任において本サービスを利用するものとし、弁護士に相談するなどして、回答の正確性を確保するようにしてください。
		</p>
		<p>
		  ２．運営組織は、本サービスに関し、以下の内容について保証を行うものではありません。
		  ①本サービスのサービス内容がユーザーの要求に合致すること又は有益であること
		  ②他のユーザーによる本サービスの利用が正確又は適正であり、本サービスに悪影響を与えないこと
		  ③本サービスが中断、中止又は廃止されないこと
		  ④本サービスがタイムリーに提供されること
		  ⑤本サービスにおいていかなるエラーも発生しないこと
		  ⑥ユーザーが本サービスを通じて取得する情報が正確かつ最新であること
		  ⑦本サービスにいかなる誤りもないこと
		  ⑧ユーザーが本サービスを利用して行った行為がユーザーの特定の目的（商業的な目的を含みますがこれに限定するものではありません）に適合すること
		  ⑨本サービスを通じてユーザーが登録するユーザー情報又は入力した内容が消失しないこと
		</p>
		<p>
		  ３．運営組織は、ユーザーの本サービスの利用により、ユーザーの法務業務を代行する又は法律上の専門的知識に基づいて具体的な紛争を背景とした法律的見解を提供する等法律事務の取り扱いを受託するものではありません。
		</p>
		<p>４．運営組織は、本サービスの利用に起因してユーザーに生じたあらゆる損害について一切の責任を負いません。</p>
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

	  <div>
	    <div className="mb-4 font-bold uppercase tracking-widest text-gray-100">法人情報</div>

	    <nav className="flex flex-col gap-4">
	      <div>
		<a href="/company" className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">会社概要</a>
	      </div>
	      
	      <div>
		<a href="/terms" className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">利用規約</a>
	      </div>

	      <div>
		<a href="/privacy-policy" className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">プライバシーポリシー</a>
	      </div>

	      <div>
		<a href="/asct" className="text-gray-400 transition duration-100 hover:text-indigo-500 active:text-indigo-600">特定商取引に基づく表記</a>
	      </div>

	    </nav>
	  </div>
	  
	  
	</div>
	<div className="border-t border-gray-800 py-8 text-center text-sm text-gray-400">© 2024 - LawFlow. All rights reserved.</div>
      </footer>
    </div>
    
  )
}

export default Footer
