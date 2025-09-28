import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Typography,
  Chip,
  Box
} from '@mui/material';
import { CheckCircle, Cancel } from '@mui/icons-material';

const DatasetSelector = ({ datasets, selectedDataset, onDatasetChange }) => {
  const handleChange = (event) => {
    onDatasetChange(event.target.value);
  };

  return (
    <Box>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select Dataset</InputLabel>
        <Select
          value={selectedDataset}
          label="Select Dataset"
          onChange={handleChange}
        >
          {datasets.map((dataset) => (
            <MenuItem key={dataset.id} value={dataset.id}>
              <Box display="flex" alignItems="center" width="100%">
                <Box flexGrow={1}>
                  <Typography variant="subtitle1">
                    {dataset.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {dataset.description}
                  </Typography>
                </Box>
                <Chip
                  icon={dataset.available ? <CheckCircle /> : <Cancel />}
                  label={dataset.available ? 'Available' : 'Unavailable'}
                  color={dataset.available ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {selectedDataset && (
        <Card variant="outlined">
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dataset Information
            </Typography>
            {datasets
              .filter(d => d.id === selectedDataset)
              .map(dataset => (
                <Box key={dataset.id}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Name:</strong> {dataset.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Description:</strong> {dataset.description}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Status:</strong> 
                    <Chip
                      icon={dataset.available ? <CheckCircle /> : <Cancel />}
                      label={dataset.available ? 'Available' : 'Unavailable'}
                      color={dataset.available ? 'success' : 'error'}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                </Box>
              ))
            }
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DatasetSelector;
