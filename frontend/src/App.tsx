import { useState } from 'react';
import { ChatProvider } from './contexts/ChatContext';
import ChatContainer from './components/chat/ChatContainer';
import Sidebar from './components/layout/Sidebar';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <ChatProvider>
      <div className='flex h-screen w-screen bg-[#252525] text-stone-100'>
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
        <main className={`flex-1 duration-300 ${sidebarOpen ? 'md:ml-72' : 'ml-0'}`}>
          <ChatContainer toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        </main>
      </div>
    </ChatProvider>
  );
}

export default App;
