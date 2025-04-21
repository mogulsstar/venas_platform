import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// Types
interface Widget {
  id: number;
  name: string;
  widget_type: string;
  configuration: any;
  data_source: string;
  refresh_interval: number;
}

interface WidgetInstance {
  id: number;
  dashboard: number;
  widget: number;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  configuration_override: any;
}

interface Dashboard {
  id: number;
  name: string;
  description: string;
  layout: any;
  is_default: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  widget_instances: WidgetInstance[];
}

interface DashboardState {
  dashboards: Dashboard[];
  currentDashboard: Dashboard | null;
  widgets: Widget[];
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: DashboardState = {
  dashboards: [],
  currentDashboard: null,
  widgets: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchDashboards = createAsyncThunk(
  'dashboard/fetchDashboards',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<Dashboard[]>('/dashboard/dashboards/my-dashboards/');
      return response.data;
    } catch (error: any) {
      // 如果是 404 或 401 错误，返回空数组而不是拒绝 Promise
      if (error.response?.status === 404 || error.response?.status === 401) {
        return [];
      }
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboards');
    }
  }
);

export const fetchDefaultDashboard = createAsyncThunk(
  'dashboard/fetchDefaultDashboard',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<Dashboard>('/dashboard/dashboards/default/');
      return response.data;
    } catch (error: any) {
      // 如果是 404 或 401 错误，返回空对象而不是拒绝 Promise
      if (error.response?.status === 404 || error.response?.status === 401) {
        return {
          id: 0,
          name: 'Default Dashboard',
          description: '',
          layout: {},
          is_default: true,
          created_by: null,
          created_by_name: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          widget_instances: []
        };
      }
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch default dashboard');
    }
  }
);

export const fetchDashboard = createAsyncThunk(
  'dashboard/fetchDashboard',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get<Dashboard>(`/dashboard/dashboards/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch dashboard');
    }
  }
);

export const createDashboard = createAsyncThunk(
  'dashboard/createDashboard',
  async (dashboard: Partial<Dashboard>, { rejectWithValue }) => {
    try {
      const response = await api.post<Dashboard>('/dashboard/dashboards/', dashboard);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create dashboard');
    }
  }
);

export const updateDashboard = createAsyncThunk(
  'dashboard/updateDashboard',
  async ({ id, data }: { id: number; data: Partial<Dashboard> }, { rejectWithValue }) => {
    try {
      const response = await api.patch<Dashboard>(`/dashboard/dashboards/${id}/`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update dashboard');
    }
  }
);

export const fetchWidgets = createAsyncThunk(
  'dashboard/fetchWidgets',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<Widget[]>('/dashboard/widgets/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch widgets');
    }
  }
);

export const addWidgetToDashboard = createAsyncThunk(
  'dashboard/addWidgetToDashboard',
  async (
    {
      dashboardId,
      widgetId,
      position,
    }: {
      dashboardId: number;
      widgetId: number;
      position: {
        x: number;
        y: number;
        width: number;
        height: number;
      };
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post<WidgetInstance>(`/dashboard/dashboards/${dashboardId}/add_widget/`, {
        widget_id: widgetId,
        position_x: position.x,
        position_y: position.y,
        width: position.width,
        height: position.height,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to add widget to dashboard');
    }
  }
);

// Slice
const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentDashboard: (state, action: PayloadAction<Dashboard>) => {
      state.currentDashboard = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch dashboards
      .addCase(fetchDashboards.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboards.fulfilled, (state, action: PayloadAction<Dashboard[]>) => {
        state.loading = false;
        state.dashboards = action.payload;
        state.error = null;
      })
      .addCase(fetchDashboards.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch default dashboard
      .addCase(fetchDefaultDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDefaultDashboard.fulfilled, (state, action: PayloadAction<Dashboard>) => {
        state.loading = false;
        state.currentDashboard = action.payload;
        state.error = null;
      })
      .addCase(fetchDefaultDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch dashboard
      .addCase(fetchDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboard.fulfilled, (state, action: PayloadAction<Dashboard>) => {
        state.loading = false;
        state.currentDashboard = action.payload;
        state.error = null;
      })
      .addCase(fetchDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Create dashboard
      .addCase(createDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createDashboard.fulfilled, (state, action: PayloadAction<Dashboard>) => {
        state.loading = false;
        state.dashboards.push(action.payload);
        state.currentDashboard = action.payload;
        state.error = null;
      })
      .addCase(createDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Update dashboard
      .addCase(updateDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateDashboard.fulfilled, (state, action: PayloadAction<Dashboard>) => {
        state.loading = false;
        state.dashboards = state.dashboards.map((dashboard) =>
          dashboard.id === action.payload.id ? action.payload : dashboard
        );
        if (state.currentDashboard && state.currentDashboard.id === action.payload.id) {
          state.currentDashboard = action.payload;
        }
        state.error = null;
      })
      .addCase(updateDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch widgets
      .addCase(fetchWidgets.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWidgets.fulfilled, (state, action: PayloadAction<Widget[]>) => {
        state.loading = false;
        state.widgets = action.payload;
        state.error = null;
      })
      .addCase(fetchWidgets.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Add widget to dashboard
      .addCase(addWidgetToDashboard.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addWidgetToDashboard.fulfilled, (state, action: PayloadAction<WidgetInstance>) => {
        state.loading = false;
        if (state.currentDashboard && state.currentDashboard.id === action.payload.dashboard) {
          state.currentDashboard.widget_instances.push(action.payload);
        }
        state.error = null;
      })
      .addCase(addWidgetToDashboard.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setCurrentDashboard } = dashboardSlice.actions;

export default dashboardSlice.reducer;
