import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// 定义帮助文档类型
export interface HelpArticle {
  id: number;
  title: string;
  content: string;
  category: string;
  tags: string[];
  created_at: string;
  updated_at: string;
}

// 定义状态类型
interface HelpState {
  articles: HelpArticle[];
  currentArticle: HelpArticle | null;
  categories: string[];
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: HelpState = {
  articles: [],
  currentArticle: null,
  categories: [],
  loading: false,
  error: null,
};

// 异步 thunk 获取所有帮助文档
export const fetchHelpArticles = createAsyncThunk(
  'help/fetchHelpArticles',
  async (_, { rejectWithValue }) => {
    try {
      console.log('Fetching help articles');
      const response = await api.get('/help/articles/');
      console.log('Help articles fetched successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch help articles:', error.response?.status, error.response?.data);
      // 如果是 404 或 401 错误，返回空数组而不是拒绝 Promise
      if (error.response?.status === 404 || error.response?.status === 401) {
        return [];
      }
      return rejectWithValue(error.response?.data?.detail || '获取帮助文档失败');
    }
  }
);

// 异步 thunk 获取单个帮助文档
export const fetchHelpArticle = createAsyncThunk(
  'help/fetchHelpArticle',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/help/articles/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取帮助文档详情失败');
    }
  }
);

// 异步 thunk 获取所有分类
export const fetchHelpCategories = createAsyncThunk(
  'help/fetchHelpCategories',
  async (_, { rejectWithValue }) => {
    try {
      console.log('Fetching help categories');
      const response = await api.get('/help/categories/');
      console.log('Help categories fetched successfully:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch help categories:', error.response?.status, error.response?.data);
      // 如果是 404 或 401 错误，返回空数组而不是拒绝 Promise
      if (error.response?.status === 404 || error.response?.status === 401) {
        return [];
      }
      return rejectWithValue(error.response?.data?.detail || '获取帮助分类失败');
    }
  }
);

// 创建 slice
const helpSlice = createSlice({
  name: 'help',
  initialState,
  reducers: {
    clearCurrentArticle: (state) => {
      state.currentArticle = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取所有帮助文档
      .addCase(fetchHelpArticles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHelpArticles.fulfilled, (state, action: PayloadAction<HelpArticle[]>) => {
        state.loading = false;
        state.articles = action.payload;
      })
      .addCase(fetchHelpArticles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取单个帮助文档
      .addCase(fetchHelpArticle.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHelpArticle.fulfilled, (state, action: PayloadAction<HelpArticle>) => {
        state.loading = false;
        state.currentArticle = action.payload;
      })
      .addCase(fetchHelpArticle.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取所有分类
      .addCase(fetchHelpCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchHelpCategories.fulfilled, (state, action: PayloadAction<string[]>) => {
        state.loading = false;
        state.categories = action.payload;
      })
      .addCase(fetchHelpCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearCurrentArticle, clearError } = helpSlice.actions;

export default helpSlice.reducer;
