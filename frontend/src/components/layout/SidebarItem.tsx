import { ReactNode } from 'react';

interface SidebarItemProps {
  text: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  onClick?: () => void;
  active?: boolean;
  className?: string;
}

function SidebarItem({
  text,
  leftIcon,
  rightIcon,
  onClick,
  active = false,
  className = '',
}: SidebarItemProps) {
  return (
    <div
      className={`group mx-2 flex cursor-pointer items-center justify-between gap-1 rounded-xl px-3 py-2 hover:bg-[#252525] ${active ? 'bg-[#353535]' : ''} ${className}`}
      onClick={onClick}
    >
      <div className='flex items-center gap-2 truncate'>
        {leftIcon && <div className='shrink-0'>{leftIcon}</div>}
        <span>{text}</span>
      </div>
      {rightIcon && (
        <div className='shrink-0 opacity-0 transition-opacity duration-100 group-hover:opacity-100'>
          {rightIcon}
        </div>
      )}
    </div>
  );
}

export default SidebarItem;
