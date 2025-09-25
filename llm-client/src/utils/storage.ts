import Cookies from 'js-cookie'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'user_info'

export const storage = {
  getToken: (): string | undefined => {
    return Cookies.get(TOKEN_KEY)
  },

  setToken: (token: string): void => {
    Cookies.set(TOKEN_KEY, token, { expires: 1 }) // 1 day
  },

  removeToken: (): void => {
    Cookies.remove(TOKEN_KEY)
  },

  getUser: () => {
    const user = localStorage.getItem(USER_KEY)
    return user ? JSON.parse(user) : null
  },

  setUser: (user: any): void => {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },

  removeUser: (): void => {
    localStorage.removeItem(USER_KEY)
  },

  clear: (): void => {
    storage.removeToken()
    storage.removeUser()
  }
}