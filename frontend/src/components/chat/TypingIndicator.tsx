import { Card } from '@/components/ui/card';

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <Card className="bg-chat-bubble-ai border-border px-4 py-3 max-w-[70%] mr-4">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-muted-foreground rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full typing-dot"></div>
            <div className="w-2 h-2 bg-muted-foreground rounded-full typing-dot"></div>
          </div>
          <span className="text-sm text-muted-foreground">AI is typing...</span>
        </div>
      </Card>
    </div>
  );
};

export default TypingIndicator;