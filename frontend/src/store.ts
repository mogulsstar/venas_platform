import { configureStore } from '@reduxjs/toolkit';
import authReducer from './features/auth/authSlice';
import regulationsReducer from './features/regulations/regulationsSlice';
import testcasesReducer from './features/testcases/testcasesSlice';
import projectsReducer from './features/projects/projectsSlice';
import analysisReducer from './features/analysis/analysisSlice';
import dashboardReducer from './features/dashboard/dashboardSlice';
import monitorReducer from './features/monitor/monitorSlice';
import helpReducer from './features/help/helpSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    regulations: regulationsReducer,
    testcases: testcasesReducer,
    projects: projectsReducer,
    analysis: analysisReducer,
    dashboard: dashboardReducer,
    monitor: monitorReducer,
    help: helpReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
