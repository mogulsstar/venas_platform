import React, { useRef, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as d3 from 'd3';
import { 
  Box, 
  Paper, 
  Typography, 
  IconButton, 
  Tooltip, 
  Stack,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  TextField,
  Slider,
  Autocomplete
} from '@mui/material';
import {
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon,
  FilterList as FilterIcon,
  Search as SearchIcon
} from '@mui/icons-material';

// Types
interface RegulationNode {
  id: string;
  name: string;
  country: string;
  region?: string;
  category: string;
  weight: number;
  similarity?: number;
}

interface RegulationLink {
  source: string;
  target: string;
  value: number;
  type: 'similar' | 'reference' | 'dependency';
}

interface DataMappingMatrixProps {
  nodes: RegulationNode[];
  links: RegulationLink[];
  isLoading?: boolean;
  onNodeClick?: (node: RegulationNode) => void;
  onLinkClick?: (link: RegulationLink) => void;
}

const DataMappingMatrix: React.FC<DataMappingMatrixProps> = ({
  nodes,
  links,
  isLoading = false,
  onNodeClick,
  onLinkClick
}) => {
  const { t } = useTranslation();
  const svgRef = useRef<SVGSVGElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  
  // State
  const [scale, setScale] = useState<number>(1);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.5);
  const [filteredNodes, setFilteredNodes] = useState<RegulationNode[]>(nodes);
  const [filteredLinks, setFilteredLinks] = useState<RegulationLink[]>(links);
  
  // Get unique countries and categories for filters
  const countries = Array.from(new Set(nodes.map(node => node.country)));
  const categories = Array.from(new Set(nodes.map(node => node.category)));
  
  // Filter nodes and links based on selected filters
  useEffect(() => {
    let filtered = [...nodes];
    
    // Apply country filter
    if (selectedCountries.length > 0) {
      filtered = filtered.filter(node => selectedCountries.includes(node.country));
    }
    
    // Apply category filter
    if (selectedCategories.length > 0) {
      filtered = filtered.filter(node => selectedCategories.includes(node.category));
    }
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(node => 
        node.name.toLowerCase().includes(term) || 
        node.id.toLowerCase().includes(term)
      );
    }
    
    setFilteredNodes(filtered);
    
    // Filter links to only include connections between filtered nodes
    const filteredNodeIds = filtered.map(node => node.id);
    const newFilteredLinks = links.filter(link => 
      filteredNodeIds.includes(link.source as string) && 
      filteredNodeIds.includes(link.target as string) &&
      link.value >= similarityThreshold
    );
    
    setFilteredLinks(newFilteredLinks);
  }, [nodes, links, selectedCountries, selectedCategories, searchTerm, similarityThreshold]);
  
  // Render the matrix visualization using D3
  useEffect(() => {
    if (isLoading || !svgRef.current || filteredNodes.length === 0) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    
    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    const padding = 100;
    
    // Create scales for node positions
    const xScale = d3.scaleBand()
      .domain(filteredNodes.map(d => d.id))
      .range([padding, width - padding])
      .padding(0.1);
    
    const yScale = d3.scaleBand()
      .domain(filteredNodes.map(d => d.id))
      .range([padding, height - padding])
      .padding(0.1);
    
    // Create color scale for links
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['similar', 'reference', 'dependency'])
      .range(['#1976d2', '#ff9800', '#4caf50']);
    
    // Create size scale for nodes
    const sizeScale = d3.scaleLinear()
      .domain([0, d3.max(filteredNodes, d => d.weight) || 1])
      .range([5, 15]);
    
    // Create a group for the visualization
    const g = svg.append('g')
      .attr('transform', `scale(${scale})`);
    
    // Add links (matrix cells)
    g.selectAll('.matrix-cell')
      .data(filteredLinks)
      .enter()
      .append('rect')
      .attr('class', 'matrix-cell')
      .attr('x', d => xScale(d.source as string) || 0)
      .attr('y', d => yScale(d.target as string) || 0)
      .attr('width', xScale.bandwidth())
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.type))
      .attr('opacity', d => d.value)
      .attr('stroke', '#fff')
      .attr('stroke-width', 1)
      .on('click', (event, d) => {
        if (onLinkClick) onLinkClick(d);
      })
      .append('title')
      .text(d => `${d.source} → ${d.target}: ${d.value.toFixed(2)}`);
    
    // Add x-axis labels (rotated)
    g.selectAll('.x-label')
      .data(filteredNodes)
      .enter()
      .append('text')
      .attr('class', 'x-label')
      .attr('x', d => (xScale(d.id) || 0) + xScale.bandwidth() / 2)
      .attr('y', padding - 10)
      .attr('text-anchor', 'end')
      .attr('transform', d => `rotate(-45, ${(xScale(d.id) || 0) + xScale.bandwidth() / 2}, ${padding - 10})`)
      .style('font-size', '10px')
      .text(d => d.name.length > 20 ? d.name.substring(0, 20) + '...' : d.name);
    
    // Add y-axis labels
    g.selectAll('.y-label')
      .data(filteredNodes)
      .enter()
      .append('text')
      .attr('class', 'y-label')
      .attr('x', padding - 10)
      .attr('y', d => (yScale(d.id) || 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '10px')
      .text(d => d.name.length > 20 ? d.name.substring(0, 20) + '...' : d.name);
    
    // Add nodes on the diagonal
    g.selectAll('.node')
      .data(filteredNodes)
      .enter()
      .append('circle')
      .attr('class', 'node')
      .attr('cx', d => (xScale(d.id) || 0) + xScale.bandwidth() / 2)
      .attr('cy', d => (yScale(d.id) || 0) + yScale.bandwidth() / 2)
      .attr('r', d => sizeScale(d.weight))
      .attr('fill', d => {
        // Color by country
        const countryHash = d.country.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return d3.interpolateRainbow(countryHash / 1000);
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 1)
      .on('click', (event, d) => {
        if (onNodeClick) onNodeClick(d);
      })
      .append('title')
      .text(d => `${d.name} (${d.country}): ${d.weight}`);
    
    // Add country legend
    const legendGroup = svg.append('g')
      .attr('transform', `translate(${width - 150}, 20)`);
    
    legendGroup.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(t('regulations.countries'));
    
    const countryLegend = legendGroup.selectAll('.country-legend')
      .data(countries)
      .enter()
      .append('g')
      .attr('class', 'country-legend')
      .attr('transform', (d, i) => `translate(0, ${i * 20 + 20})`);
    
    countryLegend.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', d => {
        const countryHash = d.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return d3.interpolateRainbow(countryHash / 1000);
      });
    
    countryLegend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .style('font-size', '10px')
      .text(d => d);
    
    // Add link type legend
    const linkLegendGroup = svg.append('g')
      .attr('transform', `translate(${width - 150}, ${countries.length * 20 + 40})`);
    
    linkLegendGroup.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text(t('regulations.linkTypes'));
    
    const linkTypes = ['similar', 'reference', 'dependency'];
    const linkLegend = linkLegendGroup.selectAll('.link-legend')
      .data(linkTypes)
      .enter()
      .append('g')
      .attr('class', 'link-legend')
      .attr('transform', (d, i) => `translate(0, ${i * 20 + 20})`);
    
    linkLegend.append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', d => colorScale(d));
    
    linkLegend.append('text')
      .attr('x', 20)
      .attr('y', 12)
      .style('font-size', '10px')
      .text(d => t(`regulations.linkType.${d}`));
    
  }, [filteredNodes, filteredLinks, scale, isLoading, t, onNodeClick, onLinkClick]);
  
  // Zoom functions
  const zoomIn = () => {
    setScale(prevScale => Math.min(prevScale + 0.2, 3));
  };

  const zoomOut = () => {
    setScale(prevScale => Math.max(prevScale - 0.2, 0.5));
  };
  
  return (
    <Box ref={containerRef} sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="h6">
            {t('regulations.dataMapping')}
          </Typography>
          
          <Stack direction="row" spacing={1} alignItems="center">
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
            
            <Tooltip title={t('common.refresh')}>
              <IconButton>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
          <TextField
            label={t('common.search')}
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon fontSize="small" sx={{ mr: 1 }} />,
            }}
            sx={{ width: 200 }}
          />
          
          <Autocomplete
            multiple
            options={countries}
            value={selectedCountries}
            onChange={(_, newValue) => setSelectedCountries(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label={t('regulations.countries')}
                variant="outlined"
                size="small"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  size="small"
                  {...getTagProps({ index })}
                />
              ))
            }
            sx={{ width: 250 }}
          />
          
          <Autocomplete
            multiple
            options={categories}
            value={selectedCategories}
            onChange={(_, newValue) => setSelectedCategories(newValue)}
            renderInput={(params) => (
              <TextField
                {...params}
                label={t('regulations.categories')}
                variant="outlined"
                size="small"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  size="small"
                  {...getTagProps({ index })}
                />
              ))
            }
            sx={{ width: 250 }}
          />
          
          <Box sx={{ width: 200 }}>
            <Typography variant="body2" gutterBottom>
              {t('regulations.similarityThreshold')}: {similarityThreshold.toFixed(2)}
            </Typography>
            <Slider
              value={similarityThreshold}
              min={0}
              max={1}
              step={0.05}
              onChange={(_, value) => setSimilarityThreshold(value as number)}
              aria-labelledby="similarity-threshold-slider"
            />
          </Box>
        </Stack>
      </Paper>
      
      <Box sx={{ flexGrow: 1, position: 'relative', minHeight: 500 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : filteredNodes.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body1" color="text.secondary">
              {t('common.noResults')}
            </Typography>
          </Box>
        ) : (
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            style={{ minHeight: 500 }}
          />
        )}
      </Box>
    </Box>
  );
};

export default DataMappingMatrix;
