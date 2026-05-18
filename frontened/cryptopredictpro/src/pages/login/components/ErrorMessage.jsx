import React from 'react';
import Icon from '../../../components/AppIcon';

const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div className="w-full max-w-md mx-auto mb-6">
      <div className="bg-error/10 border border-error/20 rounded-lg p-4">
        <div className="flex items-start">
          <Icon name="AlertCircle" size={20} className="text-error mr-3 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-error mb-1">
              Authentication Failed
            </h3>
            <p className="text-sm text-error/80">
              {error}
            </p>
          </div>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="ml-2 text-error/60 hover:text-error transition-smooth"
            >
              <Icon name="X" size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;