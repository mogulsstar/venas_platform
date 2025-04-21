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
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

import { AppDispatch, RootState } from '../../store';
import { fetchRegulations, deleteRegulation, Regulation } from '../../features/regulations/regulationsSlice';

const RegulationsPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { regulations, loading } = useSelector((state: RootState) => state.regulations);

  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [regulationToDelete, setRegulationToDelete] = useState<number | null>(null);

  useEffect(() => {
    dispatch(fetchRegulations());
  }, [dispatch]);

  const handleViewRegulation = (id: number) => {
    navigate(`/regulations/${id}`);
  };

  const handleEditRegulation = (id: number) => {
    navigate(`/regulations/${id}?edit=true`);
  };

  const handleDeleteClick = (id: number) => {
    setRegulationToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (regulationToDelete) {
      dispatch(deleteRegulation(regulationToDelete));
      setDeleteDialogOpen(false);
      setRegulationToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setRegulationToDelete(null);
  };

  const handleAddRegulation = () => {
    navigate('/regulations/new');
  };

  // Filter regulations based on search term and filters
  const filteredRegulations = Array.isArray(regulations) ? regulations.filter((regulation) => {
    const matchesSearch =
      regulation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      regulation.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = filterType ? regulation.regulation_type === filterType : true;
    const matchesStatus = filterStatus ? regulation.status === filterStatus : true;

    return matchesSearch && matchesType && matchesStatus;
  }) : [];

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'name', headerName: t('regulations.name'), flex: 1 },
    { field: 'regulation_type', headerName: t('regulations.type'), width: 150 },
    { field: 'status', headerName: t('regulations.status'), width: 120 },
    {
      field: 'effective_date',
      headerName: t('regulations.effectiveDate'),
      width: 150,
      valueFormatter: (params) => {
        if (!params.value) return '';
        return new Date(params.value).toLocaleDateString();
      }
    },
    { field: 'jurisdiction', headerName: t('regulations.jurisdiction'), width: 150 },
    {
      field: 'actions',
      headerName: t('common.actions'),
      width: 150,
      sortable: false,
      renderCell: (params: GridRenderCellParams) => (
        <Box>
          <Tooltip title={t('common.view')}>
            <IconButton onClick={() => handleViewRegulation(params.row.id)} size="small">
              <VisibilityIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title={t('common.edit')}>
            <IconButton onClick={() => handleEditRegulation(params.row.id)} size="small">
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
              {t('regulations.title')}
            </Typography>
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleAddRegulation}
            >
              {t('regulations.addRegulation')}
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
                label={t('regulations.filterByType')}
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                variant="outlined"
                size="small"
              >
                <MenuItem value="">{t('common.all')}</MenuItem>
                <MenuItem value="FINANCIAL">{t('regulations.types.financial')}</MenuItem>
                <MenuItem value="ENVIRONMENTAL">{t('regulations.types.environmental')}</MenuItem>
                <MenuItem value="HEALTH">{t('regulations.types.health')}</MenuItem>
                <MenuItem value="SAFETY">{t('regulations.types.safety')}</MenuItem>
                <MenuItem value="OTHER">{t('regulations.types.other')}</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                select
                fullWidth
                label={t('regulations.filterByStatus')}
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                variant="outlined"
                size="small"
              >
                <MenuItem value="">{t('common.all')}</MenuItem>
                <MenuItem value="DRAFT">{t('regulations.statuses.draft')}</MenuItem>
                <MenuItem value="ACTIVE">{t('regulations.statuses.active')}</MenuItem>
                <MenuItem value="INACTIVE">{t('regulations.statuses.inactive')}</MenuItem>
                <MenuItem value="ARCHIVED">{t('regulations.statuses.archived')}</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        <Card>
          <CardContent>
            <div style={{ height: 600, width: '100%' }}>
              <DataGrid
                rows={filteredRegulations}
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
        <DialogTitle>{t('regulations.deleteConfirmTitle')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('regulations.deleteConfirmMessage')}
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

export default RegulationsPage;
