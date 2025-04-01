import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container } from '@mui/material';
import { Chat } from './components/Chat/Chat';
import { theme } from './theme';
import { motion } from 'framer-motion';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
        style={{ height: '100vh', width: '100vw', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
      >
        <Box
          sx={{
            width: '100%',
            height: '100%',
            background: 'linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Container
            maxWidth="lg"
            sx={{
              height: '90vh',
              display: 'flex',
              flexDirection: 'column',
              px: { xs: 2, sm: 3, md: 4 },
              '& > *': {
                height: '100%',
              },
            }}
          >
            <Chat />
          </Container>
        </Box>
      </motion.div>
    </ThemeProvider>
  );
}

export default App;
