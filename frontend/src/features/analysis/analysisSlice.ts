import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// 定义分析任务类型
export interface AnalysisTask {
  id: number;
  name: string;
  description: string;
  analysis_type: string;
  status: string;
  results?: any;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  execution_time?: number;
  created_by: {
    id: number;
    username: string;
  };
  template?: {
    id: number;
    name: string;
  };
  test_case?: {
    id: number;
    name: string;
  };
  project?: {
    id: number;
    name: string;
  };
}

// 定义状态类型
interface AnalysisState {
  tasks: AnalysisTask[];
  currentTask: AnalysisTask | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: AnalysisState = {
  tasks: [],
  currentTask: null,
  loading: false,
  error: null,
};

// 异步 thunk 获取所有分析任务
export const fetchAnalysisTasks = createAsyncThunk(
  'analysis/fetchAnalysisTasks',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/analysis/tasks/');
      return response.data;
    } catch (error: any) {
      // 如果是 404 或 401 错误，返回空数组而不是拒绝 Promise
      if (error.response?.status === 404 || error.response?.status === 401) {
        return [];
      }
      return rejectWithValue(error.response?.data?.detail || '获取分析任务失败');
    }
  }
);

// 异步 thunk 获取单个分析任务
export const fetchAnalysisTask = createAsyncThunk(
  'analysis/fetchAnalysisTask',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/analysis/tasks/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取分析任务详情失败');
    }
  }
);

// 异步 thunk 创建分析任务
export const createAnalysisTask = createAsyncThunk(
  'analysis/createAnalysisTask',
  async (task: Partial<AnalysisTask>, { rejectWithValue }) => {
    try {
      const response = await api.post('/analysis/tasks/', task);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '创建分析任务失败');
    }
  }
);

// 异步 thunk 更新分析任务
export const updateAnalysisTask = createAsyncThunk(
  'analysis/updateAnalysisTask',
  async ({ id, data }: { id: number; data: Partial<AnalysisTask> }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/analysis/tasks/${id}/`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '更新分析任务失败');
    }
  }
);

// 异步 thunk 删除分析任务
export const deleteAnalysisTask = createAsyncThunk(
  'analysis/deleteAnalysisTask',
  async (id: number, { rejectWithValue }) => {
    try {
      await api.delete(`/analysis/tasks/${id}/`);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '删除分析任务失败');
    }
  }
);

// 异步 thunk 运行分析任务
export const runAnalysisTask = createAsyncThunk(
  'analysis/runAnalysisTask',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.post(`/analysis/tasks/${id}/run/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '运行分析任务失败');
    }
  }
);

// 创建 slice
const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    clearCurrentTask: (state) => {
      state.currentTask = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取所有分析任务
      .addCase(fetchAnalysisTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalysisTasks.fulfilled, (state, action: PayloadAction<AnalysisTask[]>) => {
        state.loading = false;
        state.tasks = action.payload;
      })
      .addCase(fetchAnalysisTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取单个分析任务
      .addCase(fetchAnalysisTask.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnalysisTask.fulfilled, (state, action: PayloadAction<AnalysisTask>) => {
        state.loading = false;
        state.currentTask = action.payload;
      })
      .addCase(fetchAnalysisTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 创建分析任务
      .addCase(createAnalysisTask.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAnalysisTask.fulfilled, (state, action: PayloadAction<AnalysisTask>) => {
        state.loading = false;
        state.tasks.push(action.payload);
      })
      .addCase(createAnalysisTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 更新分析任务
      .addCase(updateAnalysisTask.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAnalysisTask.fulfilled, (state, action: PayloadAction<AnalysisTask>) => {
        state.loading = false;
        const index = state.tasks.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
        if (state.currentTask?.id === action.payload.id) {
          state.currentTask = action.payload;
        }
      })
      .addCase(updateAnalysisTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 删除分析任务
      .addCase(deleteAnalysisTask.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteAnalysisTask.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.tasks = state.tasks.filter((t) => t.id !== action.payload);
        if (state.currentTask?.id === action.payload) {
          state.currentTask = null;
        }
      })
      .addCase(deleteAnalysisTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 运行分析任务
      .addCase(runAnalysisTask.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(runAnalysisTask.fulfilled, (state, action: PayloadAction<AnalysisTask>) => {
        state.loading = false;
        const index = state.tasks.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
        if (state.currentTask?.id === action.payload.id) {
          state.currentTask = action.payload;
        }
      })
      .addCase(runAnalysisTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearCurrentTask, clearError } = analysisSlice.actions;

export default analysisSlice.reducer;
