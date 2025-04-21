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
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import CancelIcon from '@mui/icons-material/Cancel';

import { AppDispatch, RootState } from '../../store';
import {
  fetchTestCase,
  updateTestCase,
  createTestCase
} from '../../features/testcases/testcasesSlice';
import { fetchRegulations } from '../../features/regulations/regulationsSlice';
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
      id={`testcase-tabpanel-${index}`}
      aria-labelledby={`testcase-tab-${index}`}
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

const TestCaseDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';
  const isEdit = new URLSearchParams(location.search).get('edit') === 'true' || isNew;

  const { currentTestCase, loading } = useSelector((state: RootState) => state.testcases);
  const { regulations } = useSelector((state: RootState) => state.regulations);
  const { projects } = useSelector((state: RootState) => state.projects);

  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (!isNew && id) {
      dispatch(fetchTestCase(parseInt(id)));
    }
    dispatch(fetchRegulations());
    dispatch(fetchProjects());
  }, [dispatch, id, isNew]);

  const validationSchema = yup.object({
    name: yup.string().required(t('validation.required')),
    description: yup.string().required(t('validation.required')),
    status: yup.string().required(t('validation.required')),
  });

  const formik = useFormik({
    initialValues: {
      name: currentTestCase?.name || '',
      description: currentTestCase?.description || '',
      status: currentTestCase?.status || 'DRAFT',
      regulation: currentTestCase?.regulation?.id || '',
      project: currentTestCase?.project?.id || '',
    },
    validationSchema,
    enableReinitialize: true,
    onSubmit: (values) => {
      if (isNew) {
        dispatch(createTestCase(values))
          .unwrap()
          .then((result) => {
            navigate(`/testcases/${result.id}`);
          });
      } else if (id) {
        dispatch(updateTestCase({ id: parseInt(id), data: values }))
          .unwrap()
          .then(() => {
            navigate(`/testcases/${id}`);
          });
      }
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleBack = () => {
    navigate('/testcases');
  };

  const handleEdit = () => {
    navigate(`/testcases/${id}?edit=true`);
  };

  const handleCancel = () => {
    if (isNew) {
      navigate('/testcases');
    } else {
      navigate(`/testcases/${id}`);
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
            {t('testcases.title')}
          </Link>
          <Typography color="text.primary">
            {isNew ? t('testcases.newTestCase') : currentTestCase?.name}
          </Typography>
        </Breadcrumbs>

        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4" component="h1" gutterBottom>
              {isNew ? t('testcases.newTestCase') : currentTestCase?.name}
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
            <Tab label={t('testcases.details')} />
            <Tab label={t('testcases.analysisResults')} />
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
                    label={t('testcases.name')}
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
                    label={t('testcases.status')}
                    value={formik.values.status}
                    onChange={formik.handleChange}
                    error={formik.touched.status && Boolean(formik.errors.status)}
                    helperText={formik.touched.status && formik.errors.status}
                    disabled={!isEdit}
                    margin="normal"
                  >
                    <MenuItem value="DRAFT">{t('testcases.statuses.draft')}</MenuItem>
                    <MenuItem value="ACTIVE">{t('testcases.statuses.active')}</MenuItem>
                    <MenuItem value="COMPLETED">{t('testcases.statuses.completed')}</MenuItem>
                    <MenuItem value="ARCHIVED">{t('testcases.statuses.archived')}</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="regulation-label">{t('testcases.regulation')}</InputLabel>
                    <Select
                      labelId="regulation-label"
                      id="regulation"
                      name="regulation"
                      value={formik.values.regulation}
                      onChange={formik.handleChange}
                      disabled={!isEdit}
                      label={t('testcases.regulation')}
                    >
                      <MenuItem value="">{t('common.none')}</MenuItem>
                      {Array.isArray(regulations) ? regulations.map((regulation) => (
                        <MenuItem key={regulation.id} value={regulation.id}>
                          {regulation.name}
                        </MenuItem>
                      )) : null}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="project-label">{t('testcases.project')}</InputLabel>
                    <Select
                      labelId="project-label"
                      id="project"
                      name="project"
                      value={formik.values.project}
                      onChange={formik.handleChange}
                      disabled={!isEdit}
                      label={t('testcases.project')}
                    >
                      <MenuItem value="">{t('common.none')}</MenuItem>
                      {Array.isArray(projects) ? projects.map((project) => (
                        <MenuItem key={project.id} value={project.id}>
                          {project.name}
                        </MenuItem>
                      )) : null}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="description"
                    name="description"
                    label={t('testcases.description')}
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
              {t('testcases.noAnalysisResults')}
            </Typography>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default TestCaseDetailPage;
