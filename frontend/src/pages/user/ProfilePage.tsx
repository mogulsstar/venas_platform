import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  Avatar,
  Button,
  TextField,
  Divider,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Snackbar,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import PersonIcon from '@mui/icons-material/Person';
import SecurityIcon from '@mui/icons-material/Security';
import HistoryIcon from '@mui/icons-material/History';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SaveIcon from '@mui/icons-material/Save';
import EventIcon from '@mui/icons-material/Event';
import DescriptionIcon from '@mui/icons-material/Description';
import AnalyticsIcon from '@mui/icons-material/Analytics';

import { AppDispatch, RootState } from '../../store';
import { updateUserProfile } from '../../features/auth/authSlice';

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
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
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

const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const { user, loading } = useSelector((state: RootState) => state.auth);
  
  const [tabValue, setTabValue] = useState(0);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const validationSchema = yup.object({
    first_name: yup.string().required(t('validation.required')),
    last_name: yup.string().required(t('validation.required')),
    email: yup.string().email(t('validation.invalidEmail')).required(t('validation.required')),
    phone: yup.string(),
    job_title: yup.string(),
    department: yup.string(),
  });
  
  const formik = useFormik({
    initialValues: {
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      job_title: user?.job_title || '',
      department: user?.department || '',
    },
    validationSchema,
    enableReinitialize: true,
    onSubmit: (values) => {
      dispatch(updateUserProfile(values))
        .unwrap()
        .then(() => {
          setSuccessMessage(t('profile.updateSuccess'));
        });
    },
  });
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const handleCloseSnackbar = () => {
    setSuccessMessage(null);
  };
  
  if (!user) {
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
        <Typography variant="h4" component="h1" gutterBottom>
          {t('profile.title')}
        </Typography>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Avatar
                sx={{ width: 120, height: 120, mx: 'auto', mb: 2 }}
                alt={`${user.first_name} ${user.last_name}`}
                src={user.avatar_url || ''}
              >
                {user.first_name && user.last_name ? 
                  `${user.first_name[0]}${user.last_name[0]}` : 
                  <PersonIcon fontSize="large" />
                }
              </Avatar>
              
              <Typography variant="h5" gutterBottom>
                {user.first_name} {user.last_name}
              </Typography>
              
              <Typography variant="body1" color="text.secondary" gutterBottom>
                {user.job_title}
                {user.job_title && user.department && ' • '}
                {user.department}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {user.email}
              </Typography>
              
              <Button
                variant="outlined"
                sx={{ mt: 2 }}
              >
                {t('profile.changeAvatar')}
              </Button>
              
              <Divider sx={{ my: 3 }} />
              
              <List>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={t('profile.username')} 
                    secondary={user.username} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <EventIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={t('profile.joinedDate')} 
                    secondary={new Date(user.date_joined).toLocaleDateString()} 
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary={t('profile.role')} 
                    secondary={user.is_admin ? t('profile.roles.admin') : 
                              user.is_manager ? t('profile.roles.manager') : 
                              user.is_analyst ? t('profile.roles.analyst') : 
                              t('profile.roles.user')} 
                  />
                </ListItem>
              </List>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <Paper sx={{ width: '100%' }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabValue} onChange={handleTabChange} aria-label="profile tabs">
                  <Tab icon={<PersonIcon />} label={t('profile.personalInfo')} />
                  <Tab icon={<SecurityIcon />} label={t('profile.security')} />
                  <Tab icon={<HistoryIcon />} label={t('profile.activity')} />
                  <Tab icon={<NotificationsIcon />} label={t('profile.notifications')} />
                </Tabs>
              </Box>
              
              <TabPanel value={tabValue} index={0}>
                <form onSubmit={formik.handleSubmit}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="first_name"
                        name="first_name"
                        label={t('profile.firstName')}
                        value={formik.values.first_name}
                        onChange={formik.handleChange}
                        error={formik.touched.first_name && Boolean(formik.errors.first_name)}
                        helperText={formik.touched.first_name && formik.errors.first_name}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="last_name"
                        name="last_name"
                        label={t('profile.lastName')}
                        value={formik.values.last_name}
                        onChange={formik.handleChange}
                        error={formik.touched.last_name && Boolean(formik.errors.last_name)}
                        helperText={formik.touched.last_name && formik.errors.last_name}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="email"
                        name="email"
                        label={t('profile.email')}
                        value={formik.values.email}
                        onChange={formik.handleChange}
                        error={formik.touched.email && Boolean(formik.errors.email)}
                        helperText={formik.touched.email && formik.errors.email}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="phone"
                        name="phone"
                        label={t('profile.phone')}
                        value={formik.values.phone}
                        onChange={formik.handleChange}
                        error={formik.touched.phone && Boolean(formik.errors.phone)}
                        helperText={formik.touched.phone && formik.errors.phone}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="job_title"
                        name="job_title"
                        label={t('profile.jobTitle')}
                        value={formik.values.job_title}
                        onChange={formik.handleChange}
                        error={formik.touched.job_title && Boolean(formik.errors.job_title)}
                        helperText={formik.touched.job_title && formik.errors.job_title}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        id="department"
                        name="department"
                        label={t('profile.department')}
                        value={formik.values.department}
                        onChange={formik.handleChange}
                        error={formik.touched.department && Boolean(formik.errors.department)}
                        helperText={formik.touched.department && formik.errors.department}
                        margin="normal"
                      />
                    </Grid>
                    
                    <Grid item xs={12}>
                      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                        <Button
                          type="submit"
                          variant="contained"
                          color="primary"
                          startIcon={<SaveIcon />}
                          disabled={loading}
                        >
                          {loading ? t('common.saving') : t('common.save')}
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </form>
              </TabPanel>
              
              <TabPanel value={tabValue} index={1}>
                <Typography variant="h6" gutterBottom>
                  {t('profile.changePassword')}
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="password"
                      id="current_password"
                      name="current_password"
                      label={t('profile.currentPassword')}
                      margin="normal"
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="password"
                      id="new_password"
                      name="new_password"
                      label={t('profile.newPassword')}
                      margin="normal"
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      type="password"
                      id="confirm_password"
                      name="confirm_password"
                      label={t('profile.confirmPassword')}
                      margin="normal"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                      <Button
                        variant="contained"
                        color="primary"
                      >
                        {t('profile.updatePassword')}
                      </Button>
                    </Box>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 4 }} />
                
                <Typography variant="h6" gutterBottom>
                  {t('profile.twoFactorAuth')}
                </Typography>
                
                <Typography variant="body1" paragraph>
                  {t('profile.twoFactorDescription')}
                </Typography>
                
                <Button
                  variant="outlined"
                  color="primary"
                >
                  {t('profile.setupTwoFactor')}
                </Button>
              </TabPanel>
              
              <TabPanel value={tabValue} index={2}>
                <Typography variant="h6" gutterBottom>
                  {t('profile.recentActivity')}
                </Typography>
                
                <List>
                  {[1, 2, 3, 4, 5].map((item) => (
                    <ListItem key={item} divider>
                      <ListItemIcon>
                        {item % 3 === 0 ? <DescriptionIcon /> : 
                         item % 3 === 1 ? <AnalyticsIcon /> : 
                         <SecurityIcon />}
                      </ListItemIcon>
                      <ListItemText 
                        primary={t(`profile.activityItems.${item}.action`)} 
                        secondary={t(`profile.activityItems.${item}.time`)} 
                      />
                    </ListItem>
                  ))}
                </List>
              </TabPanel>
              
              <TabPanel value={tabValue} index={3}>
                <Typography variant="h6" gutterBottom>
                  {t('profile.notificationSettings')}
                </Typography>
                
                <Typography variant="body1" paragraph>
                  {t('profile.notificationDescription')}
                </Typography>
                
                <Grid container spacing={3}>
                  {['email', 'system', 'task', 'security'].map((category) => (
                    <Grid item xs={12} md={6} key={category}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            {t(`profile.notifications.${category}.title`)}
                          </Typography>
                          
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {t(`profile.notifications.${category}.description`)}
                          </Typography>
                          
                          <Button
                            variant="outlined"
                            size="small"
                          >
                            {t('profile.configure')}
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>
            </Paper>
          </Grid>
        </Grid>
      </Box>
      
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default ProfilePage;
