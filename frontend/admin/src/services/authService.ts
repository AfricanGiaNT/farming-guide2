import { LoginCredentials, User } from '../types';

class AuthService {
  private baseUrl = '/api/admin';

  async login(credentials: LoginCredentials) {
    // Development mode mock authentication
    if (process.env.NODE_ENV === 'development' || true) {
      await new Promise(resolve => setTimeout(resolve, 500)); // Simulate network delay
      
      return {
        user: {
          id: '1',
          email: credentials.email,
          name: 'Admin User',
          role: 'admin' as const,
          lastLogin: new Date().toISOString(),
        },
        token: 'mock_jwt_token_' + Date.now(),
      };
    }

    try {
      const response = await fetch(`${this.baseUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Login failed');
      }

      const data = await response.json();
      return {
        user: data.user as User,
        token: data.token as string,
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    try {
      const token = localStorage.getItem('admin_token');
      if (token) {
        await fetch(`${this.baseUrl}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
  }

  async getCurrentUser(): Promise<User> {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      throw new Error('No token found');
    }

    // Development mode mock user
    if (process.env.NODE_ENV === 'development' || true) {
      await new Promise(resolve => setTimeout(resolve, 200));
      
      return {
        id: '1',
        email: 'admin@example.com',
        name: 'Admin User',
        role: 'admin',
        lastLogin: new Date().toISOString(),
      };
    }

    try {
      const response = await fetch(`${this.baseUrl}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get user info');
      }

      const data = await response.json();
      return data.user as User;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  async refreshToken(): Promise<string> {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      throw new Error('No token found');
    }

    try {
      const response = await fetch(`${this.baseUrl}/refresh-token`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }

      const data = await response.json();
      return data.token as string;
    } catch (error) {
      console.error('Refresh token error:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();