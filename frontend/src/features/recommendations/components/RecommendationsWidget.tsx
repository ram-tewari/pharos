/**
 * RecommendationsWidget Component
 * Displays personalized "For You" recommendations
 */

import { useQuery } from '@tanstack/react-query';
import { Sparkles, BookOpen, FileText, Globe } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getRecommendations } from '../api';

interface RecommendationsWidgetProps {
  onRecommendationClick: (id: string) => void;
}

const RESOURCE_TYPE_CONFIG = {
  article: { icon: FileText, color: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' },
  paper: { icon: FileText, color: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300' },
  book: { icon: BookOpen, color: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' },
  website: { icon: Globe, color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
  default: { icon: FileText, color: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300' },
};

export function RecommendationsWidget({ onRecommendationClick }: RecommendationsWidgetProps) {
  const { data: recommendations, isLoading, error } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => getRecommendations(6),
    staleTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  if (error) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <p className="text-sm">Recommendations unavailable</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <h2 className="text-2xl font-bold">For You</h2>
        </div>
        <p className="text-muted-foreground">
          Personalized recommendations based on your interests
        </p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i} className="p-4 space-y-3 animate-pulse">
              <div className="h-5 bg-secondary rounded w-3/4" />
              <div className="space-y-2">
                <div className="h-4 bg-secondary rounded" />
                <div className="h-4 bg-secondary rounded w-5/6" />
              </div>
              <div className="flex gap-2">
                <div className="h-5 bg-secondary rounded w-16" />
                <div className="h-5 bg-secondary rounded w-20" />
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Recommendations Grid */}
      {!isLoading && recommendations && recommendations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recommendations.map((rec) => {
            const typeConfig = RESOURCE_TYPE_CONFIG[rec.resource_type as keyof typeof RESOURCE_TYPE_CONFIG] || RESOURCE_TYPE_CONFIG.default;
            const Icon = typeConfig.icon;

            return (
              <Card
                key={rec.id}
                className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => onRecommendationClick(rec.id)}
              >
                <div className="space-y-3">
                  {/* Title */}
                  <h3 className="font-semibold line-clamp-2">
                    {rec.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {rec.description}
                  </p>

                  {/* Reason Badge */}
                  <Badge variant="secondary" className="text-xs">
                    <Sparkles className="h-3 w-3 mr-1" />
                    {rec.reason}
                  </Badge>

                  {/* Metadata */}
                  <div className="flex items-center gap-2 flex-wrap text-xs">
                    <Badge variant="secondary" className={typeConfig.color}>
                      <Icon className="h-3 w-3 mr-1" />
                      {rec.resource_type}
                    </Badge>
                    
                    <Badge variant="outline">
                      Quality: {Math.round(rec.quality_score * 100)}%
                    </Badge>

                    <span className="text-muted-foreground ml-auto">
                      {formatDate(rec.created_at)}
                    </span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && recommendations && recommendations.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p className="text-sm">No recommendations available yet</p>
          <p className="text-xs mt-2">Start exploring resources to get personalized suggestions</p>
        </div>
      )}
    </div>
  );
}
