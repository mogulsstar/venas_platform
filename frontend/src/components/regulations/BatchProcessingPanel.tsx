import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Checkbox, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Translate as TranslateIcon,
  PlayArrow as ProcessIcon
} from '@mui/icons-material';

import { AppDispatch, RootState } from '../../store';
import { fetchDocuments } from '../../features/regulations/regulationsSlice';
import api from '../../services/api';

interface BatchProcessingPanelProps {
  onClose?: () => void;
}

const BatchProcessingPanel: React.FC<BatchProcessingPanelProps> = ({ onClose }) => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  
  // Get documents from Redux store
  const { documents } = useSelector((state: RootState) => state.regulations);
  
  // State
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>([]);
  const [processing, setProcessing] = useState<boolean>(false);
  const [translating, setTranslating] = useState<boolean>(false);
  const [targetLanguage, setTargetLanguage] = useState<string>('');
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Filter for unprocessed PDF documents
  const unprocessedDocuments = documents.filter(doc => 
    !doc.is_processed && doc.file_type === 'pdf'
  );
  
  // Filter for processed documents
  const processedDocuments = documents.filter(doc => 
    doc.is_processed
  );
  
  // Load documents on mount
  useEffect(() => {
    dispatch(fetchDocuments());
  }, [dispatch]);
  
  // Handle document selection
  const handleToggleDocument = (documentId: number) => {
    setSelectedDocuments(prev => {
      if (prev.includes(documentId)) {
        return prev.filter(id => id !== documentId);
      } else {
        return [...prev, documentId];
      }
    });
  };
  
  // Handle select all unprocessed documents
  const handleSelectAllUnprocessed = () => {
    setSelectedDocuments(unprocessedDocuments.map(doc => doc.id));
  };
  
  // Handle select all processed documents
  const handleSelectAllProcessed = () => {
    setSelectedDocuments(processedDocuments.map(doc => doc.id));
  };
  
  // Handle clear selection
  const handleClearSelection = () => {
    setSelectedDocuments([]);
  };
  
  // Handle batch processing
  const handleBatchProcess = async () => {
    if (selectedDocuments.length === 0) {
      setSnackbar({
        open: true,
        message: t('regulations.noDocumentsSelected'),
        severity: 'warning'
      });
      return;
    }
    
    setProcessing(true);
    
    try {
      const response = await api.post('/api/v1/regulations/documents/batch_process/', {
        document_ids: selectedDocuments
      });
      
      setSnackbar({
        open: true,
        message: t('regulations.batchProcessingStarted', {
          count: response.data.processing_count,
          skipped: response.data.skipped_count
        }),
        severity: 'success'
      });
      
      // Clear selection
      setSelectedDocuments([]);
      
      // Refresh documents list
      dispatch(fetchDocuments());
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    } finally {
      setProcessing(false);
    }
  };
  
  // Handle language change
  const handleLanguageChange = (event: SelectChangeEvent<string>) => {
    setTargetLanguage(event.target.value);
  };
  
  // Handle batch translation
  const handleBatchTranslate = async () => {
    if (selectedDocuments.length === 0) {
      setSnackbar({
        open: true,
        message: t('regulations.noDocumentsSelected'),
        severity: 'warning'
      });
      return;
    }
    
    if (!targetLanguage) {
      setSnackbar({
        open: true,
        message: t('regulations.noLanguageSelected'),
        severity: 'warning'
      });
      return;
    }
    
    setTranslating(true);
    
    try {
      // Get all segments for selected documents
      const segmentIds: number[] = [];
      
      for (const documentId of selectedDocuments) {
        const response = await api.get(`/api/v1/regulations/segments/?document=${documentId}`);
        const segments = response.data.results || [];
        segmentIds.push(...segments.map((segment: any) => segment.id));
      }
      
      if (segmentIds.length === 0) {
        setSnackbar({
          open: true,
          message: t('regulations.noSegmentsFound'),
          severity: 'warning'
        });
        setTranslating(false);
        return;
      }
      
      // Start batch translation
      const response = await api.post('/api/v1/regulations/segments/batch_translate/', {
        segment_ids: segmentIds,
        language: targetLanguage
      });
      
      setSnackbar({
        open: true,
        message: t('regulations.batchTranslationStarted', {
          documents: response.data.document_count,
          segments: response.data.segment_count
        }),
        severity: 'success'
      });
      
      // Clear selection
      setSelectedDocuments([]);
    } catch (error: any) {
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || t('common.errorOccurred'),
        severity: 'error'
      });
    } finally {
      setTranslating(false);
    }
  };
  
  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          {t('regulations.batchProcessing')}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            {t('regulations.unprocessedDocuments')} ({unprocessedDocuments.length})
          </Typography>
          
          <Box sx={{ display: 'flex', mb: 1 }}>
            <Button 
              size="small" 
              onClick={handleSelectAllUnprocessed}
              disabled={unprocessedDocuments.length === 0}
            >
              {t('common.selectAll')}
            </Button>
            <Button 
              size="small" 
              onClick={handleClearSelection}
              disabled={selectedDocuments.length === 0}
              sx={{ ml: 1 }}
            >
              {t('common.clearSelection')}
            </Button>
          </Box>
          
          <List dense sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'background.paper' }}>
            {unprocessedDocuments.length === 0 ? (
              <ListItem>
                <ListItemText primary={t('regulations.noUnprocessedDocuments')} />
              </ListItem>
            ) : (
              unprocessedDocuments.map(doc => (
                <ListItem 
                  key={doc.id}
                  button
                  onClick={() => handleToggleDocument(doc.id)}
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={selectedDocuments.includes(doc.id)}
                      tabIndex={-1}
                      disableRipple
                    />
                  </ListItemIcon>
                  <ListItemText 
                    primary={doc.title} 
                    secondary={`${doc.document_number || ''} ${doc.country_name || ''}`}
                  />
                </ListItem>
              ))
            )}
          </List>
          
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<ProcessIcon />}
              onClick={handleBatchProcess}
              disabled={selectedDocuments.length === 0 || processing}
            >
              {processing ? <CircularProgress size={24} /> : t('regulations.processPDFs')}
            </Button>
          </Box>
        </Box>
        
        <Divider sx={{ my: 3 }} />
        
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            {t('regulations.processedDocuments')} ({processedDocuments.length})
          </Typography>
          
          <Box sx={{ display: 'flex', mb: 1 }}>
            <Button 
              size="small" 
              onClick={handleSelectAllProcessed}
              disabled={processedDocuments.length === 0}
            >
              {t('common.selectAll')}
            </Button>
            <Button 
              size="small" 
              onClick={handleClearSelection}
              disabled={selectedDocuments.length === 0}
              sx={{ ml: 1 }}
            >
              {t('common.clearSelection')}
            </Button>
          </Box>
          
          <List dense sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'background.paper' }}>
            {processedDocuments.length === 0 ? (
              <ListItem>
                <ListItemText primary={t('regulations.noProcessedDocuments')} />
              </ListItem>
            ) : (
              processedDocuments.map(doc => (
                <ListItem 
                  key={doc.id}
                  button
                  onClick={() => handleToggleDocument(doc.id)}
                >
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={selectedDocuments.includes(doc.id)}
                      tabIndex={-1}
                      disableRipple
                    />
                  </ListItemIcon>
                  <ListItemText 
                    primary={doc.title} 
                    secondary={`${doc.document_number || ''} ${doc.country_name || ''}`}
                  />
                </ListItem>
              ))
            )}
          </List>
          
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 120, mr: 2 }}>
              <InputLabel id="target-language-label">{t('common.language')}</InputLabel>
              <Select
                labelId="target-language-label"
                value={targetLanguage}
                label={t('common.language')}
                onChange={handleLanguageChange}
              >
                <MenuItem value="en">{t('languages.english')}</MenuItem>
                <MenuItem value="zh-hans">{t('languages.chinese')}</MenuItem>
                <MenuItem value="de">{t('languages.german')}</MenuItem>
              </Select>
            </FormControl>
            
            <Button
              variant="contained"
              color="secondary"
              startIcon={<TranslateIcon />}
              onClick={handleBatchTranslate}
              disabled={selectedDocuments.length === 0 || !targetLanguage || translating}
            >
              {translating ? <CircularProgress size={24} /> : t('regulations.translateDocuments')}
            </Button>
          </Box>
        </Box>
      </Paper>
      
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

export default BatchProcessingPanel;
