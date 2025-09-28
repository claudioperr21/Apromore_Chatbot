import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Button,
  TextField,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar,
  Badge
} from '@mui/material';
import {
  Assessment,
  Chat,
  Timeline,
  People,
  Speed,
  GetApp,
  PictureAsPdf,
  Send,
  SmartToy,
  Person,
  Refresh,
  Download,
  Analytics,
  Insights
} from '@mui/icons-material';
import VegaLiteChart from './components/VegaLiteChart';
import SimpleChart from './components/SimpleChart';
import { fetchChat, fetchAnalysis, fetchChart, exportPDF, exportChatHistory } from './services/api';

function App() {
  const [selectedDataset, setSelectedDataset] = useState('salesforce');
  const [chatHistory, setChatHistory] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [analysisData, setAnalysisData] = useState(null);
  const [systemStatus, setSystemStatus] = useState('initializing');
  const [exportDialogOpen, setExportDialogOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  useEffect(() => {
    initializeSystem();
  }, []);

  const initializeSystem = async () => {
    try {
      setSystemStatus('initializing');
      // Test system connection
      const response = await fetch('/api/health');
      if (response.ok) {
        setSystemStatus('ready');
        // Add welcome message
        setChatHistory([{
          id: Date.now(),
          type: 'ai',
          message: '🎯 Welcome to the Task Mining AI Chat System! I can help you analyze your data. Try asking me questions like:\n\n• "who is the most active user?"\n• "what are some bottlenecks?"\n• "how many users are there?"\n• "give me insights about the data"\n\nYou can also switch between Salesforce and Amadeus datasets using the selector above.',
          timestamp: new Date()
        }]);
      } else {
        setSystemStatus('error');
        setError('Backend system not available');
      }
    } catch (err) {
      setSystemStatus('error');
      setError('Failed to connect to backend system');
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: currentMessage,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await fetchChat(selectedDataset, currentMessage);
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: response.data.message,
        chart: response.data.chart,
        chartJson: response.data.chartJson,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (err) {
      setError('Failed to get AI response');
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleDatasetChange = (dataset) => {
    setSelectedDataset(dataset);
    // Add dataset switch message
    const switchMessage = {
      id: Date.now(),
      type: 'system',
      message: `Switched to ${dataset} dataset`,
      timestamp: new Date()
    };
    setChatHistory(prev => [...prev, switchMessage]);
  };

  const handleQuickAction = async (action) => {
    const quickMessages = {
      summary: 'summary',
      bottlenecks: 'top bottlenecks',
      team: 'team performance',
      recommendations: 'recommendations for managers'
    };

    setCurrentMessage(quickMessages[action]);
    await handleSendMessage();
  };

  const handleExportChat = async () => {
    try {
      const response = await exportChatHistory(chatHistory);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `chat_history_${selectedDataset}_${new Date().toISOString().slice(0,10)}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to export chat history');
    }
  };

  const handleAnalysis = async (query) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetchAnalysis(selectedDataset, query);
      setAnalysisData(response.data);
    } catch (err) {
      setError('Failed to fetch analysis');
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    const isSystem = message.type === 'system';
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          px: 2
        }}
      >
        <Box
          sx={{
            maxWidth: '70%',
            display: 'flex',
            flexDirection: isUser ? 'row-reverse' : 'row',
            alignItems: 'flex-start',
            gap: 1
          }}
        >
          {!isUser && !isSystem && (
            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
              <SmartToy />
            </Avatar>
          )}
          {isUser && (
            <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
              <Person />
            </Avatar>
          )}
          <Card
            sx={{
              bgcolor: isUser ? 'primary.main' : isSystem ? 'info.main' : 'grey.100',
              color: isUser ? 'white' : 'text.primary',
              borderRadius: 2,
              px: 2,
              py: 1
            }}
          >
            <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.message}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.7rem' }}>
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    );
  };

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Chat sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Task Mining AI Chat System
          </Typography>
          <Chip
            icon={systemStatus === 'ready' ? <Assessment /> : <CircularProgress size={16} />}
            label={systemStatus === 'ready' ? 'System Ready' : 'Initializing...'}
            color={systemStatus === 'ready' ? 'success' : 'default'}
            variant="outlined"
            sx={{ color: 'white' }}
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Dataset Selector & Quick Actions */}
          <Grid item xs={12} md={3}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Dataset Selection
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant={selectedDataset === 'salesforce' ? 'contained' : 'outlined'}
                  onClick={() => handleDatasetChange('salesforce')}
                  size="small"
                >
                  Salesforce
                </Button>
                <Button
                  variant={selectedDataset === 'amadeus' ? 'contained' : 'outlined'}
                  onClick={() => handleDatasetChange('amadeus')}
                  size="small"
                >
                  Amadeus
                </Button>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Active: {selectedDataset}
              </Typography>
            </Paper>

            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  onClick={() => handleQuickAction('summary')}
                  disabled={loading}
                  size="small"
                >
                  Summary
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Speed />}
                  onClick={() => handleQuickAction('bottlenecks')}
                  disabled={loading}
                  size="small"
                >
                  Bottlenecks
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<People />}
                  onClick={() => handleQuickAction('team')}
                  disabled={loading}
                  size="small"
                >
                  Team Performance
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Insights />}
                  onClick={() => handleQuickAction('recommendations')}
                  disabled={loading}
                  size="small"
                >
                  Recommendations
                </Button>
              </Box>
            </Paper>
          </Grid>

          {/* Main Chat Interface */}
          <Grid item xs={12} md={9}>
            <Paper sx={{ height: '70vh', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                  <Tab label="AI Chat" />
                  <Tab label="Analysis Dashboard" />
                  <Tab label="Export" />
                </Tabs>
              </Box>

              <TabPanel value={activeTab} index={0}>
                <Box sx={{ height: '50vh', overflow: 'auto', p: 1 }}>
                  {chatHistory.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                  ))}
                  {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                      <CircularProgress size={24} />
                    </Box>
                  )}
                  <div ref={messagesEndRef} />
                </Box>
                
                <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      placeholder="Ask me anything about your data... (e.g., 'who is the most active user?', 'what are some bottlenecks?')"
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={loading}
                      multiline
                      maxRows={3}
                    />
                    <IconButton
                      color="primary"
                      onClick={handleSendMessage}
                      disabled={!currentMessage.trim() || loading}
                    >
                      <Send />
                    </IconButton>
                  </Box>
                </Box>
              </TabPanel>

              <TabPanel value={activeTab} index={1}>
                <Box sx={{ height: '50vh', overflow: 'auto' }}>
                  {analysisData && (
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Analysis Results
                      </Typography>
                      <Paper sx={{ p: 2, mb: 2 }}>
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {analysisData.text}
                        </Typography>
                      </Paper>
                      {analysisData.chart && (
                        <VegaLiteChart spec={analysisData.chart} />
                      )}
                      {analysisData.chartJson && !analysisData.chart && (
                        <SimpleChart spec={analysisData.chartJson} title="Chart Visualization" />
                      )}
                    </Box>
                  )}
                </Box>
              </TabPanel>

              <TabPanel value={activeTab} index={2}>
                <Box sx={{ height: '50vh' }}>
                  <Typography variant="h6" gutterBottom>
                    Export Options
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<Download />}
                      onClick={handleExportChat}
                      disabled={chatHistory.length === 0}
                    >
                      Export Chat History
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<PictureAsPdf />}
                      onClick={() => setExportDialogOpen(true)}
                    >
                      Export Analysis PDF
                    </Button>
                  </Box>
                </Box>
              </TabPanel>
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Export Dialog */}
      <Dialog open={exportDialogOpen} onClose={() => setExportDialogOpen(false)}>
        <DialogTitle>Export Analysis PDF</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            This feature will be available in the next update. For now, you can export chat history and individual charts.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExportDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}

export default App;