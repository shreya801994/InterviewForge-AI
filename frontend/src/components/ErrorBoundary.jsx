import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[16rem] p-8 text-center">
          <h2 className="text-white text-lg font-semibold mb-2">Something went wrong</h2>
          <p className="text-gray-400 text-sm mb-4">
            The dashboard encountered an unexpected error. Please refresh the page and try again.
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
