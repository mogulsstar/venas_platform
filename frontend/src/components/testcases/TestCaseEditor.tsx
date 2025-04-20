import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Box, 
  Paper, 
  Typography, 
  TextField, 
  Button, 
  Grid, 
  Divider, 
  IconButton,
  Tooltip,
  Card,
  CardContent,
  CardActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Image as ImageIcon,
  TableChart as TableIcon,
  Code as CodeIcon,
  FormatListBulleted as ListIcon,
  SmartToy as AIIcon,
  Send as SendIcon,
  History as HistoryIcon
} from '@mui/icons-material';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../store';

// Types
interface TestCaseEditorProps {
  testCaseId?: string;
  initialData?: TestCaseData;
  onSave?: (data: TestCaseData) => Promise<void>;
  onSubmitForReview?: (id: string) => Promise<void>;
  onGenerateAI?: (id: string, templateId: string, regulationId: string) => Promise<any>;
  readOnly?: boolean;
}

export interface TestCaseData {
  id?: string;
  name: string;
  description: string;
  cluster: string;
  template?: string;
  content: TestCaseContent;
  regulation_segment?: string;
  regulation_interpretation?: string;
  status: 'draft' | 'review' | 'published' | 'archived';
  is_ai_generated: boolean;
}

interface TestCaseContent {
  sections: TestCaseSection[];
  signals?: TestCaseSignal[];
  metadata?: Record<string, any>;
}

interface TestCaseSection {
  id: string;
  type: 'text' | 'image' | 'table' | 'code' | 'list';
  title?: string;
  content: any;
}

interface TestCaseSignal {
  id: string;
  name: string;
  description?: string;
  unit?: string;
  min_value?: number;
  max_value?: number;
  default_value?: number;
}

// Helper function to generate unique IDs
const generateId = () => Math.random().toString(36).substr(2, 9);

const TestCaseEditor: React.FC<TestCaseEditorProps> = ({
  testCaseId,
  initialData,
  onSave,
  onSubmitForReview,
  onGenerateAI,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  
  // State
  const [testCase, setTestCase] = useState<TestCaseData>(initialData || {
    name: '',
    description: '',
    cluster: '',
    content: { sections: [] },
    status: 'draft',
    is_ai_generated: false
  });
  
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [openAIDialog, setOpenAIDialog] = useState<boolean>(false);
  const [aiLoading, setAiLoading] = useState<boolean>(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // Load initial data
  useEffect(() => {
    if (initialData) {
      setTestCase(initialData);
      
      // Set the first section as active if there are sections
      if (initialData.content.sections.length > 0) {
        setActiveSection(initialData.content.sections[0].id);
      }
    }
  }, [initialData]);
  
  // Handle save
  const handleSave = async () => {
    if (onSave) {
      setSaving(true);
      try {
        await onSave(testCase);
        setSnackbar({
          open: true,
          message: t('common.saveSuccess'),
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: t('common.saveError'),
          severity: 'error'
        });
      } finally {
        setSaving(false);
      }
    }
  };
  
  // Handle submit for review
  const handleSubmitForReview = async () => {
    if (onSubmitForReview && testCaseId) {
      try {
        await onSubmitForReview(testCaseId);
        setSnackbar({
          open: true,
          message: t('testcases.submitForReviewSuccess'),
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: t('testcases.submitForReviewError'),
          severity: 'error'
        });
      }
    }
  };
  
  // Handle AI generation
  const handleGenerateAI = async () => {
    if (onGenerateAI && testCaseId && testCase.template && (testCase.regulation_segment || testCase.regulation_interpretation)) {
      setAiLoading(true);
      try {
        const regulationId = testCase.regulation_segment || testCase.regulation_interpretation || '';
        const result = await onGenerateAI(testCaseId, testCase.template, regulationId);
        
        // Update the test case with the AI-generated content
        if (result && result.content) {
          setTestCase(prev => ({
            ...prev,
            content: result.content,
            is_ai_generated: true
          }));
        }
        
        setSnackbar({
          open: true,
          message: t('testcases.aiGenerationSuccess'),
          severity: 'success'
        });
      } catch (error) {
        setSnackbar({
          open: true,
          message: t('testcases.aiGenerationError'),
          severity: 'error'
        });
      } finally {
        setAiLoading(false);
        setOpenAIDialog(false);
      }
    }
  };
  
  // Handle adding a new section
  const handleAddSection = (type: 'text' | 'image' | 'table' | 'code' | 'list') => {
    const newSection: TestCaseSection = {
      id: generateId(),
      type,
      title: '',
      content: type === 'text' ? '' : type === 'table' ? { rows: 3, cols: 3, data: [] } : []
    };
    
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        sections: [...prev.content.sections, newSection]
      }
    }));
    
    setActiveSection(newSection.id);
  };
  
  // Handle removing a section
  const handleRemoveSection = (id: string) => {
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        sections: prev.content.sections.filter(section => section.id !== id)
      }
    }));
    
    // If the active section is removed, set the first remaining section as active
    if (activeSection === id) {
      const remainingSections = testCase.content.sections.filter(section => section.id !== id);
      if (remainingSections.length > 0) {
        setActiveSection(remainingSections[0].id);
      } else {
        setActiveSection(null);
      }
    }
  };
  
  // Handle updating a section
  const handleUpdateSection = (id: string, updates: Partial<TestCaseSection>) => {
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        sections: prev.content.sections.map(section => 
          section.id === id ? { ...section, ...updates } : section
        )
      }
    }));
  };
  
  // Handle adding a signal
  const handleAddSignal = () => {
    const newSignal: TestCaseSignal = {
      id: generateId(),
      name: `Signal_${testCase.content.signals?.length || 0 + 1}`,
      description: '',
      unit: '',
    };
    
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        signals: [...(prev.content.signals || []), newSignal]
      }
    }));
  };
  
  // Handle removing a signal
  const handleRemoveSignal = (id: string) => {
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        signals: (prev.content.signals || []).filter(signal => signal.id !== id)
      }
    }));
  };
  
  // Handle updating a signal
  const handleUpdateSignal = (id: string, updates: Partial<TestCaseSignal>) => {
    setTestCase(prev => ({
      ...prev,
      content: {
        ...prev.content,
        signals: (prev.content.signals || []).map(signal => 
          signal.id === id ? { ...signal, ...updates } : signal
        )
      }
    }));
  };
  
  // Render section content based on type
  const renderSectionContent = (section: TestCaseSection) => {
    switch (section.type) {
      case 'text':
        return (
          <TextField
            fullWidth
            multiline
            minRows={4}
            value={section.content}
            onChange={(e) => handleUpdateSection(section.id, { content: e.target.value })}
            disabled={readOnly}
            variant="outlined"
            placeholder={t('testcases.enterTextHere')}
          />
        );
        
      case 'image':
        return (
          <Box sx={{ textAlign: 'center' }}>
            {section.content && typeof section.content === 'string' ? (
              <Box sx={{ position: 'relative' }}>
                <img 
                  src={section.content} 
                  alt={section.title || 'Image'} 
                  style={{ maxWidth: '100%', maxHeight: '400px' }} 
                />
                {!readOnly && (
                  <IconButton 
                    sx={{ position: 'absolute', top: 0, right: 0, bgcolor: 'rgba(255,255,255,0.7)' }}
                    onClick={() => handleUpdateSection(section.id, { content: '' })}
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
            ) : (
              !readOnly && (
                <Button
                  variant="outlined"
                  startIcon={<ImageIcon />}
                  component="label"
                  sx={{ my: 2 }}
                >
                  {t('common.uploadImage')}
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onload = (event) => {
                          handleUpdateSection(section.id, { content: event.target?.result as string });
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                  />
                </Button>
              )
            )}
          </Box>
        );
        
      case 'table':
        const tableData = section.content || { rows: 3, cols: 3, data: [] };
        
        // Initialize table data if empty
        if (!tableData.data || !tableData.data.length) {
          tableData.data = Array(tableData.rows).fill(0).map(() => 
            Array(tableData.cols).fill('')
          );
        }
        
        return (
          <Box sx={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <tbody>
                {Array(tableData.rows).fill(0).map((_, rowIndex) => (
                  <tr key={rowIndex}>
                    {Array(tableData.cols).fill(0).map((_, colIndex) => (
                      <td 
                        key={colIndex}
                        style={{ 
                          border: '1px solid #ddd', 
                          padding: '8px',
                          height: '40px'
                        }}
                      >
                        {readOnly ? (
                          tableData.data[rowIndex]?.[colIndex] || ''
                        ) : (
                          <TextField
                            fullWidth
                            variant="standard"
                            value={tableData.data[rowIndex]?.[colIndex] || ''}
                            onChange={(e) => {
                              const newData = [...tableData.data];
                              if (!newData[rowIndex]) newData[rowIndex] = [];
                              newData[rowIndex][colIndex] = e.target.value;
                              handleUpdateSection(section.id, { 
                                content: { ...tableData, data: newData } 
                              });
                            }}
                            InputProps={{ disableUnderline: true }}
                          />
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            
            {!readOnly && (
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Button
                  size="small"
                  onClick={() => {
                    const newData = [...tableData.data];
                    newData.push(Array(tableData.cols).fill(''));
                    handleUpdateSection(section.id, { 
                      content: { ...tableData, rows: tableData.rows + 1, data: newData } 
                    });
                  }}
                >
                  {t('common.addRow')}
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    const newData = tableData.data.map(row => [...row, '']);
                    handleUpdateSection(section.id, { 
                      content: { ...tableData, cols: tableData.cols + 1, data: newData } 
                    });
                  }}
                >
                  {t('common.addColumn')}
                </Button>
              </Box>
            )}
          </Box>
        );
        
      case 'code':
        return (
          <TextField
            fullWidth
            multiline
            minRows={6}
            value={section.content}
            onChange={(e) => handleUpdateSection(section.id, { content: e.target.value })}
            disabled={readOnly}
            variant="outlined"
            placeholder={t('testcases.enterCodeHere')}
            InputProps={{
              style: { fontFamily: 'monospace' }
            }}
          />
        );
        
      case 'list':
        const listItems = Array.isArray(section.content) ? section.content : [];
        
        return (
          <Box>
            {listItems.map((item, index) => (
              <Box key={index} sx={{ display: 'flex', mb: 1 }}>
                <TextField
                  fullWidth
                  value={item}
                  onChange={(e) => {
                    const newItems = [...listItems];
                    newItems[index] = e.target.value;
                    handleUpdateSection(section.id, { content: newItems });
                  }}
                  disabled={readOnly}
                  variant="outlined"
                  size="small"
                />
                {!readOnly && (
                  <IconButton
                    onClick={() => {
                      const newItems = listItems.filter((_, i) => i !== index);
                      handleUpdateSection(section.id, { content: newItems });
                    }}
                  >
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
            ))}
            
            {!readOnly && (
              <Button
                startIcon={<AddIcon />}
                onClick={() => {
                  handleUpdateSection(section.id, { content: [...listItems, ''] });
                }}
                sx={{ mt: 1 }}
              >
                {t('common.addItem')}
              </Button>
            )}
          </Box>
        );
        
      default:
        return null;
    }
  };
  
  // Render signals section
  const renderSignals = () => {
    const signals = testCase.content.signals || [];
    
    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          {t('testcases.signals')}
        </Typography>
        
        <Grid container spacing={2}>
          {signals.map(signal => (
            <Grid item xs={12} md={6} key={signal.id}>
              <Card variant="outlined">
                <CardContent>
                  <TextField
                    fullWidth
                    label={t('common.name')}
                    value={signal.name}
                    onChange={(e) => handleUpdateSignal(signal.id, { name: e.target.value })}
                    disabled={readOnly}
                    variant="outlined"
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  
                  <TextField
                    fullWidth
                    label={t('common.description')}
                    value={signal.description || ''}
                    onChange={(e) => handleUpdateSignal(signal.id, { description: e.target.value })}
                    disabled={readOnly}
                    variant="outlined"
                    size="small"
                    sx={{ mb: 2 }}
                  />
                  
                  <Grid container spacing={2}>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        label={t('common.unit')}
                        value={signal.unit || ''}
                        onChange={(e) => handleUpdateSignal(signal.id, { unit: e.target.value })}
                        disabled={readOnly}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        label={t('common.minValue')}
                        type="number"
                        value={signal.min_value || ''}
                        onChange={(e) => handleUpdateSignal(signal.id, { min_value: parseFloat(e.target.value) })}
                        disabled={readOnly}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        label={t('common.maxValue')}
                        type="number"
                        value={signal.max_value || ''}
                        onChange={(e) => handleUpdateSignal(signal.id, { max_value: parseFloat(e.target.value) })}
                        disabled={readOnly}
                        variant="outlined"
                        size="small"
                      />
                    </Grid>
                  </Grid>
                </CardContent>
                
                {!readOnly && (
                  <CardActions>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => handleRemoveSignal(signal.id)}
                    >
                      {t('common.remove')}
                    </Button>
                  </CardActions>
                )}
              </Card>
            </Grid>
          ))}
          
          {!readOnly && (
            <Grid item xs={12} md={6}>
              <Card 
                variant="outlined" 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  minHeight: 200,
                  border: '1px dashed #ccc'
                }}
              >
                <Button
                  startIcon={<AddIcon />}
                  onClick={handleAddSignal}
                >
                  {t('testcases.addSignal')}
                </Button>
              </Card>
            </Grid>
          )}
        </Grid>
      </Box>
    );
  };
  
  return (
    <Box>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              label={t('common.name')}
              value={testCase.name}
              onChange={(e) => setTestCase(prev => ({ ...prev, name: e.target.value }))}
              disabled={readOnly}
              variant="outlined"
              sx={{ mb: 2 }}
            />
            
            <TextField
              fullWidth
              label={t('common.description')}
              value={testCase.description}
              onChange={(e) => setTestCase(prev => ({ ...prev, description: e.target.value }))}
              disabled={readOnly}
              variant="outlined"
              multiline
              rows={2}
            />
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', justifyContent: 'space-between' }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {t('common.status')}: <strong>{t(`testcases.status.${testCase.status}`)}</strong>
              </Typography>
              
              {!readOnly && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  {testCase.status === 'draft' && (
                    <>
                      <Button
                        variant="outlined"
                        startIcon={<SendIcon />}
                        onClick={handleSubmitForReview}
                        sx={{ mr: 1 }}
                      >
                        {t('testcases.submitForReview')}
                      </Button>
                      
                      <Button
                        variant="contained"
                        startIcon={<SaveIcon />}
                        onClick={handleSave}
                        disabled={saving}
                      >
                        {saving ? <CircularProgress size={24} /> : t('common.save')}
                      </Button>
                    </>
                  )}
                </Box>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {/* AI Generation Button */}
      {!readOnly && testCase.status === 'draft' && (
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<AIIcon />}
            onClick={() => setOpenAIDialog(true)}
            disabled={!testCase.template || !(testCase.regulation_segment || testCase.regulation_interpretation)}
          >
            {t('testcases.generateAI')}
          </Button>
        </Box>
      )}
      
      {/* Content Editor */}
      <Grid container spacing={3}>
        {/* Sections List */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              {t('common.sections')}
            </Typography>
            
            <List>
              {testCase.content.sections.map((section, index) => (
                <ListItem
                  key={section.id}
                  button
                  selected={activeSection === section.id}
                  onClick={() => setActiveSection(section.id)}
                  sx={{ 
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: activeSection === section.id ? 'action.selected' : 'transparent'
                  }}
                >
                  <ListItemText 
                    primary={section.title || `${t(`testcases.section`)} ${index + 1}`}
                    secondary={t(`testcases.${section.type}Section`)}
                  />
                  
                  {!readOnly && (
                    <IconButton
                      edge="end"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveSection(section.id);
                      }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </ListItem>
              ))}
            </List>
            
            {!readOnly && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('common.addSection')}
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  <Tooltip title={t('testcases.addTextSection')}>
                    <IconButton onClick={() => handleAddSection('text')}>
                      <TextIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title={t('testcases.addImageSection')}>
                    <IconButton onClick={() => handleAddSection('image')}>
                      <ImageIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title={t('testcases.addTableSection')}>
                    <IconButton onClick={() => handleAddSection('table')}>
                      <TableIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title={t('testcases.addCodeSection')}>
                    <IconButton onClick={() => handleAddSection('code')}>
                      <CodeIcon />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title={t('testcases.addListSection')}>
                    <IconButton onClick={() => handleAddSection('list')}>
                      <ListIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Section Editor */}
        <Grid item xs={12} md={9}>
          <Paper sx={{ p: 2 }}>
            {activeSection ? (
              <>
                {/* Active Section */}
                {(() => {
                  const section = testCase.content.sections.find(s => s.id === activeSection);
                  if (!section) return null;
                  
                  return (
                    <>
                      <Box sx={{ mb: 3 }}>
                        <TextField
                          fullWidth
                          label={t('common.sectionTitle')}
                          value={section.title || ''}
                          onChange={(e) => handleUpdateSection(section.id, { title: e.target.value })}
                          disabled={readOnly}
                          variant="outlined"
                        />
                      </Box>
                      
                      <Box>
                        {renderSectionContent(section)}
                      </Box>
                    </>
                  );
                })()}
              </>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  {testCase.content.sections.length === 0
                    ? t('testcases.noSectionsYet')
                    : t('testcases.selectSectionToEdit')}
                </Typography>
                
                {!readOnly && testCase.content.sections.length === 0 && (
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={() => handleAddSection('text')}
                    sx={{ mt: 2 }}
                  >
                    {t('testcases.addFirstSection')}
                  </Button>
                )}
              </Box>
            )}
          </Paper>
          
          {/* Signals */}
          <Paper sx={{ p: 2, mt: 3 }}>
            {renderSignals()}
          </Paper>
        </Grid>
      </Grid>
      
      {/* AI Generation Dialog */}
      <Dialog open={openAIDialog} onClose={() => setOpenAIDialog(false)}>
        <DialogTitle>{t('testcases.generateAI')}</DialogTitle>
        
        <DialogContent>
          <Typography variant="body2" paragraph>
            {t('testcases.aiGenerationDescription')}
          </Typography>
          
          <Typography variant="body2" color="warning.main" paragraph>
            {t('testcases.aiGenerationWarning')}
          </Typography>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setOpenAIDialog(false)}>
            {t('common.cancel')}
          </Button>
          
          <Button 
            variant="contained" 
            onClick={handleGenerateAI}
            disabled={aiLoading}
            startIcon={aiLoading ? <CircularProgress size={20} /> : <AIIcon />}
          >
            {t('testcases.generateWithAI')}
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

export default TestCaseEditor;
