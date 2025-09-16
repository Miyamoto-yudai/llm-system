import clsx from 'clsx'
export type ButtonProps = {
  onClick?: () => void;
  label: string;
}

export default function Button({ onClick, label }: ButtonProps) {
  return (
    <div>
      <button className={clsx('px-4 py-2 border')} onClick={onClick}>
        {label}
      </button>
    </div>
  )
}
