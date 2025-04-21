import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Button,
  Card,
  CardContent,
  CardActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Description as DocumentIcon,
  CheckBox as TestCaseIcon,
  Folder as ProjectIcon,
  BarChart as AnalysisIcon,
} from '@mui/icons-material';

import { AppDispatch, RootState } from '../../store';
import { fetchDashboards, fetchDefaultDashboard } from '../../features/dashboard/dashboardSlice';

const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const { currentDashboard, dashboards, loading } = useSelector((state: RootState) => state.dashboard);

  useEffect(() => {
    console.log('DashboardPage - Fetching dashboards');
    dispatch(fetchDashboards())
      .unwrap()
      .then(dashboards => {
        console.log('Dashboards fetched successfully:', dashboards);
      })
      .catch(error => {
        console.error('Failed to fetch dashboards:', error);
      });

    console.log('DashboardPage - Fetching default dashboard');
    dispatch(fetchDefaultDashboard())
      .unwrap()
      .then(dashboard => {
        console.log('Default dashboard fetched successfully:', dashboard);
      })
      .catch(error => {
        console.error('Failed to fetch default dashboard:', error);
      });
  }, [dispatch]);

  if (loading) {
    return <Typography>{t('common.loading')}</Typography>;
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {t('dashboard.title')}
        </Typography>
        <Box>
          <Tooltip title={t('common.refresh')}>
            <IconButton sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('dashboard.editDashboard')}>
            <IconButton sx={{ mr: 1 }}>
              <EditIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
          >
            {t('dashboard.addWidget')}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Summary Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.summary')}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('regulations.documents')}
                </Typography>
                <Typography variant="h5">24</Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('testcases.testcases')}
                </Typography>
                <Typography variant="h5">156</Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('projects.projects')}
                </Typography>
                <Typography variant="h5">8</Typography>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('analysis.tasks')}
                </Typography>
                <Typography variant="h5">12</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.recentActivity')}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <List>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <DocumentIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="ISO 26262 Document Updated"
                    secondary="2 hours ago by John Doe"
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <TestCaseIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Lane Keeping Test Case Created"
                    secondary="Yesterday by Jane Smith"
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <ProjectIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Highway Pilot Project Started"
                    secondary="2 days ago by Mike Johnson"
                  />
                </ListItem>
                <ListItem>
                  <ListItemAvatar>
                    <Avatar>
                      <AnalysisIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary="Sensor Fusion Analysis Completed"
                    secondary="3 days ago by Sarah Williams"
                  />
                </ListItem>
              </List>
            </CardContent>
            <CardActions>
              <Button size="small">View All</Button>
            </CardActions>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6} lg={2}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.quickActions')}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 2 }}>
                <Button variant="outlined" startIcon={<DocumentIcon />}>
                  {t('regulations.uploadDocument')}
                </Button>
                <Button variant="outlined" startIcon={<TestCaseIcon />}>
                  {t('testcases.createTestCase')}
                </Button>
                <Button variant="outlined" startIcon={<ProjectIcon />}>
                  {t('projects.createProject')}
                </Button>
                <Button variant="outlined" startIcon={<AnalysisIcon />}>
                  {t('analysis.createTask')}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('dashboard.statistics')}
              </Typography>
              <Divider sx={{ my: 1 }} />
              <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Charts will be displayed here
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Additional Widgets */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('regulations.documents')} {t('common.status')}
            </Typography>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Document status chart will be displayed here
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t('testcases.testcases')} {t('common.status')}
            </Typography>
            <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Test case status chart will be displayed here
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
