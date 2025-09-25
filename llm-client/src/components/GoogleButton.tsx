import React from 'react'

interface GoogleButtonProps {
  onClick: () => void
  isLoading?: boolean
  text?: string
}

const GoogleIcon = () => (
  <svg
    className="h-5 w-5"
    viewBox="0 0 18 18"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path d="M17.64 9.2045c0-.6381-.0573-1.2527-.1636-1.8409H9v3.4813h4.8436c-.2093 1.125-.8436 2.0795-1.7977 2.7181v2.2581h2.9086c1.7018-1.5677 2.6855-3.8731 2.6855-6.6166z" fill="#4285F4" />
    <path d="M9 18c2.43 0 4.4673-.8063 5.9564-2.1795l-2.9086-2.2581c-.8063.54-1.8363.8581-3.0478.8581-2.3441 0-4.3281-1.5822-5.0354-3.7104H.956543v2.3317C2.4379 15.9837 5.48105 18 9 18z" fill="#34A853" />
    <path d="M3.96459 10.7101c-.18-.54-.282-1.1163-.282-1.7101s.102-1.1701.282-1.7101V4.95836H.956543C.347159 6.01854 0 7.45544 0 9.00004s.347159 2.9815.956543 4.0417l3.008047-2.3316z" fill="#FBBC05" />
    <path d="M9 3.58c1.3209 0 2.5068.4536 3.4391 1.3432l2.579-2.579C13.4616.9437 11.425 0 9 0 5.48105 0 2.4379 2.01666.956543 4.95836L3.96459 7.29006C4.6719 5.16226 6.6559 3.58 9 3.58z" fill="#EA4335" />
  </svg>
)

const GoogleButton: React.FC<GoogleButtonProps> = ({
  onClick,
  isLoading = false,
  text = 'Googleで続ける'
}) => {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      aria-busy={isLoading}
      className="relative w-full flex items-center justify-center gap-3 h-11 px-4 rounded-md border border-[#dadce0] bg-white text-[13px] font-medium text-[#3c4043] transition-colors duration-200 disabled:opacity-70 disabled:cursor-not-allowed hover:bg-[#f7f8f8] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#4285F4]/40"
    >
      <span className="absolute left-4 flex items-center">
        <GoogleIcon />
      </span>
      <span className="tracking-wide">
        {isLoading ? '処理中...' : text}
      </span>
    </button>
  )
}

export default GoogleButton
