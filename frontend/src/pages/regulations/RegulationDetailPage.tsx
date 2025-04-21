import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  Card,
  CardContent,
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
  fetchRegulation,
  updateRegulation,
  createRegulation
} from '../../features/regulations/regulationsSlice';

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
      id={`regulation-tabpanel-${index}`}
      aria-labelledby={`regulation-tab-${index}`}
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

const RegulationDetailPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const isNew = id === 'new';
  const isEdit = new URLSearchParams(location.search).get('edit') === 'true' || isNew;

  const { currentRegulation, loading } = useSelector((state: RootState) => state.regulations);

  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (!isNew && id) {
      dispatch(fetchRegulation(parseInt(id)));
    }
  }, [dispatch, id, isNew]);

  const validationSchema = yup.object({
    name: yup.string().required(t('validation.required')),
    description: yup.string().required(t('validation.required')),
    regulation_type: yup.string().required(t('validation.required')),
    status: yup.string().required(t('validation.required')),
    effective_date: yup.date().required(t('validation.required')),
    jurisdiction: yup.string().required(t('validation.required')),
  });

  // 使用 useState 来存储初始值，避免无限循环
  const [initialValues] = useState({
    name: isNew ? '' : (currentRegulation?.name || ''),
    description: isNew ? '' : (currentRegulation?.description || ''),
    regulation_type: isNew ? '' : (currentRegulation?.regulation_type || ''),
    status: isNew ? 'DRAFT' : (currentRegulation?.status || 'DRAFT'),
    effective_date: isNew ? new Date() : (currentRegulation?.effective_date ? new Date(currentRegulation.effective_date) : new Date()),
    jurisdiction: isNew ? '' : (currentRegulation?.jurisdiction || ''),
    document_url: isNew ? '' : (currentRegulation?.document_url || ''),
  });

  const formik = useFormik({
    initialValues,
    validationSchema,
    enableReinitialize: false,
    onSubmit: (values) => {
      if (isNew) {
        dispatch(createRegulation(values))
          .unwrap()
          .then((result) => {
            navigate(`/regulations/${result.id}`);
          });
      } else if (id) {
        dispatch(updateRegulation({ id: parseInt(id), data: values }))
          .unwrap()
          .then(() => {
            navigate(`/regulations/${id}`);
          });
      }
    },
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleBack = () => {
    navigate('/regulations');
  };

  const handleEdit = () => {
    navigate(`/regulations/${id}?edit=true`);
  };

  const handleCancel = () => {
    if (isNew) {
      navigate('/regulations');
    } else {
      navigate(`/regulations/${id}`);
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
            {t('regulations.title')}
          </Link>
          <Typography color="text.primary">
            {isNew ? t('regulations.newRegulation') : currentRegulation?.name}
          </Typography>
        </Breadcrumbs>

        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4" component="h1" gutterBottom>
              {isNew ? t('regulations.newRegulation') : currentRegulation?.name}
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
            <Tab label={t('regulations.details')} />
            <Tab label={t('regulations.relatedTestCases')} />
            <Tab label={t('regulations.relatedProjects')} />
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
                    label={t('regulations.name')}
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
                    id="regulation_type"
                    name="regulation_type"
                    label={t('regulations.type')}
                    value={formik.values.regulation_type}
                    onChange={formik.handleChange}
                    error={formik.touched.regulation_type && Boolean(formik.errors.regulation_type)}
                    helperText={formik.touched.regulation_type && formik.errors.regulation_type}
                    disabled={!isEdit}
                    margin="normal"
                  >
                    <MenuItem value="FINANCIAL">{t('regulations.types.financial')}</MenuItem>
                    <MenuItem value="ENVIRONMENTAL">{t('regulations.types.environmental')}</MenuItem>
                    <MenuItem value="HEALTH">{t('regulations.types.health')}</MenuItem>
                    <MenuItem value="SAFETY">{t('regulations.types.safety')}</MenuItem>
                    <MenuItem value="OTHER">{t('regulations.types.other')}</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    select
                    fullWidth
                    id="status"
                    name="status"
                    label={t('regulations.status')}
                    value={formik.values.status}
                    onChange={formik.handleChange}
                    error={formik.touched.status && Boolean(formik.errors.status)}
                    helperText={formik.touched.status && formik.errors.status}
                    disabled={!isEdit}
                    margin="normal"
                  >
                    <MenuItem value="DRAFT">{t('regulations.statuses.draft')}</MenuItem>
                    <MenuItem value="ACTIVE">{t('regulations.statuses.active')}</MenuItem>
                    <MenuItem value="INACTIVE">{t('regulations.statuses.inactive')}</MenuItem>
                    <MenuItem value="ARCHIVED">{t('regulations.statuses.archived')}</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label={t('regulations.effectiveDate')}
                    value={formik.values.effective_date}
                    onChange={(date) => formik.setFieldValue('effective_date', date)}
                    disabled={!isEdit}
                    slotProps={{
                      textField: {
                        fullWidth: true,
                        margin: 'normal',
                        error: formik.touched.effective_date && Boolean(formik.errors.effective_date),
                        helperText: formik.touched.effective_date && formik.errors.effective_date as string,
                      },
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    id="jurisdiction"
                    name="jurisdiction"
                    label={t('regulations.jurisdiction')}
                    value={formik.values.jurisdiction}
                    onChange={formik.handleChange}
                    error={formik.touched.jurisdiction && Boolean(formik.errors.jurisdiction)}
                    helperText={formik.touched.jurisdiction && formik.errors.jurisdiction}
                    disabled={!isEdit}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    id="document_url"
                    name="document_url"
                    label={t('regulations.documentUrl')}
                    value={formik.values.document_url}
                    onChange={formik.handleChange}
                    disabled={!isEdit}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    id="description"
                    name="description"
                    label={t('regulations.description')}
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
              {t('regulations.noTestCases')}
            </Typography>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Typography variant="body1">
              {t('regulations.noProjects')}
            </Typography>
          </TabPanel>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegulationDetailPage;
