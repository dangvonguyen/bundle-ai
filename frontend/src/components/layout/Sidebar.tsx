import { useChat } from '../../contexts/ChatContext';
import SidebarItem from './SidebarItem';
import { Add, DeleteOutlined } from '@mui/icons-material';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const { chats, currentChatId, selectChat, deleteChat, setCurrentChatId } = useChat();

  return (
    <>
      {isOpen && (
        <div
          className='fixed inset-0 z-10 bg-black/50 md:hidden'
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed z-20 h-full w-72 bg-[#171717] duration-300 ${!isOpen && '-translate-x-full'}`}
      >
        <div className='py-4'>
          <SidebarItem
            text='New chat'
            leftIcon={<Add />}
            onClick={() => setCurrentChatId(null)}
          />
        </div>

        <div className='flex h-[calc(100%-5rem)] flex-col'>
          <span className='px-5 text-sm font-bold'>Recents</span>
          <div className='scrollbar-thin scrollbar-thumb-[#455445] scrollbar-track-transparent mt-1 flex-1 overflow-y-auto'>
            {chats.map((chat) => (
              <SidebarItem
                text={chat.title}
                onClick={() => selectChat(chat.id)}
                active={currentChatId === chat.id}
                className='font-normal text-stone-100'
                rightIcon={
                  <button
                    className='cursor-pointer'
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteChat(chat.id);
                    }}
                  >
                    <DeleteOutlined />
                  </button>
                }
              />
            ))}
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
