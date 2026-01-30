const express = require('express');
const router = express.Router();
const { 
  handleChat, 
  getConversationHistory, 
  clearConversation, 
  getAIStatus 
} = require('../controllers/chatController.cjs');

// Main chat endpoint
router.post('/', handleChat);

// Conversation management
router.get('/history', getConversationHistory);
router.delete('/conversation', clearConversation);

// AI service status
router.get('/status', getAIStatus);

module.exports = router;
