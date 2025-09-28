import React from 'react';
import { Box, Alert, Typography } from '@mui/material';

const SimpleChart = ({ spec, title }) => {
  if (!spec) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <Alert severity="info">
          No chart data available
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 2 }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <Typography variant="body2" color="text.secondary">
        Chart visualization will be available once the Vega-Lite dependencies are properly configured.
      </Typography>
      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
        <Typography variant="caption" display="block">
          Chart Spec: {JSON.stringify(spec, null, 2).substring(0, 200)}...
        </Typography>
      </Box>
    </Box>
  );
};

export default SimpleChart;
