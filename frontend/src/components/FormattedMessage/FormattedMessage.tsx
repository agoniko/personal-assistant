import { Box, Typography, Paper } from '@mui/material';

interface FormattedMessageProps {
  message: string;
  type: 'email' | 'calendar' | 'text';
}

export const FormattedMessage = ({ message, type }: FormattedMessageProps) => {
  const renderContent = () => {
    switch (type) {
      case 'email': {
        // Split message into individual email blocks
        const emailBlocks = message.split('[EMAIL]').filter(block => block.trim());
        
        if (emailBlocks.length === 0) return <Typography>{message}</Typography>;
        
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {emailBlocks.map((block, index) => {
              const lines = block.trim().split('\n');
              return (
                <Paper
                  key={index}
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '16px 16px 16px 4px',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                  }}
                >
                  {lines.map((line, lineIndex) => (
                    <Typography
                      key={lineIndex}
                      sx={{
                        mb: 1,
                        color: lineIndex === 0 ? 'text.secondary' : 'text.primary',
                        opacity: lineIndex === 0 ? 0.8 : 1,
                      }}
                    >
                      {line}
                    </Typography>
                  ))}
                </Paper>
              );
            })}
          </Box>
        );
      }
      case 'calendar': {
        return (
          <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '16px 16px 16px 4px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
            }}
          >
            {message.split('\n').map((line, index) => (
              <Typography
                key={index}
                sx={{
                  mb: 1,
                  color: index === 0 ? 'text.secondary' : 'text.primary',
                  opacity: index === 0 ? 0.8 : 1,
                }}
              >
                {line}
              </Typography>
            ))}
          </Paper>
        );
      }
      default:
        return (
          <Typography
            sx={{
              color: 'text.primary',
              opacity: 0.9,
            }}
          >
            {message}
          </Typography>
        );
    }
  };

  return (
    <Box sx={{ my: 2 }}>
      {renderContent()}
    </Box>
  );
}; 