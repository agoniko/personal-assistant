import { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  List,
  ListItem,
  Divider,
  Fade,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { api } from '../../services/api';
import { FormattedMessage } from '../FormattedMessage/FormattedMessage';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
  type?: 'email' | 'calendar' | 'text';
}

export const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string>('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  useEffect(() => {
    // Focus input when component mounts and after each message
    inputRef.current?.focus();
  }, [messages]);

  const detectMessageType = (text: string): 'email' | 'calendar' | 'text' => {
    if (text.includes('[EMAIL]')) {
      return 'email';
    }
    if (text.includes('**Event**:') && text.includes('**Location**:')) {
      return 'calendar';
    }
    return 'text';
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      text: input,
      isUser: true,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setStreamingMessage('');

    try {
      const response = await api.post('/api/chat', {
        message: input,
        conversation_id: conversationId,
      }, (chunk) => {
        setStreamingMessage(chunk);
      });

      const messageType = detectMessageType(response.data.response);
      const assistantMessage: Message = {
        text: response.data.response,
        isUser: false,
        timestamp: new Date(),
        type: messageType
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingMessage('');
      setConversationId(response.data.conversation_id);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        text: 'Sorry, there was an error processing your message.',
        isUser: false,
        timestamp: new Date(),
        type: 'text'
      };
      setMessages((prev) => [...prev, errorMessage]);
      setStreamingMessage('');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        background: 'rgba(45, 45, 45, 0.8)',
        backdropFilter: 'blur(10px)',
        borderRadius: '16px',
        overflow: 'hidden',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          overflow: 'auto',
          display: 'flex',
          flexDirection: 'column',
          background: 'transparent',
          p: 2,
        }}
      >
        <List sx={{ flex: 1 }}>
          <AnimatePresence mode="popLayout">
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ListItem
                  sx={{
                    flexDirection: 'column',
                    alignItems: message.isUser ? 'flex-end' : 'flex-start',
                    px: 0,
                  }}
                >
                  {message.isUser ? (
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        backgroundColor: 'primary.main',
                        maxWidth: '70%',
                        borderRadius: '16px 16px 4px 16px',
                      }}
                    >
                      <Typography sx={{ color: 'white' }}>
                        {message.text}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          color: 'white',
                          display: 'block',
                          mt: 1,
                          opacity: 0.8,
                        }}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  ) : (
                    <Box sx={{ maxWidth: '70%' }}>
                      <FormattedMessage
                        message={message.text}
                        type={message.type || 'text'}
                      />
                      <Typography
                        variant="caption"
                        sx={{
                          color: 'text.secondary',
                          display: 'block',
                          mt: 1,
                          opacity: 0.8,
                        }}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  )}
                </ListItem>
              </motion.div>
            ))}
            {streamingMessage && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ListItem
                  sx={{
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    px: 0,
                  }}
                >
                  <Box sx={{ maxWidth: '70%' }}>
                    <FormattedMessage
                      message={streamingMessage}
                      type="text"
                    />
                  </Box>
                </ListItem>
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </List>
      </Paper>
      <Paper
        elevation={0}
        sx={{
          p: 2,
          background: 'rgba(45, 45, 45, 0.8)',
          backdropFilter: 'blur(10px)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            inputRef={inputRef}
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            variant="outlined"
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '12px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.1)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: 'primary.main',
                },
              },
            }}
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            sx={{
              alignSelf: 'flex-end',
              mb: 1,
              '&:hover': {
                backgroundColor: 'rgba(0, 180, 216, 0.1)',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
}; 