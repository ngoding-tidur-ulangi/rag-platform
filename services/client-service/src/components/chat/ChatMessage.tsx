import React from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import clsx from 'clsx';
import { HoverCard, HoverCardContent, HoverCardTrigger } from '../ui/hover-card';
import { surahs } from '../../constants/surahs';

interface Message {
  messager: string;
  message: string;
  resources: any[];
}

interface ChatMessageProps {
  item: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ item }) => {
  return (
    <div className={clsx(item.messager === "USER" && "flex justify-end")}>
      <div className={clsx(
        "max-w-xl w-[90%] prose prose-invert prose-sm",
        item.messager === "USER" && "bg-neutral-700 p-4 rounded-2xl"
      )}>
        <Markdown remarkPlugins={[remarkGfm]}>
          {item.message}
        </Markdown>
        {item.resources && item.resources.length > 0 && (
          <div className="flex max-w-3xl flex-wrap gap-2 mt-4">
            {item.resources.map((resource: any, rIdx: number) => (
              <HoverCard key={rIdx}>
                <HoverCardTrigger asChild>
                  <span className="block bg-neutral-500 px-2 py-1 rounded-full text-xs hover:cursor-pointer">
                    Q.S {surahs.find(s => s.number === resource.surah_no)?.name} {resource.first_ayah_no_surah}
                  </span>
                </HoverCardTrigger>
                <HoverCardContent className="w-80 bg-neutral-900 border-neutral-700 text-neutral-200">
                  <div className="flex flex-col gap-2">
                    <p className="text-xs italic">"{resource.ayah_en}"</p>
                  </div>
                </HoverCardContent>
              </HoverCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
