import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// 定义监控数据类型
export interface MonitorData {
  system_status: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    uptime: number;
  };
  active_tasks: Array<{
    id: number;
    name: string;
    type: string;
    status: string;
    progress: number;
    started_at: string;
    estimated_completion: string;
  }>;
  recent_errors: Array<{
    id: number;
    timestamp: string;
    level: string;
    message: string;
    source: string;
  }>;
  performance_metrics: {
    api_response_time: number;
    database_query_time: number;
    analysis_execution_time: number;
  };
}

// 定义状态类型
interface MonitorState {
  data: MonitorData | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: MonitorState = {
  data: null,
  loading: false,
  error: null,
};

// 异步 thunk 获取监控数据
export const fetchMonitorData = createAsyncThunk(
  'monitor/fetchMonitorData',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/monitor/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取监控数据失败');
    }
  }
);

// 创建 slice
const monitorSlice = createSlice({
  name: 'monitor',
  initialState,
  reducers: {
    clearMonitorData: (state) => {
      state.data = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMonitorData.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchMonitorData.fulfilled, (state, action: PayloadAction<MonitorData>) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchMonitorData.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearMonitorData, clearError } = monitorSlice.actions;

export default monitorSlice.reducer;
