import React, { useState } from 'react';
import { Send } from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  inputRef?: React.RefObject<HTMLTextAreaElement | null>;
}

function ChatInput({ onSendMessage, disabled = false, inputRef }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      onClick={() => inputRef?.current?.focus()}
      className='flex max-h-56 w-full max-w-3xl rounded-3xl rounded-b-none bg-[#303030]'
    >
      <textarea
        ref={inputRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='Ask anything'
        className='m-5 w-full resize-none outline-none'
      />
      <button
        type='submit'
        disabled={disabled || !message.trim()}
        className='mr-5 flex items-center self-center rounded-full bg-blue-400 p-1.5 hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-gray-500'
      >
        <Send />
      </button>
    </form>
  );
}

export default ChatInput;
