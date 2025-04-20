import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box, Typography, Button, Container, Paper } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';

const NotFoundPage: React.FC = () => {
  const { t } = useTranslation();
  
  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 5,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}
        >
          <Typography variant="h1" color="primary" sx={{ fontSize: '8rem', fontWeight: 'bold' }}>
            404
          </Typography>
          <Typography variant="h4" gutterBottom>
            {t('error.pageNotFound')}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            {t('error.pageNotFoundMessage')}
          </Typography>
          <Button
            component={Link}
            to="/"
            variant="contained"
            startIcon={<HomeIcon />}
            size="large"
          >
            {t('common.backToHome')}
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default NotFoundPage;
