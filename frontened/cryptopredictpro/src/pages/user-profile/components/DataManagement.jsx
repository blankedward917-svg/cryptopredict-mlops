import React, { useState } from 'react';
import Icon from '../../../components/AppIcon';
import Button from '../../../components/ui/Button';

const DataManagement = ({ user }) => {
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const handleExportData = async () => {
    setIsExporting(true);
    
    // Simulate data export process
    setTimeout(() => {
      const userData = {
        profile: {
          id: user?.id,
          name: user?.name,
          email: user?.email,
          provider: user?.provider,
          createdAt: user?.createdAt,
          lastLogin: user?.lastLogin
        },
        exportedAt: new Date()?.toISOString(),
        dataTypes: ['Profile Information', 'Account Activity', 'Prediction History']
      };
      
      const dataStr = JSON.stringify(userData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `cryptopredictpro-data-${user?.id}.json`;
      document.body?.appendChild(link);
      link?.click();
      document.body?.removeChild(link);
      URL.revokeObjectURL(url);
      
      setIsExporting(false);
    }, 2000);
  };

  const handleDeleteAccount = () => {
    setShowDeleteConfirm(true);
  };

  const handleConfirmDelete = () => {
    // In a real app, this would call an API to delete the account
    alert('Account deletion would be processed. This is a demo.');
    setShowDeleteConfirm(false);
  };

  const dataCategories = [
    {
      title: 'Profile Information',
      description: 'Name, email, authentication details',
      icon: 'User',
      size: '2.1 KB'
    },
    {
      title: 'Account Activity',
      description: 'Login history, session data',
      icon: 'Activity',
      size: '15.3 KB'
    },
    {
      title: 'Prediction History',
      description: 'Generated predictions and results',
      icon: 'TrendingUp',
      size: '45.7 KB'
    },
    {
      title: 'Application Settings',
      description: 'Preferences and configurations',
      icon: 'Settings',
      size: '1.2 KB'
    }
  ];

  return (
    <div className="bg-card rounded-lg shadow-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-foreground">
          Data Management
        </h2>
        <div className="text-sm text-muted-foreground">
          GDPR Compliant
        </div>
      </div>
      {/* Data Categories */}
      <div className="space-y-4 mb-6">
        <h3 className="text-lg font-medium text-foreground">
          Your Data Categories
        </h3>
        
        {dataCategories?.map((category, index) => (
          <div key={index} className="flex items-center justify-between p-4 rounded-lg border border-border">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                <Icon name={category?.icon} size={18} className="text-muted-foreground" />
              </div>
              <div>
                <div className="text-sm font-medium text-foreground">
                  {category?.title}
                </div>
                <div className="text-sm text-muted-foreground">
                  {category?.description}
                </div>
              </div>
            </div>
            
            <div className="text-xs text-muted-foreground font-mono">
              {category?.size}
            </div>
          </div>
        ))}
      </div>
      {/* Data Actions */}
      <div className="border-t border-border pt-6">
        <h3 className="text-lg font-medium text-foreground mb-4">
          Data Actions
        </h3>
        
        <div className="space-y-4">
          {/* Export Data */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-muted/30">
            <div className="flex items-center space-x-3">
              <Icon name="Download" size={20} className="text-primary" />
              <div>
                <div className="text-sm font-medium text-foreground">
                  Export Your Data
                </div>
                <div className="text-sm text-muted-foreground">
                  Download all your data in JSON format
                </div>
              </div>
            </div>
            
            <Button
              variant="outline"
              onClick={handleExportData}
              loading={isExporting}
              iconName="Download"
              iconPosition="left"
            >
              {isExporting ? 'Exporting...' : 'Export'}
            </Button>
          </div>

          {/* Delete Account */}
          <div className="flex items-center justify-between p-4 rounded-lg bg-destructive/5 border border-destructive/20">
            <div className="flex items-center space-x-3">
              <Icon name="Trash2" size={20} className="text-destructive" />
              <div>
                <div className="text-sm font-medium text-foreground">
                  Delete Account
                </div>
                <div className="text-sm text-muted-foreground">
                  Permanently delete your account and all data
                </div>
              </div>
            </div>
            
            <Button
              variant="destructive"
              onClick={handleDeleteAccount}
              iconName="Trash2"
              iconPosition="left"
            >
              Delete
            </Button>
          </div>
        </div>
      </div>
      {/* Privacy Notice */}
      <div className="mt-6 p-4 bg-muted/50 rounded-lg">
        <div className="flex items-start space-x-3">
          <Icon name="Shield" size={16} className="text-primary mt-0.5" />
          <div className="text-sm text-muted-foreground">
            <p className="font-medium text-foreground mb-1">Data Privacy</p>
            <p>Your data is processed in accordance with our Privacy Policy and GDPR regulations. You have the right to access, modify, or delete your personal data at any time.</p>
          </div>
        </div>
      </div>
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-lg shadow-modal max-w-md w-full p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-destructive/10 rounded-lg flex items-center justify-center">
                <Icon name="AlertTriangle" size={20} className="text-destructive" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">
                  Delete Account
                </h3>
                <p className="text-sm text-muted-foreground">
                  This action cannot be undone
                </p>
              </div>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-muted-foreground mb-3">
                Are you sure you want to permanently delete your account? This will:
              </p>
              <ul className="text-sm text-muted-foreground space-y-1 ml-4">
                <li>• Delete all your profile information</li>
                <li>• Remove all prediction history</li>
                <li>• Cancel any active sessions</li>
                <li>• This action cannot be reversed</li>
              </ul>
            </div>
            
            <div className="flex gap-3">
              <Button
                variant="destructive"
                onClick={handleConfirmDelete}
                className="flex-1"
              >
                Delete Account
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataManagement;