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
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { useFormik } from 'formik';
import * as yup from 'yup';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';

import { AppDispatch, RootState } from '../../store';
import { 
  fetchProject, 
  updateProject, 
  createProject 
} from '../../features/projects/projectsSlice';

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
      id={`project-tabpanel-${index}`}
      aria-labelledby={`project-tab-${index}`}
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

const ProjectDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';
  const isEdit = new URLSearchParams(location.search).get('edit') === 'true' || isNew;
  
  const { currentProject, loading } = useSelector((state: RootState) => state.projects);
  
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (!isNew && id) {
      dispatch(fetchProject(parseInt(id)));
    }
  }, [dispatch, id, isNew]);

  const validationSchema = yup.object({
    name: yup.string().required(t('validation.required')),
    description: yup.string().required(t('validation.required')),
    status: yup.string().required(t('validation.required')),
    start_date: yup.date().required(t('validation.required')),
  });

  const formik = useFormik({
    initialValues: {
      name: currentProject?.name || '',
      description: currentProject?.description || '',
      status: currentProject?.status || 'PLANNING',
      start_date: currentProject?.start_date ? new Date(currentProject.start_date) : new Date(),
      end_date: currentProject?.end_date ? new Date(currentProject.end_date) : null,
    },
    validationSchema,
    enableReinitialize: true,
    onSubmit: (values) => {
      if (isNew) {
        dispatch(createProject(values))
          .unwrap()
          .then((result) => {
            navigate(`/projects/${result.id}`);
          });
      } else if (id) {
        dispatch(updateProject({ id: parseInt(id), data: values }))
          .unwrap()
          .then(() => {
            navigate(`/projects/${id}`);
          });
      }
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleBack = () => {
    navigate('/projects');
  };

  const handleEdit = () => {
    navigate(`/projects/${id}?edit=true`);
  };

  const handleCancel = () => {
    if (isNew) {
      navigate('/projects');
    } else {
      navigate(`/projects/${id}`);
    }
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
            {t('projects.title')}
          </Link>
          <Typography color="text.primary">
            {isNew ? t('projects.newProject') : currentProject?.name}
          </Typography>
        </Breadcrumbs>

        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4" component="h1" gutterBottom>
              {isNew ? t('projects.newProject') : currentProject?.name}
            </Typography>
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
                  variant="contained"
                  color="primary"
                  startIcon={<EditIcon />}
                  onClick={handleEdit}
                >
                  {t('common.edit')}
                </Button>
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
            <Tab label={t('projects.details')} />
            <Tab label={t('projects.testCases')} />
            <Tab label={t('projects.analysis')} />
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
                    label={t('projects.name')}
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
                    id="status"
                    name="status"
                    label={t('projects.status')}
                    value={formik.values.status}
                    onChange={formik.handleChange}
                    error={formik.touched.status && Boolean(formik.errors.status)}
                    helperText={formik.touched.status && formik.errors.status}
                    disabled={!isEdit}
                    margin="normal"
                  >
                    <MenuItem value="PLANNING">{t('projects.statuses.planning')}</MenuItem>
                    <MenuItem value="ACTIVE">{t('projects.statuses.active')}</MenuItem>
                    <MenuItem value="COMPLETED">{t('projects.statuses.completed')}</MenuItem>
                    <MenuItem value="ON_HOLD">{t('projects.statuses.onHold')}</MenuItem>
                    <MenuItem value="CANCELLED">{t('projects.statuses.cancelled')}</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label={t('projects.startDate')}
                    value={formik.values.start_date}
                    onChange={(date) => formik.setFieldValue('start_date', date)}
                    disabled={!isEdit}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'normal',
                        error: formik.touched.start_date && Boolean(formik.errors.start_date),
                        helperText: formik.touched.start_date && formik.errors.start_date as string,
                      },
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label={t('projects.endDate')}
                    value={formik.values.end_date}
                    onChange={(date) => formik.setFieldValue('end_date', date)}
                    disabled={!isEdit}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'normal',
                      },
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="description"
                    name="description"
                    label={t('projects.description')}
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
            <Typography variant="body1">
              {t('projects.noTestCases')}
            </Typography>
          </TabPanel>
          
          <TabPanel value={tabValue} index={2}>
            <Typography variant="body1">
              {t('projects.noAnalysis')}
            </Typography>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default ProjectDetailPage;
