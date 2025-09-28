import React, { useEffect, useRef } from 'react';
import vegaEmbed from 'vega-embed';
import { Box, CircularProgress, Alert } from '@mui/material';

const VegaLiteChart = ({ spec, width = 600, height = 400, title }) => {
  const chartRef = useRef(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  useEffect(() => {
    if (spec && chartRef.current) {
      renderChart();
    }
  }, [spec]);

  const renderChart = async () => {
    if (!spec || !chartRef.current) return;

    setLoading(true);
    setError(null);

    try {
      // Clear previous chart
      chartRef.current.innerHTML = '';

      // Ensure spec has proper dimensions
      const chartSpec = {
        ...spec,
        width: width,
        height: height,
        autosize: { type: 'fit', contains: 'padding' }
      };

      // Embed the chart using vega-embed
      await vegaEmbed(chartRef.current, chartSpec, {
        actions: {
          export: true,
          source: true,
          compiled: false,
          editor: false
        },
        renderer: 'svg'
      });

      // Add title if provided
      if (title && chartRef.current) {
        const titleElement = document.createElement('h3');
        titleElement.textContent = title;
        titleElement.style.textAlign = 'center';
        titleElement.style.marginBottom = '10px';
        titleElement.style.fontSize = '16px';
        titleElement.style.fontWeight = 'bold';
        chartRef.current.insertBefore(titleElement, chartRef.current.firstChild);
      }

    } catch (err) {
      console.error('Error rendering chart:', err);
      setError('Failed to render chart');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

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
    <Box>
      <div ref={chartRef} />
    </Box>
  );
};

export default VegaLiteChart;