import React from 'react';
import Icon from '../../../components/AppIcon';
import Button from '../../../components/ui/Button';

const SignUpCard = ({ onGoogleSignUp, isLoading }) => {
  return (
    <div className="w-full max-w-md mx-auto bg-card rounded-xl shadow-modal border border-border p-8">
      {/* Logo and App Name */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-primary rounded-xl flex items-center justify-center mx-auto mb-4">
          <Icon name="TrendingUp" size={32} color="white" />
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">
          CryptoPredictPro
        </h1>
        <p className="text-muted-foreground text-sm">
          AI-Powered Cryptocurrency Predictions
        </p>
      </div>

      {/* Welcome Message for New Users */}
      <div className="text-center mb-8">
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Create Your Account
        </h2>
        <p className="text-muted-foreground text-sm">
          Join thousands of traders making smarter decisions with AI
        </p>
      </div>

      {/* Google OAuth Sign Up Button */}
      <div className="mb-6">
        <Button
          variant="outline"
          size="lg"
          fullWidth
          onClick={onGoogleSignUp}
          loading={isLoading}
          disabled={isLoading}
          className="border-2 hover:bg-muted transition-smooth"
        >
          <div className="flex items-center justify-center">
            <svg
              className="w-5 h-5 mr-3"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            {isLoading ? 'Creating account...' : 'Sign up with Google'}
          </div>
        </Button>
      </div>

      {/* Platform Benefits */}
      <div className="text-center mb-6">
        <div className="bg-muted rounded-lg p-4">
          <div className="flex items-center justify-center mb-3">
            <Icon name="Star" size={20} className="text-accent mr-2" />
            <span className="text-sm font-medium text-foreground">
              Exclusive Platform Access
            </span>
          </div>
          <ul className="text-xs text-muted-foreground space-y-2">
            <li className="flex items-center justify-center">
              <Icon name="Check" size={14} className="text-success mr-2" />
              AI predictions for 10+ cryptocurrencies
            </li>
            <li className="flex items-center justify-center">
              <Icon name="Check" size={14} className="text-success mr-2" />
              Hourly & daily prediction timeframes
            </li>
            <li className="flex items-center justify-center">
              <Icon name="Check" size={14} className="text-success mr-2" />
              Interactive charts with INR pricing
            </li>
            <li className="flex items-center justify-center">
              <Icon name="Check" size={14} className="text-success mr-2" />
              Real-time market data analysis
            </li>
          </ul>
        </div>
      </div>

      {/* Trust Indicators */}
      <div className="text-center mb-6">
        <div className="flex items-center justify-center space-x-6 mb-3">
          <div className="text-center">
            <div className="text-lg font-bold text-foreground">10K+</div>
            <div className="text-xs text-muted-foreground">Active Users</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-foreground">85%</div>
            <div className="text-xs text-muted-foreground">Accuracy Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-foreground">24/7</div>
            <div className="text-xs text-muted-foreground">Market Analysis</div>
          </div>
        </div>
      </div>

      {/* Security Indicators */}
      <div className="text-center">
        <div className="flex items-center justify-center space-x-4 mb-4">
          <div className="flex items-center">
            <Icon name="Shield" size={16} className="text-success mr-1" />
            <span className="text-xs text-muted-foreground">SSL Secured</span>
          </div>
          <div className="flex items-center">
            <Icon name="Lock" size={16} className="text-success mr-1" />
            <span className="text-xs text-muted-foreground">Privacy Protected</span>
          </div>
          <div className="flex items-center">
            <Icon name="Check" size={16} className="text-success mr-1" />
            <span className="text-xs text-muted-foreground">Free to Join</span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          By creating an account, you agree to our{' '}
          <button className="text-primary hover:underline">Terms of Service</button>
          {' '}and{' '}
          <button className="text-primary hover:underline">Privacy Policy</button>
        </p>
      </div>
    </div>
  );
};

export default SignUpCard;