import { useEffect, useRef, useState } from 'react';
import { useChat } from '../../contexts/ChatContext';
import ChatInput from './ChatInput';
import ChatMessages from './ChatMessages';
import { Menu } from '@mui/icons-material';
import { chatApi } from '../../utils/api';

interface ChatContainerProps {
  toggleSidebar: () => void;
}

function ChatContainer({ toggleSidebar }: ChatContainerProps) {
  const { currentChatId, currentChat, createNewChat, addMessage } = useChat();
  const [isLoading, setIsLoading] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleSendMessage = async (message: string) => {
    if (!currentChatId) {
      createNewChat();
      setPendingMessage(message);
      return;
    }

    addMessage('user', message);
    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.sendMessage(currentChatId, message);
      addMessage('assistant', response.response);
    } catch (err) {
      setError('Failed to get response from the assistant. Please try again.');
      console.error('Error sending message:', err);
      addMessage('assistant', error!);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (currentChatId && pendingMessage) {
      handleSendMessage(pendingMessage);
      setPendingMessage(null);
    }
  }, [currentChatId, pendingMessage]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [currentChatId]);

  return (
    <div className='flex h-full flex-col'>
      <div className='flex items-center justify-between border-b border-b-neutral-700 p-2'>
        <button
          onClick={toggleSidebar}
          className='rounded-md p-1.5 pl-2 hover:bg-[#454545]'
        >
          <Menu />
        </button>
        <h1 className='text-xl font-semibold'>Bundle AI</h1>
        <div className='w-10'></div>
      </div>

      <div className='flex-1 overflow-hidden'>
        <div className='h-full'>
          {!currentChatId ? (
            <span className='flex h-11/12 items-center justify-center text-4xl font-medium'>
              Hi, how can I help you?
            </span>
          ) : (
              <ChatMessages messages={currentChat?.messages || []} />
          )}
        </div>
      </div>

      <div className='flex justify-center px-3'>
        <ChatInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          inputRef={inputRef}
        />
      </div>
    </div>
  );
}

export default ChatContainer;
