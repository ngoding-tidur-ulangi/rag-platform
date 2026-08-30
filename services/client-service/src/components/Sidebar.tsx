import React from 'react';
import { Plus, MessageSquare, Trash2 } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Conversation } from '../services/chat';
import clsx from 'clsx';

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
}) => {
  return (
    <div className="w-64 bg-neutral-900 border-r border-neutral-800 flex flex-col h-full">
      <div className="p-4">
        <Button 
          onClick={onNew}
          className="w-full flex items-center justify-start gap-2 bg-neutral-800 hover:bg-neutral-700 text-white border-neutral-700"
          variant="outline"
        >
          <Plus size={16} />
          New Chat
        </Button>
      </div>
      
      <ScrollArea className="flex-1 px-2">
        <div className="flex flex-col gap-1">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={clsx(
                "group flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors",
                activeId === conv.id ? "bg-neutral-800" : "hover:bg-neutral-800/50"
              )}
              onClick={() => onSelect(conv.id)}
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <MessageSquare size={14} className="shrink-0 text-neutral-400" />
                <span className="truncate text-sm text-neutral-200">
                  {conv.title || "Untitled Chat"}
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-400 text-neutral-500 transition-opacity"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};
