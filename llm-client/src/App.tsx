import React from 'react'
import clsx from 'clsx'
import { Toaster } from 'react-hot-toast'
import { DefaultApi, Configuration } from './api-client'
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext'

import Header from './components/Header'
import Footer from './components/Footer'
import Chat from './components/Chat'
import CompanyPage from './pages/Company'
import TermsPage from './pages/Terms'
import PrivacyPolicyPage from './pages/PrivacyPolicy'
import AsctPage from './pages/Asct'
import AuthCallback from './pages/AuthCallback'



const config = new Configuration({ basePath: 'http://notebook.lawflow.jp:8000' }) // TODO: This is for dev
export const apiClient = new DefaultApi(config)



function App() {
  return (
    <AuthProvider>
      <div className='flex flex-col h-full w-full justify-center'>
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
        <div className='flex flex-col h-full w-full'>
          <Routes><Route path="/" element={<Chat />} /></Routes>
          <Routes><Route path="/auth/callback" element={<AuthCallback />} /></Routes>
          <Routes><Route path="/auth/error" element={<AuthCallback />} /></Routes>
          <Routes><Route path="/company" element={<CompanyPage />} /></Routes>
          <Routes><Route path="/terms" element={<TermsPage />} /></Routes>
          <Routes><Route path="/privacy-policy" element={<PrivacyPolicyPage />} /></Routes>
          <Routes><Route path="/asct" element={<AsctPage />} /></Routes>
        </div>
        <Footer />
      </div>
    </AuthProvider>
  )
}

export default App
