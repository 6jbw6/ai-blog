import { request } from './request'
import type { TokenOut, User } from '@/types'

export const loginApi = (data: { username: string; password: string }) => {
  return request<TokenOut>({
    url: '/auth/login',
    method: 'POST',
    data
  })
}

export const registerApi = (data: { username: string; password: string; email: string; nickname?: string }) => {
  return request<User>({
    url: '/auth/register',
    method: 'POST',
    data
  })
}

export const getMeApi = () => {
  return request<User>({
    url: '/auth/me',
    method: 'GET'
  })
}
