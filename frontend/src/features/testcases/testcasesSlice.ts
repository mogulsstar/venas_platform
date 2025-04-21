import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// 定义测试用例类型
export interface TestCase {
  id: number;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  };
  regulation?: {
    id: number;
    name: string;
  };
  project?: {
    id: number;
    name: string;
  };
}

// 定义状态类型
interface TestCasesState {
  testCases: TestCase[];
  currentTestCase: TestCase | null;
  loading: boolean;
  error: string | null;
}

// 初始状态
const initialState: TestCasesState = {
  testCases: [],
  currentTestCase: null,
  loading: false,
  error: null,
};

// 异步 thunk 获取所有测试用例
export const fetchTestCases = createAsyncThunk(
  'testcases/fetchTestCases',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/testcases/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取测试用例失败');
    }
  }
);

// 异步 thunk 获取单个测试用例
export const fetchTestCase = createAsyncThunk(
  'testcases/fetchTestCase',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get(`/testcases/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '获取测试用例详情失败');
    }
  }
);

// 异步 thunk 创建测试用例
export const createTestCase = createAsyncThunk(
  'testcases/createTestCase',
  async (testCase: Partial<TestCase>, { rejectWithValue }) => {
    try {
      const response = await api.post('/testcases/', testCase);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '创建测试用例失败');
    }
  }
);

// 异步 thunk 更新测试用例
export const updateTestCase = createAsyncThunk(
  'testcases/updateTestCase',
  async ({ id, data }: { id: number; data: Partial<TestCase> }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/testcases/${id}/`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '更新测试用例失败');
    }
  }
);

// 异步 thunk 删除测试用例
export const deleteTestCase = createAsyncThunk(
  'testcases/deleteTestCase',
  async (id: number, { rejectWithValue }) => {
    try {
      await api.delete(`/testcases/${id}/`);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '删除测试用例失败');
    }
  }
);

// 创建 slice
const testcasesSlice = createSlice({
  name: 'testcases',
  initialState,
  reducers: {
    clearCurrentTestCase: (state) => {
      state.currentTestCase = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取所有测试用例
      .addCase(fetchTestCases.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTestCases.fulfilled, (state, action: PayloadAction<TestCase[]>) => {
        state.loading = false;
        state.testCases = action.payload;
      })
      .addCase(fetchTestCases.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 获取单个测试用例
      .addCase(fetchTestCase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTestCase.fulfilled, (state, action: PayloadAction<TestCase>) => {
        state.loading = false;
        state.currentTestCase = action.payload;
      })
      .addCase(fetchTestCase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 创建测试用例
      .addCase(createTestCase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createTestCase.fulfilled, (state, action: PayloadAction<TestCase>) => {
        state.loading = false;
        state.testCases.push(action.payload);
      })
      .addCase(createTestCase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 更新测试用例
      .addCase(updateTestCase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateTestCase.fulfilled, (state, action: PayloadAction<TestCase>) => {
        state.loading = false;
        const index = state.testCases.findIndex((tc) => tc.id === action.payload.id);
        if (index !== -1) {
          state.testCases[index] = action.payload;
        }
        if (state.currentTestCase?.id === action.payload.id) {
          state.currentTestCase = action.payload;
        }
      })
      .addCase(updateTestCase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      // 删除测试用例
      .addCase(deleteTestCase.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteTestCase.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.testCases = state.testCases.filter((tc) => tc.id !== action.payload);
        if (state.currentTestCase?.id === action.payload) {
          state.currentTestCase = null;
        }
      })
      .addCase(deleteTestCase.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearCurrentTestCase, clearError } = testcasesSlice.actions;

export default testcasesSlice.reducer;
