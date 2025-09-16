import { api } from './api.config'
import { storage } from '../utils/storage'

interface GoogleAuthResponse {
  auth_url: string
}

export const oauthService = {
  async getGoogleAuthUrl(): Promise<string> {
    const response = await api.get<GoogleAuthResponse>('/api/auth/google')
    return response.data.auth_url
  },

  async handleGoogleCallback(code: string): Promise<void> {
    const response = await api.post('/api/auth/google/token', { code })
    const data = response.data
    storage.setToken(data.access_token)
    storage.setUser(data.user)
  },

  initiateGoogleLogin(): void {
    // This will redirect the user to Google's OAuth page
    oauthService.getGoogleAuthUrl().then(url => {
      window.location.href = url
    })
  }
}