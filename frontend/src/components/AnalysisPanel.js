import React, { useState } from 'react';
import {
  Grid,
  Button,
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Paper,
  Alert,
  Divider,
  Chip
} from '@mui/material';
import {
  Assessment,
  Timeline,
  People,
  Speed,
  GetApp
} from '@mui/icons-material';
import VegaLiteChart from './VegaLiteChart';

const AnalysisPanel = ({
  selectedDataset,
  chartTypes,
  analysisData,
  loading,
  onAnalysis,
  onChartRequest
}) => {
  const [customQuery, setCustomQuery] = useState('');

  const handleQuickAnalysis = (query) => {
    onAnalysis(query);
  };

  const handleChartRequest = (chartType) => {
    onChartRequest(chartType);
  };

  const handleCustomQuery = () => {
    if (customQuery.trim()) {
      onAnalysis(customQuery);
    }
  };

  const getAvailableChartTypes = () => {
    // Filter chart types based on dataset
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

  const quickQueries = [
    { label: 'Summary', query: 'summary' },
    { label: 'Bottlenecks', query: 'top bottlenecks' },
    { label: 'Team Performance', query: 'team performance' },
    { label: 'App Usage', query: 'app usage' },
    { label: 'Recommendations', query: 'recommendations for managers' }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Analysis Dashboard
      </Typography>
      
      {selectedDataset && (
        <>
          {/* Quick Analysis Buttons */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Analysis
            </Typography>
            <Grid container spacing={2}>
              {quickQueries.map((query) => (
                <Grid item key={query.query}>
                  <Button
                    variant="outlined"
                    onClick={() => handleQuickAnalysis(query.query)}
                    disabled={loading}
                    startIcon={<Assessment />}
                  >
                    {query.label}
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Paper>

          {/* Custom Query */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Custom Query
            </Typography>
            <Box display="flex" gap={2} alignItems="center">
              <TextField
                fullWidth
                label="Enter your analysis query"
                value={customQuery}
                onChange={(e) => setCustomQuery(e.target.value)}
                placeholder="e.g., 'summary', 'top bottlenecks', 'team performance'"
                disabled={loading}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleCustomQuery();
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={handleCustomQuery}
                disabled={loading || !customQuery.trim()}
              >
                Analyze
              </Button>
            </Box>
          </Paper>

          {/* Chart Types */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Available Charts
            </Typography>
            <Grid container spacing={2}>
              {getAvailableChartTypes().map((chartType) => (
                <Grid item key={chartType.id}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleChartRequest(chartType.id)}
                    disabled={loading}
                    startIcon={chartType.icon}
                  >
                    {chartType.label}
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Paper>

          <Divider sx={{ my: 3 }} />

          {/* Analysis Results */}
          {analysisData && (
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Analysis Results
              </Typography>
              
              {/* Text Analysis */}
              {analysisData.text && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Analysis Summary
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                      {analysisData.text}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {/* Chart Visualization */}
              {analysisData.vega_lite_spec && (
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Visualization
                    </Typography>
                    <VegaLiteChart
                      spec={analysisData.vega_lite_spec}
                      width={800}
                      height={500}
                    />
                  </CardContent>
                </Card>
              )}

              {/* Additional Info */}
              {analysisData.additional_info && (
                <Card sx={{ mt: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Additional Information
                    </Typography>
                    <Box display="flex" flexWrap="wrap" gap={1}>
                      {Object.entries(analysisData.additional_info).map(([key, value]) => (
                        <Chip
                          key={key}
                          label={`${key}: ${value}`}
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Paper>
          )}

          {/* Loading State */}
          {loading && (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
              <Typography variant="h6">
                Analyzing data...
              </Typography>
            </Box>
          )}
        </>
      )}

      {!selectedDataset && (
        <Alert severity="info">
          Please select a dataset to begin analysis
        </Alert>
      )}
    </Box>
  );
};

export default AnalysisPanel;
