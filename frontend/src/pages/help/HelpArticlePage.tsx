import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Typography,
  Paper,
  Breadcrumbs,
  Link,
  Chip,
  Divider,
  Button,
  CircularProgress,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CategoryIcon from '@mui/icons-material/Category';
import LocalOfferIcon from '@mui/icons-material/LocalOffer';
import UpdateIcon from '@mui/icons-material/Update';
import ReactMarkdown from 'react-markdown';

import { AppDispatch, RootState } from '../../store';
import { fetchHelpArticle } from '../../features/help/helpSlice';

const HelpArticlePage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { currentArticle, loading } = useSelector((state: RootState) => state.help);
  
  useEffect(() => {
    if (id) {
      dispatch(fetchHelpArticle(parseInt(id)));
    }
  }, [dispatch, id]);
  
  const handleBack = () => {
    navigate('/help');
  };
  
  if (loading || !currentArticle) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Breadcrumbs sx={{ mb: 2 }}>
          <Link color="inherit" onClick={handleBack} sx={{ cursor: 'pointer' }}>
            {t('help.title')}
          </Link>
          <Typography color="text.primary">
            {currentArticle.title}
          </Typography>
        </Breadcrumbs>
        
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          sx={{ mb: 3 }}
        >
          {t('common.back')}
        </Button>
        
        <Paper sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {currentArticle.title}
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
            <Chip 
              icon={<CategoryIcon />} 
              label={t(`help.categories.${currentArticle.category.toLowerCase()}`, { defaultValue: currentArticle.category })} 
              color="primary" 
            />
            
            {currentArticle.tags.map((tag) => (
              <Chip 
                key={tag} 
                icon={<LocalOfferIcon />} 
                label={tag} 
                variant="outlined" 
              />
            ))}
            
            <Chip 
              icon={<UpdateIcon />} 
              label={`${t('help.updated')}: ${new Date(currentArticle.updated_at).toLocaleDateString()}`} 
              variant="outlined" 
              color="secondary" 
            />
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Box sx={{ typography: 'body1' }}>
            <ReactMarkdown>
              {currentArticle.content}
            </ReactMarkdown>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default HelpArticlePage;
