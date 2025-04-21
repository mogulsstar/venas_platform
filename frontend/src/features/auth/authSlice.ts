import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import jwtDecode from 'jwt-decode';
import api from '../../services/api';

// Types
interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_admin: boolean;
  is_manager: boolean;
  is_analyst: boolean;
}

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

interface LoginCredentials {
  identifier?: string;
  username?: string;
  email?: string;
  password: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

interface JwtPayload {
  exp: number;
  user_id: number;
}

// Initial state
const initialState: AuthState = {
  token: localStorage.getItem('token'),
  refreshToken: localStorage.getItem('refreshToken'),
  user: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginCredentials, { rejectWithValue }) => {
    try {
      console.log('Attempting login with credentials:', { ...credentials, password: '******' });
      const response = await api.post<LoginResponse>('/users/login/', credentials);
      console.log('Login successful, received tokens');

      // Store tokens in localStorage
      localStorage.setItem('token', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      console.log('Tokens stored in localStorage');

      return response.data;
    } catch (error: any) {
      console.error('Login failed:', error.response?.data);
      return rejectWithValue(error.response?.data?.detail || 'Login failed');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await api.post('/users/logout/');

      // Remove tokens from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');

      return null;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Logout failed');
    }
  }
);

export const refreshAuthToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    const state = getState() as { auth: AuthState };
    const refreshToken = state.auth.refreshToken;

    if (!refreshToken) {
      return rejectWithValue('No refresh token available');
    }

    try {
      const response = await api.post<{ access: string }>('/users/token/refresh/', {
        refresh: refreshToken,
      });

      // Store new token in localStorage
      localStorage.setItem('token', response.data.access);

      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Token refresh failed');
    }
  }
);

export const checkAuth = createAsyncThunk(
  'auth/checkAuth',
  async (_, { dispatch, getState, rejectWithValue }) => {
    const state = getState() as { auth: AuthState };
    const token = state.auth.token;
    console.log('checkAuth - token from state:', token ? 'exists' : 'not found');

    if (!token) {
      console.log('No token available in state');
      return rejectWithValue('No token available');
    }

    try {
      // Check if token is expired
      const decoded = jwtDecode<JwtPayload>(token);
      const currentTime = Date.now() / 1000;
      console.log('Token expiration check:', {
        exp: new Date(decoded.exp * 1000).toISOString(),
        now: new Date(currentTime * 1000).toISOString(),
        isExpired: decoded.exp < currentTime
      });

      if (decoded.exp < currentTime) {
        console.log('Token is expired, attempting to refresh');
        // Token is expired, try to refresh
        await dispatch(refreshAuthToken());
        console.log('Token refresh completed');
      }

      // Get user data
      console.log('Fetching user data');
      const response = await api.get<User>('/users/me/');
      console.log('User data fetched successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Authentication check failed:', error.response?.data);
      return rejectWithValue(error.response?.data?.detail || 'Authentication check failed');
    }
  }
);

// This function is used by ProfilePage.tsx
export const updateUserProfile = createAsyncThunk(
  'auth/updateUserProfile',
  async (userData: Partial<User>, { getState, rejectWithValue }) => {
    try {
      const response = await api.patch<User>('/users/me/', userData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update profile');
    }
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<LoginResponse>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
        state.refreshToken = null;
        state.user = null;
        state.error = action.payload as string;
      })

      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
        state.refreshToken = null;
        state.user = null;
        state.error = null;
      })

      // Refresh token
      .addCase(refreshAuthToken.fulfilled, (state, action: PayloadAction<{ access: string }>) => {
        state.token = action.payload.access;
      })
      .addCase(refreshAuthToken.rejected, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
        state.refreshToken = null;
        state.user = null;
      })

      // Check auth
      .addCase(checkAuth.pending, (state) => {
        state.loading = true;
      })
      .addCase(checkAuth.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(checkAuth.rejected, (state) => {
        state.loading = false;
        state.isAuthenticated = false;
        state.token = null;
        state.refreshToken = null;
        state.user = null;
      })

      // Update user profile
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserProfile.fulfilled, (state, action: PayloadAction<User>) => {
        state.loading = false;
        state.user = action.payload;
        state.error = null;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError } = authSlice.actions;

export default authSlice.reducer;
