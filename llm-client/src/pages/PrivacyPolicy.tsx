import clsx from 'clsx'

export default function PrivacyPolicyPage() {
  return (
    <div>
      <div className="py-6 sm:py-8 lg:py-12 bg-slate-100">
	<div className="mx-auto max-w-screen-md px-4 md:px-8 rounded bg-white  p-8">
	  <h1 className="mb-4 text-center text-2xl font-bold text-gray-800 sm:text-3xl md:mb-6">プライバシーポリシー</h1>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">LawFlow株式会社(以下「運営組織」といいます。)は、お客様の個人情報保護の重要性について認識し、個人情報の保護に関する法律(以下「個人情報保護法」といいます。)を遵守すると共に、以下のプライバシーポリシー(以下「本プライバシーポリシー」といいます。)に従い、 適切な取扱い及び保護に努めます。</p>
	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">1. 個人情報の定義</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">本プライバシーポリシーにおいて、個人情報とは、個人情報保護法第2条第1項により定義された個人情報、すなわち、生存する個人に関する情報であって、 当該情報に含まれる氏名、生年月日その他の記述等により特定の個人を識別することができるもの(他の情報と容易に照合することができ、それにより特定の個人を識別することができることとなるものを含みます。)を意味するものとし、ユーザー登録に当たり入力されたユーザー情報を含みます。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">2. 個人情報の利用目的</h2>
	  <div className="mb-6 text-gray-800 sm:text-lg md:mb-8">
	    <p>弊サービスでは、お客様の個人情報を以下の目的で利用いたします。</p>
	    <p>(1)運営組織の利用に必要な会員の管理のためのシステム運営</p>
	    <p>(2)運営組織の利便性を向上させるためのシステム運営</p>
	    <p>(3)メンテナンス情報や、重要なご連絡など、運営組織を運用する上で必要な皆様へのお知らせ</p>
	    <p>(4)運営組織の利用者の皆様に有用だと思われるメールマガジン、お知らせ</p>
	    <p>(5)運営組織へのご質問、お問い合わせなどに関する回答</p>
	    <p>(6)利用者の皆様の属性、行動、運営組織内でのアクセス履歴などを用いたターゲティング広告の配信</p>
	    <p>(7)運営組織上で、個人を特定できない範囲においての統計情報の作成および利用</p>
	    <p>(8)運営組織の各サービスにおける情報の連携及び共有</p>
	    <p>(9)運営組織の新規開発に必要なデータの解析や分析</p>
	    <p>(10)運営組織が提携している先への個人を特定できず会員の許諾を得た範囲内での情報の提供</p>
	  </div>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">3. 個人情報利用目的の変更</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、個人情報の利用目的を相当の関連性を有すると合理的に認められる範囲内において変更することがあり、変更した場合には運営組織内にてお客様に通知又は公表します。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">4.個人情報利用の制限</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、個人情報保護法その他の法令により許容される場合を除き、お客様の同意を得ず、 「2. 個人情報の利用目的」に定めた利用目的の達成に必要な範囲を超えて個人情報を取り扱いません。
	    但し、次の場合はこの限りではありません。</p>
	  <div className="mb-6 text-gray-800 sm:text-lg md:mb-8">
	    <p>(1)法令に基づく場合</p>
	    <p>(2)人の生命、身体又は財産の保護のために必要がある場合であって、お客様の同意を得ることが困難であるとき</p>
	    <p>(3)公衆衛生の向上又は児童の健全な育成の推進のために特に必要がある場合であって、お客様の同意を得ることが困難であるとき</p>
	    <p>(4)国の機関もしくは地方公共団体又はその委託を受けた者が法令の定める事務を遂行することに対して協力する必要がある場合であって、お客様の同意を得ることにより当該事務の遂行に支障を及ぼすおそれがあるとき</p>
	  </div>
	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">5. 個人情報の適正な取得</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、適正に個人情報を取得し、偽りその他不正の手段により取得しません。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">6.個人情報の安全管理</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、個人情報の紛失、破壊、改ざん及び漏洩などのリスクに対して、個人情報の安全管理が図られるよう、運営組織の従業員に対し、必要かつ適切な監督を行います。
また、運営組織において、個人情報の取扱いの全部又は一部を委託する場合は、委託先において個人情報の安全管理が図られるよう、必要かつ適切な監督を行います。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">7.第三者提供</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、個人情報保護法その他の法令に基づき開示が認められる場合を除くほか、あらかじめお客様の同意を得ないで、個人情報を第三者に提供しません。
	    但し、次に掲げる場合は上記に定める第三者への提供には該当しません。</p>
	  <div className="mb-6 text-gray-800 sm:text-lg md:mb-8">
	    <p>(1)運営組織が利用目的の達成に必要な範囲内において個人情報の取扱いの全部又は一部を委託する場合</p>
	    <p>(2)合併その他の事由による事業の承継に伴って個人情報が提供される場合</p>
	    <p>(3)別途定めに従って共同利用する場合</p>
	  </div>


	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">8. 個人情報の開示</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">お客様から、個人情報保護法の定めに基づき個人情報の開示を求められたときは、 お客様ご本人からのご請求であることを確認の上で、お客様に対し、遅滞なく開示を行います (当該個人情報が存在しないときにはその旨を通知いたします。)。
但し、個人情報保護法その他の法令により、LawFlowが開示の義務を負わない場合は、この限りではありません。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">9. 個人情報の訂正等</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織では、お客様から、個人情報が真実でないという理由によって、個人情報保護法の定めに基づきその内容の訂正、追加又は削除(以下「訂正等」といいます。)を求められた場合には、お客様ご本人からのご請求であることを確認の上で、 利用目的の達成に必要な範囲内において、遅滞なく必要な調査を行い、その結果に基づき、個人情報の内容の訂正等を行い、その旨をお客様に通知します(訂正等を行わない旨の決定をしたときは、お客様に対しその旨を通知いたします。)。
但し、個人情報保護法その他の法令により、LawFlowが訂正等の義務を負わない場合は、この限りではありません。</p>
	  
	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">10.個人情報の利用停止等</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織は、お客様から、お客様の個人情報が、あらかじめ公表された利用目的の範囲を超えて 取り扱われているという理由又は偽りその他不正の手段により取得されたものであるという理由 により、個人情報保護法の定めに基づきその利用の停止又は消去(以下「利用停止等」とい います。)を求められた場合において、 そのご請求に理由があることが判明した場合には、お客様ご本人からのご請求であることを確認の上で、遅滞なく個人情報の利用停止等を行い、 その旨をお客様に通知します。
但し、個人情報保護法その他の法令により、運営組織が利用停止 等の義務を負わない場合は、この限りではありません。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">12. 第三者のトラッキングシステム</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織では、お客様の動向の調査や最適な広告配信をする為に第三者企業(*1)によるクッキー、画像ファイル（ウェブビーコン）などを用い、統計的なサイト利用情報を取得することがあります。
さらに、上記のCookieやウェブビーコンの中には、第三者企業が直接情報を取得するものも含まれ、そこで収集されるCookie情報については運営組織に提供・開示されることはなく、第三者企業が定めるプライバシーの考え方にしたがって管理されます。
これらの情報は個人識別はされず、匿名のデータの形で扱われます。また目的以外の用途で利用されることもありません。</p>

	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">13.Google Analyticsやその他解析ツールの利用について</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織において、ユーザーの動向を調査する為にGoogle Analyticsを用い、統計的な利用情報を取得することがあります。
	    Google Analyticsの詳細に関しては、下記をご確認ください。</p>
	  <div className="mb-6 text-gray-800">http://www.google.com/analytics/</div>

	  
	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">14. お問い合わせ</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">開示等のお申出、ご意見、ご質問のお申出その他個人情報の取扱いに関するお問い合わせは、下記の窓口までお願い致します。</p>
	  <div className="mb-6 text-gray-800 sm:text-lg md:mb-8">
	    <p>事業者名: 則竹理宇</p>
	    <p>運営責任者: 則竹理宇</p>
	    <p>所在地: 160-0023 東京都新宿区西新宿1-14-15 タウンウエストビル9階</p>
	    <p>E-mail: office@lawflow.jp</p>
	    <p>(なお、受付時間は、平日9時から17時までとさせていただきます。)</p>
	  </div>
	  
	  <h2 className="mb-2 text-xl font-semibold text-gray-800 sm:text-2xl md:mb-4">15. 継続的改善</h2>
	  <p className="mb-6 text-gray-800 sm:text-lg md:mb-8">運営組織では、個人情報の取扱いに関する運用状況を適宜見直し、継続的な改善に努めるものとし、 必要に応じて、本プライバシーポリシーを変更することがあります。</p>
	  <div className="mb-6 text-gray-800 sm:text-lg md:mb-8">
	    <p>(2023年4月26日 制定)</p>
	    <p>(2023年5月2日 改定)</p>
	  </div>

	  
	</div>
      </div>
    </div>
  )
}
