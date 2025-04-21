import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import api from '../../services/api';

// Types
interface Country {
  id: number;
  name: string;
  code: string;
}

interface Region {
  id: number;
  name: string;
  country: number;
}

interface RegulationCategory {
  id: number;
  name: string;
  description: string;
  parent: number | null;
}

interface RegulationDocument {
  id: number;
  title: string;
  description: string;
  country: number;
  region: number | null;
  category: number;
  document_number: string;
  version: string;
  publication_date: string | null;
  effective_date: string | null;
  expiration_date: string | null;
  original_file: string;
  file_type: string;
  status: string;
  is_processed: boolean;
  processing_errors: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;
  previous_version: number | null;
}

// This type is used by RegulationsPage.tsx
export interface Regulation {
  id: number;
  name: string;
  description: string;
  regulation_type: string;
  status: string;
  effective_date: string;
  jurisdiction: string;
  document_url?: string;
  created_at: string;
  updated_at: string;
  created_by: {
    id: number;
    username: string;
  };
}

interface RegulationSegment {
  id: number;
  document: number;
  title: string | null;
  content: string;
  section_number: string | null;
  page_number: number;
  order: number;
  is_heading: boolean;
  is_table: boolean;
  is_figure: boolean;
}

interface RegulationInterpretation {
  id: number;
  segment: number;
  content: string;
  status: string;
  is_ai_generated: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  reviewed_at: string | null;
}

interface RegulationsState {
  countries: Country[];
  regions: Region[];
  categories: RegulationCategory[];
  documents: RegulationDocument[];
  currentDocument: RegulationDocument | null;
  segments: RegulationSegment[];
  interpretations: RegulationInterpretation[];
  regulations: Regulation[];
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: RegulationsState = {
  countries: [],
  regions: [],
  categories: [],
  documents: [],
  currentDocument: null,
  segments: [],
  interpretations: [],
  regulations: [],
  loading: false,
  error: null,
};

// Async thunks
export const fetchCountries = createAsyncThunk(
  'regulations/fetchCountries',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<Country[]>('/regulations/countries/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch countries');
    }
  }
);

export const fetchRegions = createAsyncThunk(
  'regulations/fetchRegions',
  async (countryId: number | null = null, { rejectWithValue }) => {
    try {
      const url = countryId
        ? `/regulations/regions/?country=${countryId}`
        : '/regulations/regions/';
      const response = await api.get<Region[]>(url);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch regions');
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'regulations/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<RegulationCategory[]>('/regulations/categories/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch categories');
    }
  }
);

export const fetchDocuments = createAsyncThunk(
  'regulations/fetchDocuments',
  async (
    filters: {
      country?: number;
      region?: number;
      category?: number;
      status?: string;
    } = {},
    { rejectWithValue }
  ) => {
    try {
      // Build query string
      const queryParams = new URLSearchParams();
      if (filters.country) queryParams.append('country', filters.country.toString());
      if (filters.region) queryParams.append('region', filters.region.toString());
      if (filters.category) queryParams.append('category', filters.category.toString());
      if (filters.status) queryParams.append('status', filters.status);

      const url = `/regulations/documents/?${queryParams.toString()}`;
      const response = await api.get<RegulationDocument[]>(url);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch documents');
    }
  }
);

// This function is used by RegulationsPage.tsx
export const fetchRegulations = createAsyncThunk(
  'regulations/fetchRegulations',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get<Regulation[]>('/regulations/');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch regulations');
    }
  }
);

export const fetchDocument = createAsyncThunk(
  'regulations/fetchDocument',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get<RegulationDocument>(`/regulations/documents/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch document');
    }
  }
);

// This function is used by RegulationDetailPage.tsx
export const fetchRegulation = createAsyncThunk(
  'regulations/fetchRegulation',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await api.get<Regulation>(`/regulations/${id}/`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch regulation');
    }
  }
);

export const fetchSegments = createAsyncThunk(
  'regulations/fetchSegments',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await api.get<RegulationSegment[]>(
        `/regulations/segments/?document=${documentId}`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch segments');
    }
  }
);

export const fetchInterpretations = createAsyncThunk(
  'regulations/fetchInterpretations',
  async (segmentId: number, { rejectWithValue }) => {
    try {
      const response = await api.get<RegulationInterpretation[]>(
        `/regulations/interpretations/?segment=${segmentId}`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch interpretations');
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'regulations/uploadDocument',
  async (
    {
      formData,
      onUploadProgress,
    }: {
      formData: FormData;
      onUploadProgress?: (progressEvent: any) => void;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post<RegulationDocument>('/regulations/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to upload document');
    }
  }
);

export const processDocument = createAsyncThunk(
  'regulations/processDocument',
  async (documentId: number, { rejectWithValue }) => {
    try {
      const response = await api.post<{ detail: string }>(
        `/regulations/documents/${documentId}/process/`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to process document');
    }
  }
);

export const createInterpretation = createAsyncThunk(
  'regulations/createInterpretation',
  async (
    {
      segmentId,
      content,
    }: {
      segmentId: number;
      content: string;
    },
    { rejectWithValue }
  ) => {
    try {
      const response = await api.post<RegulationInterpretation>('/regulations/interpretations/', {
        segment: segmentId,
        content,
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create interpretation');
    }
  }
);

export const generateAIInterpretation = createAsyncThunk(
  'regulations/generateAIInterpretation',
  async (segmentId: number, { rejectWithValue }) => {
    try {
      const response = await api.post<RegulationInterpretation>(
        `/regulations/segments/${segmentId}/generate_ai/`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to generate AI interpretation');
    }
  }
);

export const deleteRegulation = createAsyncThunk(
  'regulations/deleteRegulation',
  async (id: number, { rejectWithValue }) => {
    try {
      await api.delete(`/regulations/documents/${id}/`);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete regulation');
    }
  }
);

export const createRegulation = createAsyncThunk(
  'regulations/createRegulation',
  async (regulation: Partial<Regulation>, { rejectWithValue }) => {
    try {
      const response = await api.post('/regulations/', regulation);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create regulation');
    }
  }
);

export const updateRegulation = createAsyncThunk(
  'regulations/updateRegulation',
  async ({ id, data }: { id: number; data: Partial<Regulation> }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/regulations/${id}/`, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update regulation');
    }
  }
);

// Slice
const regulationsSlice = createSlice({
  name: 'regulations',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentDocument: (state, action: PayloadAction<RegulationDocument | null>) => {
      state.currentDocument = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch countries
      .addCase(fetchCountries.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCountries.fulfilled, (state, action: PayloadAction<Country[]>) => {
        state.loading = false;
        state.countries = action.payload;
        state.error = null;
      })
      .addCase(fetchCountries.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch regions
      .addCase(fetchRegions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRegions.fulfilled, (state, action: PayloadAction<Region[]>) => {
        state.loading = false;
        state.regions = action.payload;
        state.error = null;
      })
      .addCase(fetchRegions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch categories
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCategories.fulfilled, (state, action: PayloadAction<RegulationCategory[]>) => {
        state.loading = false;
        state.categories = action.payload;
        state.error = null;
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch documents
      .addCase(fetchDocuments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocuments.fulfilled, (state, action: PayloadAction<RegulationDocument[]>) => {
        state.loading = false;
        state.documents = action.payload;
        state.error = null;
      })
      .addCase(fetchDocuments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch regulations
      .addCase(fetchRegulations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRegulations.fulfilled, (state, action: PayloadAction<Regulation[]>) => {
        state.loading = false;
        state.regulations = action.payload;
        state.error = null;
      })
      .addCase(fetchRegulations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch document
      .addCase(fetchDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDocument.fulfilled, (state, action: PayloadAction<RegulationDocument>) => {
        state.loading = false;
        state.currentDocument = action.payload;
        state.error = null;
      })
      .addCase(fetchDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch regulation
      .addCase(fetchRegulation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRegulation.fulfilled, (state, action: PayloadAction<Regulation>) => {
        state.loading = false;
        // Find the regulation in the regulations array and update it
        const index = state.regulations.findIndex(reg => reg.id === action.payload.id);
        if (index !== -1) {
          state.regulations[index] = action.payload;
        } else {
          // If not found, add it to the array
          state.regulations.push(action.payload);
        }
        state.error = null;
      })
      .addCase(fetchRegulation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch segments
      .addCase(fetchSegments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSegments.fulfilled, (state, action: PayloadAction<RegulationSegment[]>) => {
        state.loading = false;
        state.segments = action.payload;
        state.error = null;
      })
      .addCase(fetchSegments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Fetch interpretations
      .addCase(fetchInterpretations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        fetchInterpretations.fulfilled,
        (state, action: PayloadAction<RegulationInterpretation[]>) => {
          state.loading = false;
          state.interpretations = action.payload;
          state.error = null;
        }
      )
      .addCase(fetchInterpretations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Upload document
      .addCase(uploadDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadDocument.fulfilled, (state, action: PayloadAction<RegulationDocument>) => {
        state.loading = false;
        state.documents.push(action.payload);
        state.currentDocument = action.payload;
        state.error = null;
      })
      .addCase(uploadDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Process document
      .addCase(processDocument.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(processDocument.fulfilled, (state) => {
        state.loading = false;
        state.error = null;
      })
      .addCase(processDocument.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Create interpretation
      .addCase(createInterpretation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        createInterpretation.fulfilled,
        (state, action: PayloadAction<RegulationInterpretation>) => {
          state.loading = false;
          state.interpretations.push(action.payload);
          state.error = null;
        }
      )
      .addCase(createInterpretation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Generate AI interpretation
      .addCase(generateAIInterpretation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        generateAIInterpretation.fulfilled,
        (state, action: PayloadAction<RegulationInterpretation>) => {
          state.loading = false;
          state.interpretations.push(action.payload);
          state.error = null;
        }
      )
      .addCase(generateAIInterpretation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Delete regulation
      .addCase(deleteRegulation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteRegulation.fulfilled, (state, action: PayloadAction<number>) => {
        state.loading = false;
        state.documents = state.documents.filter(doc => doc.id !== action.payload);
        state.regulations = state.regulations.filter(reg => reg.id !== action.payload);
        if (state.currentDocument && state.currentDocument.id === action.payload) {
          state.currentDocument = null;
        }
        state.error = null;
      })
      .addCase(deleteRegulation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Create regulation
      .addCase(createRegulation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createRegulation.fulfilled, (state, action: PayloadAction<Regulation>) => {
        state.loading = false;
        state.regulations.push(action.payload);
        state.error = null;
      })
      .addCase(createRegulation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })

      // Update regulation
      .addCase(updateRegulation.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateRegulation.fulfilled, (state, action: PayloadAction<Regulation>) => {
        state.loading = false;
        const index = state.regulations.findIndex(reg => reg.id === action.payload.id);
        if (index !== -1) {
          state.regulations[index] = action.payload;
        }
        state.error = null;
      })
      .addCase(updateRegulation.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setCurrentDocument } = regulationsSlice.actions;

export default regulationsSlice.reducer;
