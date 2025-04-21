import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Container,
  Grid,
  Typography,
  TextField,
  MenuItem,
  Tabs,
  Tab,
  Divider,
  Paper,
  CircularProgress,
  Breadcrumbs,
  Link,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

import { AppDispatch, RootState } from '../../store';
import { 
  fetchAnalysisTask, 
  updateAnalysisTask, 
  createAnalysisTask,
  runAnalysisTask
} from '../../features/analysis/analysisSlice';
import { fetchTestCases } from '../../features/testcases/testcasesSlice';
import { fetchProjects } from '../../features/projects/projectsSlice';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AnalysisDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';
  const isEdit = new URLSearchParams(location.search).get('edit') === 'true' || isNew;
  
  const { currentTask, loading } = useSelector((state: RootState) => state.analysis);
  const { testCases } = useSelector((state: RootState) => state.testcases);
  const { projects } = useSelector((state: RootState) => state.projects);
  
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (!isNew && id) {
      dispatch(fetchAnalysisTask(parseInt(id)));
    }
    dispatch(fetchTestCases());
    dispatch(fetchProjects());
  }, [dispatch, id, isNew]);

  const validationSchema = yup.object({
    name: yup.string().required(t('validation.required')),
    description: yup.string().required(t('validation.required')),
    analysis_type: yup.string().required(t('validation.required')),
  });

  const formik = useFormik({
    initialValues: {
      name: currentTask?.name || '',
      description: currentTask?.description || '',
      analysis_type: currentTask?.analysis_type || 'DATA_CLEANING',
      test_case: currentTask?.test_case?.id || '',
      project: currentTask?.project?.id || '',
    },
    validationSchema,
    enableReinitialize: true,
    onSubmit: (values) => {
      if (isNew) {
        dispatch(createAnalysisTask(values))
          .unwrap()
          .then((result) => {
            navigate(`/analysis/${result.id}`);
          });
      } else if (id) {
        dispatch(updateAnalysisTask({ id: parseInt(id), data: values }))
          .unwrap()
          .then(() => {
            navigate(`/analysis/${id}`);
          });
      }
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleBack = () => {
    navigate('/analysis');
  };

  const handleEdit = () => {
    navigate(`/analysis/${id}?edit=true`);
  };

  const handleCancel = () => {
    if (isNew) {
      navigate('/analysis');
    } else {
      navigate(`/analysis/${id}`);
    }
  };

  const handleRunTask = () => {
    if (id) {
      dispatch(runAnalysisTask(parseInt(id)));
    }
  };

  const getStatusChip = (status: string) => {
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
    
    switch (status) {
      case 'PENDING':
        color = 'default';
        break;
      case 'RUNNING':
        color = 'info';
        break;
      case 'COMPLETED':
        color = 'success';
        break;
      case 'FAILED':
        color = 'error';
        break;
      case 'CANCELLED':
        color = 'warning';
        break;
    }
    
    return (
      <Chip 
        label={t(`analysis.statuses.${status.toLowerCase()}`)} 
        color={color} 
      />
    );
  };

  if (loading && !isNew) {
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
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link color="inherit" onClick={handleBack} sx={{ cursor: 'pointer' }}>
            {t('analysis.title')}
          </Link>
          <Typography color="text.primary">
            {isNew ? t('analysis.newTask') : currentTask?.name}
          </Typography>
        </Breadcrumbs>

        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography variant="h4" component="h1" gutterBottom sx={{ mr: 2 }}>
                {isNew ? t('analysis.newTask') : currentTask?.name}
              </Typography>
              {!isNew && currentTask?.status && (
                getStatusChip(currentTask.status)
              )}
            </Box>
          </Grid>
          <Grid item>
            {isEdit ? (
              <>
                <Button
                  variant="outlined"
                  color="secondary"
                  startIcon={<CancelIcon />}
                  onClick={handleCancel}
                  sx={{ mr: 1 }}
                >
                  {t('common.cancel')}
                </Button>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SaveIcon />}
                  onClick={() => formik.handleSubmit()}
                >
                  {t('common.save')}
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outlined"
                  startIcon={<ArrowBackIcon />}
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                >
                  {t('common.back')}
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<EditIcon />}
                  onClick={handleEdit}
                  sx={{ mr: 1 }}
                >
                  {t('common.edit')}
                </Button>
                {!isNew && currentTask?.status !== 'RUNNING' && (
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<PlayArrowIcon />}
                    onClick={handleRunTask}
                  >
                    {t('analysis.run')}
                  </Button>
                )}
              </>
            )}
          </Grid>
        </Grid>

        <Paper>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab label={t('analysis.details')} />
            <Tab label={t('analysis.results')} disabled={isNew || !currentTask?.results} />
            <Tab label={t('analysis.visualizations')} disabled={isNew} />
          </Tabs>
          
          <Divider />
          
          <TabPanel value={tabValue} index={0}>
            <form onSubmit={formik.handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    id="name"
                    name="name"
                    label={t('analysis.name')}
                    value={formik.values.name}
                    onChange={formik.handleChange}
                    error={formik.touched.name && Boolean(formik.errors.name)}
                    helperText={formik.touched.name && formik.errors.name}
                    disabled={!isEdit}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    select
                    fullWidth
                    id="analysis_type"
                    name="analysis_type"
                    label={t('analysis.type')}
                    value={formik.values.analysis_type}
                    onChange={formik.handleChange}
                    error={formik.touched.analysis_type && Boolean(formik.errors.analysis_type)}
                    helperText={formik.touched.analysis_type && formik.errors.analysis_type}
                    disabled={!isEdit}
                    margin="normal"
                  >
                    <MenuItem value="DATA_CLEANING">{t('analysis.types.dataCleaning')}</MenuItem>
                    <MenuItem value="STATISTICAL">{t('analysis.types.statistical')}</MenuItem>
                    <MenuItem value="PREDICTIVE">{t('analysis.types.predictive')}</MenuItem>
                    <MenuItem value="VISUALIZATION">{t('analysis.types.visualization')}</MenuItem>
                    <MenuItem value="CUSTOM">{t('analysis.types.custom')}</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="test-case-label">{t('analysis.testCase')}</InputLabel>
                    <Select
                      labelId="test-case-label"
                      id="test_case"
                      name="test_case"
                      value={formik.values.test_case}
                      onChange={formik.handleChange}
                      disabled={!isEdit}
                      label={t('analysis.testCase')}
                    >
                      <MenuItem value="">{t('common.none')}</MenuItem>
                      {testCases.map((testCase) => (
                        <MenuItem key={testCase.id} value={testCase.id}>
                          {testCase.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="project-label">{t('analysis.project')}</InputLabel>
                    <Select
                      labelId="project-label"
                      id="project"
                      name="project"
                      value={formik.values.project}
                      onChange={formik.handleChange}
                      disabled={!isEdit}
                      label={t('analysis.project')}
                    >
                      <MenuItem value="">{t('common.none')}</MenuItem>
                      {projects.map((project) => (
                        <MenuItem key={project.id} value={project.id}>
                          {project.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="description"
                    name="description"
                    label={t('analysis.description')}
                    value={formik.values.description}
                    onChange={formik.handleChange}
                    error={formik.touched.description && Boolean(formik.errors.description)}
                    helperText={formik.touched.description && formik.errors.description}
                    disabled={!isEdit}
                    multiline
                    rows={4}
                    margin="normal"
                  />
                </Grid>
              </Grid>
            </form>
          </TabPanel>
          
          <TabPanel value={tabValue} index={1}>
            {currentTask?.results ? (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {t('analysis.resultsTitle')}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {currentTask.results.message}
                  </Typography>
                  
                  <Typography variant="subtitle1" sx={{ mt: 2 }}>
                    {t('analysis.resultsSummary')}
                  </Typography>
                  
                  <List>
                    {Object.entries(currentTask.results.summary || {}).map(([key, value]) => (
                      <ListItem key={key}>
                        <ListItemText 
                          primary={t(`analysis.summary.${key}`, { defaultValue: key })} 
                          secondary={value}
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            ) : (
              <Typography variant="body1">
                {t('analysis.noResults')}
              </Typography>
            )}
          </TabPanel>
          
          <TabPanel value={tabValue} index={2}>
            <Typography variant="body1">
              {t('analysis.noVisualizations')}
            </Typography>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default AnalysisDetailPage;
