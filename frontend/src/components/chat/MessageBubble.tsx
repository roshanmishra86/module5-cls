import { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { Message } from '@/types/chat';
import AgentBadge from './AgentBadge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble = ({ message }: MessageBubbleProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy message:', error);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`
      flex w-full mb-4 message-slide-in
      ${message.isUser ? 'justify-end' : 'justify-start'}
    `}>
      <div className={`
        max-w-[70%] min-w-[100px]
        ${message.isUser ? 'order-1' : 'order-2'}
      `}>
        {/* Agent badge for AI messages */}
        {!message.isUser && message.agentType && (
          <div className="mb-2">
            <AgentBadge agentType={message.agentType} />
          </div>
        )}
        
        {/* Message bubble */}
        <Card className={`
          relative group transition-all duration-200 hover:shadow-md
          ${message.isUser 
            ? 'bg-chat-bubble-user text-chat-bubble-user-foreground ml-4 border-primary/20' 
            : 'bg-chat-bubble-ai text-chat-bubble-ai-foreground mr-4 border-border hover:border-primary/20'
          }
        `}>
          <div className="px-4 py-3">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
          </div>
          
          {/* Copy button for AI messages */}
          {!message.isUser && (
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={handleCopy}
              className="absolute -right-1 -top-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-card border border-border hover:bg-accent hover:border-primary/20 shadow-sm"
            >
              {copied ? (
                <Check className="h-3 w-3 text-success" />
              ) : (
                <Copy className="h-3 w-3" />
              )}
            </Button>
          )}
        </Card>
        
        {/* Timestamp */}
        <div className={`
          mt-1 text-xs text-muted-foreground
          ${message.isUser ? 'text-right mr-4' : 'text-left ml-4'}
        `}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;