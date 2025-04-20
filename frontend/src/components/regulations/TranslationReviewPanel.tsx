import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Grid, 
  Divider, 
  TextField,
  CircularProgress,
  Alert,
  Snackbar,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
  Edit as EditIcon,
  Translate as TranslateIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import api from '../../services/api';

interface Translation {
  title: string;
  content: string;
  is_verified: boolean;
}

interface Segment {
  id: number;
  title: string;
  content: string;
  segment_type: string;
  document_id: number;
  document_title: string;
  translations: Record<string, Translation>;
}

interface TranslationReviewPanelProps {
  documentId?: number;
  language?: string;
  onClose?: () => void;
}

const TranslationReviewPanel: React.FC<TranslationReviewPanelProps> = ({ 
  documentId, 
  language = 'zh-hans',
  onClose 
}) => {
  const { t, i18n } = useTranslation();
  
  // State
  const [segments, setSegments] = useState<Segment[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedSegment, setSelectedSegment] = useState<Segment | null>(null);
  const [editedTranslation, setEditedTranslation] = useState<Translation | null>(null);
  const [openEditDialog, setOpenEditDialog] = useState<boolean>(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Load segments with unverified translations
  useEffect(() => {
    fetchSegments();
  }, [documentId, language]);
  
  const fetchSegments = async () => {
    setLoading(true);
    
    try {
      let url = '/api/v1/regulations/segments/?has_translation=true';
      
      if (documentId) {
        url += `&document=${documentId}`;
      }
      
      const response = await api.get(url);
      const allSegments = response.data.results || [];
      
      // Filter segments that have unverified translations in the selected language
      const filteredSegments = allSegments.filter(segment => 
        segment.translations && 
        segment.translations[language] && 
        !segment.translations[language].is_verified
      );
      
      setSegments(filteredSegments);
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  
  // Handle approving a translation
  const handleApproveTranslation = async (segment: Segment) => {
    try {
      const translation = segment.translations[language];
      
      // Update the translation's is_verified flag
      const updatedTranslations = {
        ...segment.translations,
        [language]: {
          ...translation,
          is_verified: true
        }
      };
      
      // Send the update to the API
      await api.patch(`/api/v1/regulations/segments/${segment.id}/`, {
        translations: updatedTranslations
      });
      
      // Update local state
      setSegments(prev => prev.filter(s => s.id !== segment.id));
      
      setSnackbar({
        open: true,
        message: t('regulations.translationApproved'),
        severity: 'success'
      });
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    }
  };
  
  // Handle editing a translation
  const handleEditTranslation = (segment: Segment) => {
    setSelectedSegment(segment);
    setEditedTranslation(segment.translations[language]);
    setOpenEditDialog(true);
  };
  
  // Handle saving edited translation
  const handleSaveEditedTranslation = async () => {
    if (!selectedSegment || !editedTranslation) return;
    
    try {
      // Update the translation
      const updatedTranslations = {
        ...selectedSegment.translations,
        [language]: editedTranslation
      };
      
      // Send the update to the API
      await api.patch(`/api/v1/regulations/segments/${selectedSegment.id}/`, {
        translations: updatedTranslations
      });
      
      // Update local state
      setSegments(prev => prev.map(segment => 
        segment.id === selectedSegment.id 
          ? { ...segment, translations: updatedTranslations } 
          : segment
      ));
      
      setSnackbar({
        open: true,
        message: t('regulations.translationUpdated'),
        severity: 'success'
      });
      
      // Close the dialog
      setOpenEditDialog(false);
      setSelectedSegment(null);
      setEditedTranslation(null);
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    }
  };
  
  // Handle rejecting a translation
  const handleRejectTranslation = async (segment: Segment) => {
    try {
      // Remove the translation for this language
      const updatedTranslations = { ...segment.translations };
      delete updatedTranslations[language];
      
      // Send the update to the API
      await api.patch(`/api/v1/regulations/segments/${segment.id}/`, {
        translations: updatedTranslations
      });
      
      // Update local state
      setSegments(prev => prev.filter(s => s.id !== segment.id));
      
      setSnackbar({
        open: true,
        message: t('regulations.translationRejected'),
        severity: 'success'
      });
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    }
  };
  
  // Render language name
  const renderLanguageName = (langCode: string) => {
    switch (langCode) {
      case 'en':
        return 'English';
      case 'zh-hans':
        return '中文 (Chinese)';
      case 'de':
        return 'Deutsch (German)';
      default:
        return langCode;
    }
  };
  
  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            {t('regulations.translationReview')}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 120, mr: 2 }}>
              <InputLabel>{t('common.language')}</InputLabel>
              <Select
                value={language}
                label={t('common.language')}
                onChange={(e) => window.location.href = `?language=${e.target.value}`}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="zh-hans">中文 (Chinese)</MenuItem>
                <MenuItem value="de">Deutsch (German)</MenuItem>
              </Select>
            </FormControl>
            
            <Tooltip title={t('common.refresh')}>
              <IconButton onClick={fetchSegments}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Divider sx={{ mb: 2 }} />
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : segments.length === 0 ? (
          <Alert severity="info">
            {t('regulations.noTranslationsToReview')}
          </Alert>
        ) : (
          <List>
            {segments.map(segment => (
              <Card key={segment.id} sx={{ mb: 2 }}>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    {segment.title}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t('regulations.fromDocument')}: {segment.document_title}
                  </Typography>
                  
                  <Chip 
                    label={segment.segment_type} 
                    size="small" 
                    color="primary" 
                    sx={{ mb: 2 }}
                  />
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        {t('common.original')} ({segment.translations[language]?.language || 'en'})
                      </Typography>
                      
                      <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', minHeight: 100 }}>
                        <Typography variant="body2">
                          {segment.content}
                        </Typography>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <Typography variant="subtitle2" gutterBottom>
                        {t('common.translation')} ({renderLanguageName(language)})
                      </Typography>
                      
                      <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', minHeight: 100 }}>
                        <Typography variant="body2">
                          {segment.translations[language]?.content}
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
                
                <CardActions>
                  <Button
                    startIcon={<EditIcon />}
                    onClick={() => handleEditTranslation(segment)}
                  >
                    {t('common.edit')}
                  </Button>
                  
                  <Button
                    color="error"
                    startIcon={<RejectIcon />}
                    onClick={() => handleRejectTranslation(segment)}
                  >
                    {t('common.reject')}
                  </Button>
                  
                  <Button
                    color="success"
                    startIcon={<ApproveIcon />}
                    onClick={() => handleApproveTranslation(segment)}
                  >
                    {t('common.approve')}
                  </Button>
                </CardActions>
              </Card>
            ))}
          </List>
        )}
      </Paper>
      
      {/* Edit Translation Dialog */}
      <Dialog open={openEditDialog} onClose={() => setOpenEditDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {t('regulations.editTranslation')}
        </DialogTitle>
        
        <DialogContent>
          {selectedSegment && editedTranslation && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('common.original')} ({selectedSegment.translations[language]?.language || 'en'})
                </Typography>
                
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default', minHeight: 100 }}>
                  <Typography variant="body2">
                    {selectedSegment.content}
                  </Typography>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('common.translation')} ({renderLanguageName(language)})
                </Typography>
                
                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  value={editedTranslation.content}
                  onChange={(e) => setEditedTranslation(prev => 
                    prev ? { ...prev, content: e.target.value } : null
                  )}
                  variant="outlined"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('common.title')}
                </Typography>
                
                <TextField
                  fullWidth
                  value={editedTranslation.title}
                  onChange={(e) => setEditedTranslation(prev => 
                    prev ? { ...prev, title: e.target.value } : null
                  )}
                  variant="outlined"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setOpenEditDialog(false)}>
            {t('common.cancel')}
          </Button>
          
          <Button 
            onClick={handleSaveEditedTranslation} 
            color="primary"
            startIcon={<SaveIcon />}
          >
            {t('common.save')}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default TranslationReviewPanel;
