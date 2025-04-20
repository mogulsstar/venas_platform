import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  CardMedia,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Info as InfoIcon
} from '@mui/icons-material';

import api from '../../services/api';

// Types
interface Template {
  id: number;
  name: string;
  description: string;
  structure: any;
  created_by: number;
  created_at: string;
  updated_at: string;
  thumbnail?: string;
}

interface TemplateSelectorProps {
  onSelectTemplate: (template: Template) => void;
  selectedTemplateId?: number;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({ 
  onSelectTemplate,
  selectedTemplateId
}) => {
  const { t } = useTranslation();
  
  // State
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [previewOpen, setPreviewOpen] = useState<boolean>(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Load templates on mount
  useEffect(() => {
    fetchTemplates();
  }, []);
  
  // Set selected template if selectedTemplateId is provided
  useEffect(() => {
    if (selectedTemplateId && templates.length > 0) {
      const template = templates.find(t => t.id === selectedTemplateId);
      if (template) {
        setSelectedTemplate(template);
      }
    }
  }, [selectedTemplateId, templates]);
  
  // Fetch templates from API
  const fetchTemplates = async () => {
    setLoading(true);
    
    try {
      const response = await api.get('/api/v1/testcases/templates/');
      setTemplates(response.data.results || []);
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
  
  // Handle template selection
  const handleSelectTemplate = (template: Template) => {
    setSelectedTemplate(template);
    onSelectTemplate(template);
  };
  
  // Handle template preview
  const handlePreviewTemplate = (template: Template) => {
    setSelectedTemplate(template);
    setPreviewOpen(true);
  };
  
  // Filter templates based on search query
  const filteredTemplates = templates.filter(template => 
    template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    template.description.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Render template preview
  const renderTemplatePreview = () => {
    if (!selectedTemplate) return null;
    
    return (
      <Dialog open={previewOpen} onClose={() => setPreviewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTemplate.name}
        </DialogTitle>
        
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom>
            {t('common.description')}
          </Typography>
          
          <Typography variant="body2" paragraph>
            {selectedTemplate.description}
          </Typography>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="subtitle1" gutterBottom>
            {t('testcases.templateStructure')}
          </Typography>
          
          <Box sx={{ bgcolor: 'background.default', p: 2, borderRadius: 1, overflow: 'auto', maxHeight: 400 }}>
            <pre>{JSON.stringify(selectedTemplate.structure, null, 2)}</pre>
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            {t('common.close')}
          </Button>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => {
              handleSelectTemplate(selectedTemplate);
              setPreviewOpen(false);
            }}
          >
            {t('testcases.useTemplate')}
          </Button>
        </DialogActions>
      </Dialog>
    );
  };
  
  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            {t('testcases.selectTemplate')}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <TextField
              placeholder={t('common.search')}
              size="small"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
              }}
              sx={{ mr: 1 }}
            />
            
            <Tooltip title={t('common.refresh')}>
              <IconButton onClick={fetchTemplates}>
                <FilterIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : filteredTemplates.length === 0 ? (
          <Alert severity="info">
            {searchQuery 
              ? t('testcases.noTemplatesFound') 
              : t('testcases.noTemplatesAvailable')}
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {filteredTemplates.map(template => (
              <Grid item xs={12} sm={6} md={4} key={template.id}>
                <Card 
                  variant="outlined" 
                  sx={{ 
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    borderColor: selectedTemplateId === template.id ? 'primary.main' : 'divider'
                  }}
                >
                  {template.thumbnail && (
                    <CardMedia
                      component="img"
                      height="140"
                      image={template.thumbnail}
                      alt={template.name}
                    />
                  )}
                  
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {template.name}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary">
                      {template.description.length > 100 
                        ? `${template.description.substring(0, 100)}...` 
                        : template.description}
                    </Typography>
                  </CardContent>
                  
                  <CardActions>
                    <Button 
                      size="small" 
                      startIcon={<InfoIcon />}
                      onClick={() => handlePreviewTemplate(template)}
                    >
                      {t('common.preview')}
                    </Button>
                    
                    <Button 
                      size="small" 
                      variant="contained" 
                      color="primary"
                      onClick={() => handleSelectTemplate(template)}
                      disabled={selectedTemplateId === template.id}
                    >
                      {selectedTemplateId === template.id 
                        ? t('testcases.selected') 
                        : t('testcases.select')}
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
      
      {renderTemplatePreview()}
      
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

export default TemplateSelector;
