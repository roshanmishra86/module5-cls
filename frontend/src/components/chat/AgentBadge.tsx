import { AgentType } from '@/types/chat';
import { Badge } from '@/components/ui/enhanced-badge';

interface AgentBadgeProps {
  agentType: AgentType;
}

const AgentBadge = ({ agentType }: AgentBadgeProps) => {
  const getBadgeVariant = (type: AgentType) => {
    switch (type) {
      case 'General Support':
        return 'general';
      case 'Product Specialist':
        return 'product';
      case 'Technical Support':
        return 'technical';
      default:
        return 'general';
    }
  };

  return (
    <Badge variant={getBadgeVariant(agentType as any)} className="shadow-sm">
      {agentType}
    </Badge>
  );
};

export default AgentBadge;