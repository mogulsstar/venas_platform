import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Divider,
  CircularProgress,
  Button,
  MenuItem,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

import { AppDispatch, RootState } from '../../store';
import { fetchMonitorData } from '../../features/monitor/monitorSlice';

const MonitorPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const { data, loading } = useSelector((state: RootState) => state.monitor);

  const [refreshInterval, setRefreshInterval] = useState<number>(30);
  const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

  useEffect(() => {
    // Initial data fetch
    dispatch(fetchMonitorData());

    // Set up auto-refresh
    let intervalId: NodeJS.Timeout | null = null;

    if (autoRefresh) {
      intervalId = setInterval(() => {
        dispatch(fetchMonitorData());
      }, refreshInterval * 1000);
    }

    // Clean up interval on component unmount
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [dispatch, refreshInterval, autoRefresh]);

  const handleRefresh = () => {
    dispatch(fetchMonitorData());
  };

  const handleToggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const handleChangeRefreshInterval = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRefreshInterval(Number(event.target.value));
  };

  const getStatusColor = (usage: number): 'success' | 'warning' | 'error' => {
    if (usage < 70) return 'success';
    if (usage < 90) return 'warning';
    return 'error';
  };

  const getLogLevelIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const formatUptime = (seconds: number): string => {
    const days = Math.floor(seconds / (3600 * 24));
    const hours = Math.floor((seconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    return `${days}d ${hours}h ${minutes}m`;
  };

  if (loading && !data) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4" component="h1" gutterBottom>
              {t('monitor.title')}
            </Typography>
          </Grid>
          <Grid item>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <TextField
                select
                label={t('monitor.refreshInterval')}
                value={refreshInterval}
                onChange={handleChangeRefreshInterval}
                size="small"
                sx={{ width: 150 }}
                disabled={!autoRefresh}
              >
                <MenuItem value={10}>10 {t('monitor.seconds')}</MenuItem>
                <MenuItem value={30}>30 {t('monitor.seconds')}</MenuItem>
                <MenuItem value={60}>1 {t('monitor.minute')}</MenuItem>
                <MenuItem value={300}>5 {t('monitor.minutes')}</MenuItem>
              </TextField>

              <Button
                variant={autoRefresh ? "contained" : "outlined"}
                color={autoRefresh ? "primary" : "secondary"}
                onClick={handleToggleAutoRefresh}
              >
                {autoRefresh ? t('monitor.autoRefreshOn') : t('monitor.autoRefreshOff')}
              </Button>

              <Tooltip title={t('monitor.refresh')}>
                <IconButton onClick={handleRefresh} color="primary">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>

        {data && data.system_status && (
          <>
            {/* System Status */}
            <Typography variant="h5" sx={{ mb: 2 }}>
              {t('monitor.systemStatus')}
            </Typography>

            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.cpuUsage')}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={data.system_status.cpu_usage}
                          color={getStatusColor(data.system_status.cpu_usage)}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {`${Math.round(data.system_status.cpu_usage)}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.memoryUsage')}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={data.system_status.memory_usage}
                          color={getStatusColor(data.system_status.memory_usage)}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {`${Math.round(data.system_status.memory_usage)}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.diskUsage')}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={data.system_status.disk_usage}
                          color={getStatusColor(data.system_status.disk_usage)}
                        />
                      </Box>
                      <Box sx={{ minWidth: 35 }}>
                        <Typography variant="body2" color="text.secondary">
                          {`${Math.round(data.system_status.disk_usage)}%`}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.uptime')}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'medium' }}>
                      {formatUptime(data.system_status.uptime)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Active Tasks */}
            <Typography variant="h5" sx={{ mb: 2 }}>
              {t('monitor.activeTasks')}
            </Typography>

            <Paper sx={{ mb: 4 }}>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('monitor.taskName')}</TableCell>
                      <TableCell>{t('monitor.taskType')}</TableCell>
                      <TableCell>{t('monitor.status')}</TableCell>
                      <TableCell>{t('monitor.progress')}</TableCell>
                      <TableCell>{t('monitor.startedAt')}</TableCell>
                      <TableCell>{t('monitor.estimatedCompletion')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.active_tasks.length > 0 ? (
                      data.active_tasks.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell>{task.name}</TableCell>
                          <TableCell>{task.type}</TableCell>
                          <TableCell>
                            <Chip
                              label={task.status}
                              color={task.status === 'RUNNING' ? 'primary' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Box sx={{ width: '100%', mr: 1 }}>
                                <LinearProgress variant="determinate" value={task.progress} />
                              </Box>
                              <Box sx={{ minWidth: 35 }}>
                                <Typography variant="body2" color="text.secondary">
                                  {`${Math.round(task.progress)}%`}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>{new Date(task.started_at).toLocaleString()}</TableCell>
                          <TableCell>{new Date(task.estimated_completion).toLocaleString()}</TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={6} align="center">
                          {t('monitor.noActiveTasks')}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Recent Errors */}
            <Typography variant="h5" sx={{ mb: 2 }}>
              {t('monitor.recentErrors')}
            </Typography>

            <Paper sx={{ mb: 4 }}>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>{t('monitor.timestamp')}</TableCell>
                      <TableCell>{t('monitor.level')}</TableCell>
                      <TableCell>{t('monitor.message')}</TableCell>
                      <TableCell>{t('monitor.source')}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recent_errors.length > 0 ? (
                      data.recent_errors.map((error) => (
                        <TableRow key={error.id}>
                          <TableCell>{new Date(error.timestamp).toLocaleString()}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getLogLevelIcon(error.level)}
                              <Typography sx={{ ml: 1 }}>{error.level}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{error.message}</TableCell>
                          <TableCell>{error.source}</TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={4} align="center">
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                            {t('monitor.noErrors')}
                          </Box>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>

            {/* Performance Metrics */}
            <Typography variant="h5" sx={{ mb: 2 }}>
              {t('monitor.performanceMetrics')}
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.apiResponseTime')}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'medium' }}>
                      {data.performance_metrics.api_response_time.toFixed(2)} ms
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.databaseQueryTime')}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'medium' }}>
                      {data.performance_metrics.database_query_time.toFixed(2)} ms
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {t('monitor.analysisExecutionTime')}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'medium' }}>
                      {data.performance_metrics.analysis_execution_time.toFixed(2)} s
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </>
        )}
      </Box>
    </Container>
  );
};

export default MonitorPage;
