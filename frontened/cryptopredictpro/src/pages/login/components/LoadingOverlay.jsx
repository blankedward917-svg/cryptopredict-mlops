import React from 'react';
import Icon from '../../../components/AppIcon';

const LoadingOverlay = ({ isVisible, message = "Authenticating..." }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-card rounded-xl shadow-modal border border-border p-8 max-w-sm mx-4">
        <div className="text-center">
          <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Icon name="Loader2" size={24} color="white" className="animate-spin" />
          </div>
          <h3 className="text-lg font-semibold text-foreground mb-2">
            {message}
          </h3>
          <p className="text-sm text-muted-foreground">
            Please wait while we verify your credentials...
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoadingOverlay;