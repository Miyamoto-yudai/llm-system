import React from 'react'
import clsx from 'clsx'
import { Toaster } from 'react-hot-toast'
import { DefaultApi, Configuration } from './api-client'
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext'

import Header from './components/Header'
import Footer from './components/Footer'
import Chat from './components/Chat'
import ComparisonMode from './components/ComparisonMode'
import CompanyPage from './pages/Company'
import TermsPage from './pages/Terms'
import PrivacyPolicyPage from './pages/PrivacyPolicy'
import AsctPage from './pages/Asct'
import AuthCallback from './pages/AuthCallback'



const apiBasePath = import.meta.env.VITE_API_URL || 'http://localhost:8080'
const config = new Configuration({ basePath: apiBasePath })
export const apiClient = new DefaultApi(config)



function App() {
  const isComparisonModeEnabled = import.meta.env.VITE_COMPARISON_MODE_ENABLED === 'true'

  return (
    <AuthProvider>
      <div className='flex flex-col min-h-screen w-full'>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              style: {
                background: '#10b981',
              },
            },
            error: {
              style: {
                background: '#ef4444',
              },
            },
          }}
        />
        <Header />
        <div className='flex flex-col flex-1 w-full'>
          <Routes>
            <Route path="/" element={<Chat />} />
            {isComparisonModeEnabled && (
              <Route path="/comparison" element={<ComparisonMode />} />
            )}
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/auth/error" element={<AuthCallback />} />
            <Route path="/company" element={<CompanyPage />} />
            <Route path="/terms" element={<TermsPage />} />
            <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
            <Route path="/asct" element={<AsctPage />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </AuthProvider>
  )
}

export default App
