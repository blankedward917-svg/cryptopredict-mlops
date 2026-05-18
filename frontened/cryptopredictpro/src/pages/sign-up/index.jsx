import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ErrorMessage from '../login/components/ErrorMessage';
import LoadingOverlay from '../login/components/LoadingOverlay';
import SignUpCard from './components/SignUpCard';

const SignUp = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showLoadingOverlay, setShowLoadingOverlay] = useState(false);
  const navigate = useNavigate();

  // Mock new user data for successful registration
  const mockNewUser = {
    id: "user_new_" + Date.now(),
    email: "",
    name: "",
    provider: "google",
    avatar: "",
    createdAt: new Date()?.toISOString(),
    lastLogin: new Date()?.toISOString(),
    isNewUser: true
  };

  // Check if user is already logged in
  useEffect(() => {
    const savedUser = localStorage.getItem('cryptoUser');
    if (savedUser) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleGoogleSignUp = async () => {
    setIsLoading(true);
    setError('');
    setShowLoadingOverlay(true);

    try {
      // Simulate OAuth popup and registration process
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulate different signup scenarios
      const signupScenarios = [
        { 
          success: true, 
          user: {
            ...mockNewUser,
            email: "new.user@gmail.com",
            name: "New User",
            avatar: "https://randomuser.me/api/portraits/men/45.jpg"
          }
        },
        { success: false, error: "Registration was cancelled by the user." },
        { success: false, error: "This email is already registered. Please sign in instead." },
        { success: false, error: "Network error occurred. Please check your internet connection." },
        { success: false, error: "Google OAuth service is temporarily unavailable." }
      ];

      // 70% success rate for demo purposes
      const scenario = Math.random() < 0.7 ? signupScenarios?.[0] : signupScenarios?.[Math.floor(Math.random() * 4) + 1];

      if (scenario?.success) {
        // Store user data in localStorage
        localStorage.setItem('cryptoUser', JSON.stringify(scenario?.user));
        localStorage.setItem('authToken', 'mock_jwt_token_' + Date.now());
        localStorage.setItem('isNewUser', 'true');
        
        // Navigate to dashboard (or onboarding flow for new users)
        navigate('/dashboard');
      } else {
        setError(scenario?.error);
        // If email already exists, suggest login
        if (scenario?.error?.includes('already registered')) {
          setTimeout(() => {
            setError(prev => prev + ' Would you like to sign in instead?');
          }, 1000);
        }
      }
    } catch (err) {
      setError("An unexpected error occurred during registration. Please try again.");
    } finally {
      setIsLoading(false);
      setShowLoadingOverlay(false);
    }
  };

  const handleDismissError = () => {
    setError('');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-primary/5"></div>
      
      {/* Main Content */}
      <div className="relative w-full max-w-md">
        {/* Back to Landing */}
        <div className="text-center mb-6">
          <Link 
            to="/" 
            className="inline-flex items-center text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to home
          </Link>
        </div>

        {/* Error Message */}
        <ErrorMessage 
          error={error} 
          onDismiss={handleDismissError} 
        />

        {/* Sign Up Card */}
        <SignUpCard 
          onGoogleSignUp={handleGoogleSignUp}
          isLoading={isLoading}
        />

        {/* Already have account */}
        <div className="text-center mt-6">
          <p className="text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Sign in here
            </Link>
          </p>
        </div>

        {/* Additional Info */}
        <div className="text-center mt-4">
          <p className="text-xs text-muted-foreground">
            Questions about our platform?{' '}
            <Link to="/" className="text-primary hover:underline">
              Learn more
            </Link>
          </p>
        </div>
      </div>

      {/* Loading Overlay */}
      <LoadingOverlay 
        isVisible={showLoadingOverlay}
        message="Creating your account..."
      />
    </div>
  );
};

export default SignUp;