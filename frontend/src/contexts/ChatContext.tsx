import React, { useCallback, useMemo, useState } from 'react';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
}

export interface Chat {
  id: string;
  title: string;
  messages: Message[];
  lastUpdate: Date;
}

export interface ChatContextType {
  chats: Chat[];
  currentChatId: string | null;
  currentChat: Chat | null;
  createNewChat: () => void;
  selectChat: (id: string) => void;
  deleteChat: (id: string) => void;
  addMessage: (role: 'user' | 'assistant', content: string) => void;
  setCurrentChatId: React.Dispatch<React.SetStateAction<string | null>>;
}

const ChatContext = React.createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);

  const currentChat = useMemo(
    () => chats.find((chat) => chat.id === currentChatId) || null,
    [chats, currentChatId],
  );

  const createNewChat = useCallback(() => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title: `New chat`,
      messages: [],
      lastUpdate: new Date(),
    };
    setChats((prevChats) => [newChat, ...prevChats]);
    setCurrentChatId(newChat.id);
  }, []);

  const selectChat = useCallback((id: string) => {
    setCurrentChatId(id);
  }, []);

  const deleteChat = useCallback(
    (id: string) => {
      setChats((prevChats) => prevChats.filter((chat) => chat.id !== id));
      setCurrentChatId(currentChatId === id ? null : currentChatId);
    },
    [currentChatId],
  );

  const addMessage = useCallback(
    (role: 'user' | 'assistant', content: string) => {
      if (!currentChatId) return;

      const newMessage: Message = {
        id: Date.now().toString(),
        content,
        role,
      };

      setChats((prevChats) =>
        prevChats.map((chat) =>
          chat.id === currentChatId
            ? { ...chat, messages: [...chat.messages, newMessage] }
            : chat,
        ),
      );
    },
    [currentChatId],
  );

  const value: ChatContextType = {
    chats,
    currentChatId,
    currentChat,
    createNewChat,
    deleteChat,
    selectChat,
    addMessage,
    setCurrentChatId,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = React.useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within a ChatProvider');
  return context;
}
