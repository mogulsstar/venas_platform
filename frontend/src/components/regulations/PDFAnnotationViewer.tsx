import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Document, Page, pdfjs } from 'react-pdf';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tooltip,
  Slider,
  Stack,
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  ChevronLeft as PrevPageIcon,
  ChevronRight as NextPageIcon,
  TextFields as TextSelectIcon,
  Crop as CropIcon,
  Save as SaveIcon,
  Translate as TranslateIcon,
  Title as TitleIcon,
  TableChart as TableChartIcon,
  Image as ImageIcon,
  FormatListBulleted as FormatListBulletedIcon,
  Category as CategoryIcon
} from '@mui/icons-material';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

// Types for annotations
interface Annotation {
  id: string;
  type: 'text' | 'area' | 'heading' | 'table' | 'figure' | 'list';
  page: number;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  content: string;
  title?: string;
  language?: string;
  category?: string;
  section_number?: string;
  metadata?: Record<string, any>;
}

interface PDFAnnotationViewerProps {
  pdfUrl: string;
  initialAnnotations?: Annotation[];
  onSaveAnnotations?: (annotations: Annotation[]) => void;
  readOnly?: boolean;
}

const PDFAnnotationViewer: React.FC<PDFAnnotationViewerProps> = ({
  pdfUrl,
  initialAnnotations = [],
  onSaveAnnotations,
  readOnly = false
}) => {
  const { t } = useTranslation();
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // State
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.5);
  const [annotations, setAnnotations] = useState<Annotation[]>(initialAnnotations);
  const [currentAnnotation, setCurrentAnnotation] = useState<Annotation | null>(null);
  const [isDrawing, setIsDrawing] = useState<boolean>(false);
  const [startPos, setStartPos] = useState<{ x: number; y: number } | null>(null);
  const [currentPos, setCurrentPos] = useState<{ x: number; y: number } | null>(null);
  const [annotationMode, setAnnotationMode] = useState<'text' | 'area' | 'heading' | 'table' | 'figure' | 'list' | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [openDialog, setOpenDialog] = useState<boolean>(false);
  const [selectedAnnotation, setSelectedAnnotation] = useState<Annotation | null>(null);

  // Handle document load success
  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setIsLoading(false);
  };

  // Navigation functions
  const goToPrevPage = () => {
    setPageNumber(prevPageNumber => Math.max(prevPageNumber - 1, 1));
  };

  const goToNextPage = () => {
    setPageNumber(prevPageNumber => Math.min(prevPageNumber + 1, numPages || 1));
  };

  // Zoom functions
  const zoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.2, 3));
  };

  const zoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.2, 0.5));
  };

  // Annotation functions
  const startAnnotation = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (readOnly || !annotationMode) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / scale;
    const y = (e.clientY - rect.top) / scale;

    setIsDrawing(true);
    setStartPos({ x, y });
    setCurrentPos({ x, y });
  };

  const updateAnnotation = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPos) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) / scale;
    const y = (e.clientY - rect.top) / scale;

    setCurrentPos({ x, y });
  };

  const finishAnnotation = () => {
    if (!isDrawing || !startPos || !currentPos) return;

    const newAnnotation: Annotation = {
      id: `annotation-${Date.now()}`,
      type: annotationMode || 'text',
      page: pageNumber,
      position: {
        x: Math.min(startPos.x, currentPos.x),
        y: Math.min(startPos.y, currentPos.y),
        width: Math.abs(currentPos.x - startPos.x),
        height: Math.abs(currentPos.y - startPos.y)
      },
      content: '',
      language: 'en',
      category: 'general',
      metadata: {}
    };

    setAnnotations([...annotations, newAnnotation]);
    setSelectedAnnotation(newAnnotation);
    setOpenDialog(true);

    setIsDrawing(false);
    setStartPos(null);
    setCurrentPos(null);
  };

  const saveAnnotationContent = (content: string, title?: string, language?: string, category?: string, section_number?: string, metadata?: Record<string, any>) => {
    if (!selectedAnnotation) return;

    const updatedAnnotations = annotations.map(annotation =>
      annotation.id === selectedAnnotation.id
        ? { ...annotation, content, title, language, category, section_number, metadata }
        : annotation
    );

    setAnnotations(updatedAnnotations);
    setSelectedAnnotation(null);
    setOpenDialog(false);

    if (onSaveAnnotations) {
      onSaveAnnotations(updatedAnnotations);
    }
  };

  const deleteAnnotation = (id: string) => {
    const updatedAnnotations = annotations.filter(annotation => annotation.id !== id);
    setAnnotations(updatedAnnotations);

    if (onSaveAnnotations) {
      onSaveAnnotations(updatedAnnotations);
    }
  };

  // Render annotations on canvas
  const renderAnnotations = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw current selection if in drawing mode
    if (isDrawing && startPos && currentPos) {
      ctx.strokeStyle = 'rgba(0, 123, 255, 0.8)';
      ctx.lineWidth = 2;
      ctx.strokeRect(
        startPos.x * scale,
        startPos.y * scale,
        (currentPos.x - startPos.x) * scale,
        (currentPos.y - startPos.y) * scale
      );
    }

    // Draw existing annotations for current page
    annotations
      .filter(annotation => annotation.page === pageNumber)
      .forEach(annotation => {
        const { x, y, width, height } = annotation.position;

        // Different colors for different annotation types
        let strokeColor = 'rgba(0, 0, 0, 0.8)';
        switch (annotation.type) {
          case 'text':
            strokeColor = 'rgba(76, 175, 80, 0.8)'; // Green
            break;
          case 'area':
            strokeColor = 'rgba(255, 152, 0, 0.8)'; // Orange
            break;
          case 'heading':
            strokeColor = 'rgba(33, 150, 243, 0.8)'; // Blue
            break;
          case 'table':
            strokeColor = 'rgba(156, 39, 176, 0.8)'; // Purple
            break;
          case 'figure':
            strokeColor = 'rgba(233, 30, 99, 0.8)'; // Pink
            break;
          case 'list':
            strokeColor = 'rgba(0, 188, 212, 0.8)'; // Cyan
            break;
        }
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(
          x * scale,
          y * scale,
          width * scale,
          height * scale
        );

        // Add label
        if (annotation.title) {
          // Different fill colors for different annotation types
          let fillColor = 'rgba(0, 0, 0, 0.9)';
          switch (annotation.type) {
            case 'text':
              fillColor = 'rgba(76, 175, 80, 0.9)'; // Green
              break;
            case 'area':
              fillColor = 'rgba(255, 152, 0, 0.9)'; // Orange
              break;
            case 'heading':
              fillColor = 'rgba(33, 150, 243, 0.9)'; // Blue
              break;
            case 'table':
              fillColor = 'rgba(156, 39, 176, 0.9)'; // Purple
              break;
            case 'figure':
              fillColor = 'rgba(233, 30, 99, 0.9)'; // Pink
              break;
            case 'list':
              fillColor = 'rgba(0, 188, 212, 0.9)'; // Cyan
              break;
          }
          ctx.fillStyle = fillColor;
          ctx.fillRect(
            x * scale,
            (y - 20) * scale,
            Math.min(width, annotation.title.length * 8) * scale,
            20 * scale
          );

          ctx.fillStyle = 'white';
          ctx.font = `${12 * scale}px Arial`;
          ctx.fillText(
            annotation.title,
            (x + 5) * scale,
            (y - 5) * scale
          );
        }
      });
  };

  // Effect to render annotations when needed
  useEffect(() => {
    renderAnnotations();
  }, [annotations, pageNumber, scale, isDrawing, startPos, currentPos]);

  // Render PDF page with canvas overlay
  const renderPage = (
    <div style={{ position: 'relative' }}>
      <Document
        file={pdfUrl}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={<CircularProgress />}
      >
        <Page
          pageNumber={pageNumber}
          scale={scale}
          renderTextLayer={false}
          renderAnnotationLayer={false}
          canvasRef={canvasRef}
          onRenderSuccess={renderAnnotations}
        />
      </Document>

      {!readOnly && (
        <canvas
          ref={canvasRef}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            pointerEvents: annotationMode ? 'auto' : 'none',
            cursor: annotationMode ? 'crosshair' : 'default'
          }}
          onMouseDown={startAnnotation}
          onMouseMove={updateAnnotation}
          onMouseUp={finishAnnotation}
          onMouseLeave={finishAnnotation}
        />
      )}
    </div>
  );

  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%', overflow: 'auto' }}>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {t('regulations.pdfViewer')}
          </Typography>

          <Stack direction="row" spacing={1} alignItems="center">
            {!readOnly && (
              <>
                <Tooltip title={t('regulations.selectTextArea')}>
                  <IconButton
                    color={annotationMode === 'text' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'text' ? null : 'text')}
                  >
                    <TextSelectIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('regulations.selectArea')}>
                  <IconButton
                    color={annotationMode === 'area' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'area' ? null : 'area')}
                  >
                    <CropIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('regulations.selectHeading')}>
                  <IconButton
                    color={annotationMode === 'heading' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'heading' ? null : 'heading')}
                  >
                    <TitleIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('regulations.selectTable')}>
                  <IconButton
                    color={annotationMode === 'table' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'table' ? null : 'table')}
                  >
                    <TableChartIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('regulations.selectFigure')}>
                  <IconButton
                    color={annotationMode === 'figure' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'figure' ? null : 'figure')}
                  >
                    <ImageIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('regulations.selectList')}>
                  <IconButton
                    color={annotationMode === 'list' ? 'primary' : 'default'}
                    onClick={() => setAnnotationMode(annotationMode === 'list' ? null : 'list')}
                  >
                    <FormatListBulletedIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title={t('common.save')}>
                  <IconButton
                    onClick={() => onSaveAnnotations && onSaveAnnotations(annotations)}
                  >
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              </>
            )}

            <Tooltip title={t('common.zoomOut')}>
              <IconButton onClick={zoomOut}>
                <ZoomOutIcon />
              </IconButton>
            </Tooltip>

            <Box sx={{ width: 100 }}>
              <Slider
                value={scale}
                min={0.5}
                max={3}
                step={0.1}
                onChange={(_, value) => setScale(value as number)}
                aria-labelledby="zoom-slider"
              />
            </Box>

            <Tooltip title={t('common.zoomIn')}>
              <IconButton onClick={zoomIn}>
                <ZoomInIcon />
              </IconButton>
            </Tooltip>
          </Stack>

          <Stack direction="row" spacing={1} alignItems="center">
            <Tooltip title={t('common.previousPage')}>
              <span>
                <IconButton
                  onClick={goToPrevPage}
                  disabled={pageNumber <= 1}
                >
                  <PrevPageIcon />
                </IconButton>
              </span>
            </Tooltip>

            <Typography>
              {pageNumber} / {numPages || '?'}
            </Typography>

            <Tooltip title={t('common.nextPage')}>
              <span>
                <IconButton
                  onClick={goToNextPage}
                  disabled={pageNumber >= (numPages || 1)}
                >
                  <NextPageIcon />
                </IconButton>
              </span>
            </Tooltip>
          </Stack>
        </Stack>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'center' }}>
        {isLoading ? (
          <CircularProgress />
        ) : (
          renderPage
        )}
      </Box>

      {/* Annotation Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>
          {selectedAnnotation?.type === 'text'
            ? t('regulations.addTextAnnotation')
            : t('regulations.addAreaAnnotation')}
        </DialogTitle>

        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={t('common.title')}
            fullWidth
            variant="outlined"
            value={selectedAnnotation?.title || ''}
            onChange={(e) => setSelectedAnnotation(prev =>
              prev ? { ...prev, title: e.target.value } : null
            )}
            sx={{ mb: 2 }}
          />

          <TextField
            margin="dense"
            label={t('common.sectionNumber')}
            fullWidth
            variant="outlined"
            value={selectedAnnotation?.section_number || ''}
            onChange={(e) => setSelectedAnnotation(prev =>
              prev ? { ...prev, section_number: e.target.value } : null
            )}
            sx={{ mb: 2 }}
          />

          <TextField
            margin="dense"
            label={t('common.content')}
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={selectedAnnotation?.content || ''}
            onChange={(e) => setSelectedAnnotation(prev =>
              prev ? { ...prev, content: e.target.value } : null
            )}
            sx={{ mb: 2 }}
          />

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl fullWidth variant="outlined">
              <InputLabel>{t('common.language')}</InputLabel>
              <Select
                value={selectedAnnotation?.language || 'en'}
                onChange={(e) => setSelectedAnnotation(prev =>
                  prev ? { ...prev, language: e.target.value as string } : null
                )}
                label={t('common.language')}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="zh-hans">中文 (Chinese)</MenuItem>
                <MenuItem value="de">Deutsch (German)</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth variant="outlined">
              <InputLabel>{t('regulations.category')}</InputLabel>
              <Select
                value={selectedAnnotation?.category || 'general'}
                onChange={(e) => setSelectedAnnotation(prev =>
                  prev ? { ...prev, category: e.target.value as string } : null
                )}
                label={t('regulations.category')}
              >
                <MenuItem value="general">{t('regulations.categories.general')}</MenuItem>
                <MenuItem value="definition">{t('regulations.categories.definition')}</MenuItem>
                <MenuItem value="requirement">{t('regulations.categories.requirement')}</MenuItem>
                <MenuItem value="procedure">{t('regulations.categories.procedure')}</MenuItem>
                <MenuItem value="informative">{t('regulations.categories.informative')}</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() => {
              if (selectedAnnotation) {
                deleteAnnotation(selectedAnnotation.id);
              }
              setOpenDialog(false);
            }}
            color="error"
          >
            {t('common.delete')}
          </Button>

          <Button onClick={() => setOpenDialog(false)} color="primary">
            {t('common.cancel')}
          </Button>

          <Button
            onClick={() => {
              if (selectedAnnotation) {
                saveAnnotationContent(
                  selectedAnnotation.content,
                  selectedAnnotation.title,
                  selectedAnnotation.language,
                  selectedAnnotation.category,
                  selectedAnnotation.section_number,
                  selectedAnnotation.metadata
                );
              }
            }}
            color="primary"
          >
            {t('common.save')}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PDFAnnotationViewer;
