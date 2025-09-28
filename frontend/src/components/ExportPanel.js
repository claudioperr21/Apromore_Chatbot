import React, { useState } from 'react';
import {
  Grid,
  Button,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Paper,
  Alert,
  Divider,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  PictureAsPdf,
  GetApp,
  Download,
  FileDownload,
  Assessment,
  Timeline,
  People,
  Speed
} from '@mui/icons-material';

const ExportPanel = ({
  selectedDataset,
  chartTypes,
  loading,
  onExportPDF
}) => {
  const [selectedCharts, setSelectedCharts] = useState(['summary', 'bottlenecks']);
  const [customTitle, setCustomTitle] = useState('');
  const [exportFormat, setExportFormat] = useState('pdf');

  const getAvailableChartTypes = () => {
    if (selectedDataset === 'salesforce') {
      return chartTypes.filter(ct => 
        ['summary', 'bottlenecks', 'team_performance', 'app_usage', 'time_analysis'].includes(ct.id)
      );
    } else if (selectedDataset === 'amadeus') {
      return chartTypes.filter(ct => 
        ['summary', 'bottlenecks', 'process_analysis', 'user_efficiency'].includes(ct.id)
      );
    }
    return chartTypes;
  };

  const handleChartToggle = (chartId) => {
    setSelectedCharts(prev => {
      if (prev.includes(chartId)) {
        return prev.filter(id => id !== chartId);
      } else {
        return [...prev, chartId];
      }
    });
  };

  const handleSelectAll = () => {
    const availableCharts = getAvailableChartTypes().map(ct => ct.id);
    setSelectedCharts(availableCharts);
  };

  const handleSelectNone = () => {
    setSelectedCharts([]);
  };

  const handleExport = () => {
    const title = customTitle || `Task Mining Analysis - ${selectedDataset?.charAt(0).toUpperCase() + selectedDataset?.slice(1)}`;
    
    if (exportFormat === 'pdf') {
      onExportPDF(selectedCharts, title);
    }
  };

  const getChartIcon = (chartId) => {
    const chartType = chartTypes.find(ct => ct.id === chartId);
    return chartType?.icon || <Assessment />;
  };

  const getChartLabel = (chartId) => {
    const chartType = chartTypes.find(ct => ct.id === chartId);
    return chartType?.label || chartId;
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Export Analysis
      </Typography>

      {selectedDataset && (
        <>
          {/* Export Settings */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Export Settings
            </Typography>
            
            <Grid container spacing={3}>
              {/* Export Format */}
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Export Format</InputLabel>
                  <Select
                    value={exportFormat}
                    label="Export Format"
                    onChange={(e) => setExportFormat(e.target.value)}
                  >
                    <MenuItem value="pdf">
                      <Box display="flex" alignItems="center">
                        <PictureAsPdf sx={{ mr: 1 }} />
                        PDF Document
                      </Box>
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* Custom Title */}
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Custom Title (Optional)"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  placeholder={`Task Mining Analysis - ${selectedDataset?.charAt(0).toUpperCase() + selectedDataset?.slice(1)}`}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Chart Selection */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                Select Charts to Include
              </Typography>
              <Box>
                <Button size="small" onClick={handleSelectAll} sx={{ mr: 1 }}>
                  Select All
                </Button>
                <Button size="small" onClick={handleSelectNone}>
                  Select None
                </Button>
              </Box>
            </Box>

            <Grid container spacing={2}>
              {getAvailableChartTypes().map((chartType) => (
                <Grid item xs={12} sm={6} md={4} key={chartType.id}>
                  <Card 
                    variant={selectedCharts.includes(chartType.id) ? "elevation" : "outlined"}
                    sx={{ 
                      cursor: 'pointer',
                      border: selectedCharts.includes(chartType.id) ? 2 : 1,
                      borderColor: selectedCharts.includes(chartType.id) ? 'primary.main' : 'divider'
                    }}
                    onClick={() => handleChartToggle(chartType.id)}
                  >
                    <CardContent sx={{ p: 2 }}>
                      <Box display="flex" alignItems="center" mb={1}>
                        {chartType.icon}
                        <Typography variant="subtitle1" sx={{ ml: 1, flexGrow: 1 }}>
                          {chartType.label}
                        </Typography>
                        <Checkbox
                          checked={selectedCharts.includes(chartType.id)}
                          onChange={() => handleChartToggle(chartType.id)}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>

            {selectedCharts.length === 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                Please select at least one chart to export
              </Alert>
            )}
          </Paper>

          {/* Export Preview */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Export Preview
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <FileDownload />
                </ListItemIcon>
                <ListItemText
                  primary="Export Format"
                  secondary={exportFormat.toUpperCase()}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <Assessment />
                </ListItemIcon>
                <ListItemText
                  primary="Document Title"
                  secondary={customTitle || `Task Mining Analysis - ${selectedDataset?.charAt(0).toUpperCase() + selectedDataset?.slice(1)}`}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <Timeline />
                </ListItemIcon>
                <ListItemText
                  primary="Selected Charts"
                  secondary={`${selectedCharts.length} chart(s) selected`}
                />
              </ListItem>
            </List>

            {selectedCharts.length > 0 && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Charts to be included:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {selectedCharts.map(chartId => (
                    <Chip
                      key={chartId}
                      icon={getChartIcon(chartId)}
                      label={getChartLabel(chartId)}
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Paper>

          {/* Export Button */}
          <Box display="flex" justifyContent="center">
            <Button
              variant="contained"
              size="large"
              onClick={handleExport}
              disabled={loading || selectedCharts.length === 0}
              startIcon={<PictureAsPdf />}
              sx={{ px: 4, py: 1.5 }}
            >
              {loading ? 'Generating PDF...' : 'Export to PDF'}
            </Button>
          </Box>
        </>
      )}

      {!selectedDataset && (
        <Alert severity="info">
          Please select a dataset to begin export
        </Alert>
      )}
    </Box>
  );
};

export default ExportPanel;
