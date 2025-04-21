import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  IconButton,
  Tooltip,
  Paper,
  Chip,
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

import { AppDispatch, RootState } from '../../store';
import {
  fetchAnalysisTasks,
  deleteAnalysisTask,
  runAnalysisTask
} from '../../features/analysis/analysisSlice';

const AnalysisPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { tasks, loading } = useSelector((state: RootState) => state.analysis);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);

  useEffect(() => {
    console.log('AnalysisPage - Fetching analysis tasks');
    dispatch(fetchAnalysisTasks())
      .unwrap()
      .then(tasks => {
        console.log('Analysis tasks fetched successfully:', tasks);
      })
      .catch(error => {
        console.error('Failed to fetch analysis tasks:', error);
      });
  }, [dispatch]);

  const handleViewTask = (id: number) => {
    navigate(`/analysis/${id}`);
  };

  const handleEditTask = (id: number) => {
    navigate(`/analysis/${id}?edit=true`);
  };

  const handleDeleteClick = (id: number) => {
    setTaskToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (taskToDelete) {
      dispatch(deleteAnalysisTask(taskToDelete));
      setDeleteDialogOpen(false);
      setTaskToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setTaskToDelete(null);
  };

  const handleAddTask = () => {
    navigate('/analysis/new');
  };

  const handleRunTask = (id: number) => {
    dispatch(runAnalysisTask(id));
  };

  // Filter tasks based on search term and filters
  const filteredTasks = Array.isArray(tasks) ? tasks.filter((task) => {
    const matchesSearch =
      task.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      task.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = filterType ? task.analysis_type === filterType : true;
    const matchesStatus = filterStatus ? task.status === filterStatus : true;

    return matchesSearch && matchesType && matchesStatus;
  }) : [];

  const getStatusChip = (status: string) => {
    let color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';

    switch (status) {
      case 'PENDING':
        color = 'default';
        break;
      case 'RUNNING':
        color = 'info';
        break;
      case 'COMPLETED':
        color = 'success';
        break;
      case 'FAILED':
        color = 'error';
        break;
      case 'CANCELLED':
        color = 'warning';
        break;
    }

    return (
      <Chip
        label={t(`analysis.statuses.${status.toLowerCase()}`)}
        color={color}
        size="small"
      />
    );
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: t('analysis.name'), flex: 1 },
    { field: 'analysis_type', headerName: t('analysis.type'), width: 150 },
    {
      field: 'status',
      headerName: t('analysis.status'),
      width: 150,
      renderCell: (params) => getStatusChip(params.value as string)
    },
    {
      field: 'created_at',
      headerName: t('common.createdAt'),
      width: 150,
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Date(params.value).toLocaleDateString();
      }
    },
    {
      field: 'completed_at',
      headerName: t('analysis.completedAt'),
      width: 150,
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Date(params.value).toLocaleDateString();
      }
    },
    {
      field: 'actions',
      headerName: t('common.actions'),
      width: 180,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title={t('common.view')}>
            <IconButton onClick={() => handleViewTask(params.row.id)} size="small">
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.edit')}>
            <IconButton onClick={() => handleEditTask(params.row.id)} size="small">
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.delete')}>
            <IconButton onClick={() => handleDeleteClick(params.row.id)} size="small">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          {params.row.status !== 'RUNNING' && (
            <Tooltip title={t('analysis.run')}>
              <IconButton onClick={() => handleRunTask(params.row.id)} size="small" color="primary">
                <PlayArrowIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      ),
    },
  ];

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Grid container justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
          <Grid item>
            <Typography variant="h4" component="h1" gutterBottom>
              {t('analysis.title')}
            </Typography>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddTask}
            >
              {t('analysis.addTask')}
            </Button>
          </Grid>
        </Grid>

        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label={t('common.search')}
                variant="outlined"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                label={t('analysis.filterByType')}
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                variant="outlined"
                size="small"
              >
                <MenuItem value="">{t('common.all')}</MenuItem>
                <MenuItem value="DATA_CLEANING">{t('analysis.types.dataCleaning')}</MenuItem>
                <MenuItem value="STATISTICAL">{t('analysis.types.statistical')}</MenuItem>
                <MenuItem value="PREDICTIVE">{t('analysis.types.predictive')}</MenuItem>
                <MenuItem value="VISUALIZATION">{t('analysis.types.visualization')}</MenuItem>
                <MenuItem value="CUSTOM">{t('analysis.types.custom')}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                label={t('analysis.filterByStatus')}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                variant="outlined"
                size="small"
              >
                <MenuItem value="">{t('common.all')}</MenuItem>
                <MenuItem value="PENDING">{t('analysis.statuses.pending')}</MenuItem>
                <MenuItem value="RUNNING">{t('analysis.statuses.running')}</MenuItem>
                <MenuItem value="COMPLETED">{t('analysis.statuses.completed')}</MenuItem>
                <MenuItem value="FAILED">{t('analysis.statuses.failed')}</MenuItem>
                <MenuItem value="CANCELLED">{t('analysis.statuses.cancelled')}</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        <Card>
          <CardContent>
            <div style={{ height: 600, width: '100%' }}>
              <DataGrid
                rows={filteredTasks}
                columns={columns}
                loading={loading}
                pageSizeOptions={[10, 25, 50]}
                initialState={{
                  pagination: {
                    paginationModel: { pageSize: 10 },
                  },
                }}
                disableRowSelectionOnClick
                autoHeight
              />
            </div>
          </CardContent>
        </Card>
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>{t('analysis.deleteConfirmTitle')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('analysis.deleteConfirmMessage')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            {t('common.cancel')}
          </Button>
          <Button onClick={handleDeleteConfirm} color="error">
            {t('common.delete')}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default AnalysisPage;
