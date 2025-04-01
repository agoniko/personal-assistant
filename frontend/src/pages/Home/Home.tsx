import { Box, Typography, Paper } from '@mui/material';
import { Chat } from '../../components/Chat/Chat';

export const Home = () => {
  return (
    <Box sx={{ height: 'calc(100vh - 100px)' }}>
      <Typography variant="h4" gutterBottom>
        Chat with Your Assistant
      </Typography>
      <Paper sx={{ height: 'calc(100% - 60px)', p: 2 }}>
        <Chat />
      </Paper>
    </Box>
  );
}; 