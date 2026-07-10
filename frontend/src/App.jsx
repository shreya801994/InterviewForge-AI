import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './layouts/DashboardLayout';
import ErrorBoundary from './components/ErrorBoundary';

// Public pages (eager)
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';

// Heavy routes (lazy-loaded)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ResumeUpload = lazy(() => import('./pages/ResumeUpload'));
const InterviewSetup = lazy(() => import('./pages/InterviewSetup'));
const InterviewSession = lazy(() => import('./pages/InterviewSession'));
const ReportDetails = lazy(() => import('./pages/ReportDetails'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[16rem]">
      <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

import GlobalNetworkBanner from './components/GlobalNetworkBanner';

export default function App() {
  return (
    <AuthProvider>
      <GlobalNetworkBanner />
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* Protected dashboard routes */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route
                path="/dashboard"
                element={
                  <ErrorBoundary>
                    <Dashboard />
                  </ErrorBoundary>
                }
              />
              <Route path="/resume" element={<ResumeUpload />} />
              <Route path="/interview/setup" element={<InterviewSetup />} />
              <Route path="/interview/:sessionId" element={<InterviewSession />} />
              <Route path="/report/:sessionId" element={<ReportDetails />} />
            </Route>

            {/* 404 fallback */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  );
}
