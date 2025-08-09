import { useState, useEffect, useRef } from 'react';
import { Trash2, MessageSquare } from 'lucide-react';
import { Message, AgentType } from '@/types/chat';
import { chatApi } from '@/services/chatApi';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import ErrorMessage from './ErrorMessage';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/enhanced-badge';
import { useToast } from '@/hooks/use-toast';

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const generateMessageId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const mapAgentType = (agentTypeString: string): AgentType => {
    const normalizedType = agentTypeString.toLowerCase();
    if (normalizedType.includes('product')) return 'Product Specialist';
    if (normalizedType.includes('technical')) return 'Technical Support';
    return 'General Support';
  };

  const handleSendMessage = async (content: string) => {
    // Clear any existing errors
    setError(null);

    // Add user message
    const userMessage: Message = {
      id: generateMessageId(),
      content,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(content);
      
      // Add AI response
      const aiMessage: Message = {
        id: generateMessageId(),
        content: response.message,
        isUser: false,
        timestamp: new Date(),
        agentType: mapAgentType(response.agent_type),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setError(errorMessage);
      
      toast({
        title: 'Message Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setError(null);
    toast({
      title: 'Chat Cleared',
      description: 'All messages have been cleared.',
    });
  };

  const handleRetry = () => {
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background to-background/90">
      {/* Header */}
      <Card className="rounded-none border-x-0 border-t-0 bg-card/95 backdrop-blur-sm shadow-sm">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-primary to-primary/80 rounded-xl shadow-lg">
              <MessageSquare className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
                AI Customer Support
              </h1>
              <p className="text-sm text-muted-foreground">Get instant help from our AI assistants</p>
            </div>
          </div>
          
          {messages.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearChat}
              className="flex items-center space-x-2 hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20"
            >
              <Trash2 className="h-4 w-4" />
              <span>Clear Chat</span>
            </Button>
          )}
        </div>
      </Card>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-background/50 to-background chat-scroll">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl mb-6 shadow-lg">
              <MessageSquare className="h-10 w-10 text-primary" />
            </div>
            <h2 className="text-2xl font-semibold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent mb-3">
              Welcome to AI Customer Support
            </h2>
            <p className="text-muted-foreground max-w-md mb-8 leading-relaxed">
              Ask any question about our products or services. Our AI specialists are here to help!
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm max-w-2xl">
              <Card className="p-4 border-border hover:border-primary/20 transition-all duration-200 hover:shadow-md bg-card/50 backdrop-blur-sm">
                <Badge variant="general" className="mb-2">General Support</Badge>
                <div className="text-muted-foreground">Account & billing questions</div>
              </Card>
              <Card className="p-4 border-border hover:border-success/20 transition-all duration-200 hover:shadow-md bg-card/50 backdrop-blur-sm">
                <Badge variant="product" className="mb-2">Product Specialist</Badge>
                <div className="text-muted-foreground">Product information & features</div>
              </Card>
              <Card className="p-4 border-border hover:border-warning/20 transition-all duration-200 hover:shadow-md bg-card/50 backdrop-blur-sm">
                <Badge variant="technical" className="mb-2">Technical Support</Badge>
                <div className="text-muted-foreground">Technical issues & troubleshooting</div>
              </Card>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className="group">
            <MessageBubble message={message} />
          </div>
        ))}

        {isLoading && <TypingIndicator />}
        {error && <ErrorMessage message={error} onRetry={handleRetry} />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <MessageInput 
        onSendMessage={handleSendMessage} 
        disabled={isLoading} 
      />
    </div>
  );
};

export default ChatInterface;