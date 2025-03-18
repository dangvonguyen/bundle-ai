import { Message } from '../../contexts/ChatContext';

interface ChatMessagesProps {
  messages: Message[];
}

function ChatMessages({ messages }: ChatMessagesProps) {
  return (
    <div className='h-full overflow-hidden'>
      <div className='scrollbar scrollbar-thumb-[#656565] scrollbar-track-transparent h-full overflow-y-scroll pl-3.5'>
        <div className='mx-auto flex max-w-3xl flex-col space-y-10 px-8 pt-4 pb-16'>
          {messages.map((message) =>
            message.role === 'user' ? (
              <div key={message.id} className='flex justify-end'>
                <div className='max-w-[70%] rounded-3xl bg-[#303030] px-5 py-3'>
                  {message.content}
                </div>
              </div>
            ) : (
              <div key={message.id}>{message.content}</div>
            ),
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatMessages;
