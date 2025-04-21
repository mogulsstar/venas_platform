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
} from '@mui/material';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';

import { AppDispatch, RootState } from '../../store';
import { fetchTestCases, deleteTestCase } from '../../features/testcases/testcasesSlice';

const TestCasesPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { testCases, loading } = useSelector((state: RootState) => state.testcases);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [testCaseToDelete, setTestCaseToDelete] = useState<number | null>(null);

  useEffect(() => {
    dispatch(fetchTestCases());
  }, [dispatch]);

  const handleViewTestCase = (id: number) => {
    navigate(`/testcases/${id}`);
  };

  const handleEditTestCase = (id: number) => {
    navigate(`/testcases/${id}?edit=true`);
  };

  const handleDeleteClick = (id: number) => {
    setTestCaseToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (testCaseToDelete) {
      dispatch(deleteTestCase(testCaseToDelete));
      setDeleteDialogOpen(false);
      setTestCaseToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setTestCaseToDelete(null);
  };

  const handleAddTestCase = () => {
    navigate('/testcases/new');
  };

  // Filter test cases based on search term and filters
  const filteredTestCases = Array.isArray(testCases) ? testCases.filter((testCase) => {
    const matchesSearch =
      testCase.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      testCase.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = filterStatus ? testCase.status === filterStatus : true;

    return matchesSearch && matchesStatus;
  }) : [];

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: t('testcases.name'), flex: 1 },
    { field: 'status', headerName: t('testcases.status'), width: 120 },
    {
      field: 'regulation',
      headerName: t('testcases.regulation'),
      width: 150,
      valueGetter: (params) => params.row.regulation?.name || '',
    },
    {
      field: 'project',
      headerName: t('testcases.project'),
      width: 150,
      valueGetter: (params) => params.row.project?.name || '',
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
      field: 'actions',
      headerName: t('common.actions'),
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title={t('common.view')}>
            <IconButton onClick={() => handleViewTestCase(params.row.id)} size="small">
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.edit')}>
            <IconButton onClick={() => handleEditTestCase(params.row.id)} size="small">
              <EditIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.delete')}>
            <IconButton onClick={() => handleDeleteClick(params.row.id)} size="small">
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Tooltip>
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
              {t('testcases.title')}
            </Typography>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddTestCase}
            >
              {t('testcases.addTestCase')}
            </Button>
          </Grid>
        </Grid>

        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('common.search')}
                variant="outlined"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label={t('testcases.filterByStatus')}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                variant="outlined"
                size="small"
              >
                <MenuItem value="">{t('common.all')}</MenuItem>
                <MenuItem value="DRAFT">{t('testcases.statuses.draft')}</MenuItem>
                <MenuItem value="ACTIVE">{t('testcases.statuses.active')}</MenuItem>
                <MenuItem value="COMPLETED">{t('testcases.statuses.completed')}</MenuItem>
                <MenuItem value="ARCHIVED">{t('testcases.statuses.archived')}</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        <Card>
          <CardContent>
            <div style={{ height: 600, width: '100%' }}>
              <DataGrid
                rows={filteredTestCases}
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
        <DialogTitle>{t('testcases.deleteConfirmTitle')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('testcases.deleteConfirmMessage')}
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

export default TestCasesPage;
