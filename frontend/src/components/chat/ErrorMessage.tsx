import { AlertCircle, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

const ErrorMessage = ({ message, onRetry }: ErrorMessageProps) => {
  return (
    <Card className="mx-4 my-2 p-4 bg-destructive/5 border-destructive/20">
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <AlertCircle className="h-5 w-5 text-destructive" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm text-destructive font-medium">{message}</p>
        </div>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="border-destructive/20 text-destructive hover:bg-destructive/10 hover:border-destructive/30"
          >
            <RefreshCcw className="h-3 w-3 mr-1" />
            Retry
          </Button>
        )}
      </div>
    </Card>
  );
};

export default ErrorMessage;