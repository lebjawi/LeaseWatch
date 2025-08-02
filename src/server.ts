/**
 * Optional HTTP Server for LeaseWatch
 * This file can be used if you need to expose LeaseWatch as a web service
 */

import * as http from 'http';
import { main } from '../index';

const PORT = process.env.PORT || 1300;

const server = http.createServer(async (req, res) => {
  if (req.url === '/scrape' && req.method === 'POST') {
    try {
      console.log('🌐 HTTP request received to start scraping...');
      await main();
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ 
        success: true, 
        message: 'Scraping completed successfully',
        timestamp: new Date().toISOString()
      }));
    } catch (error) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      }));
    }
  } else if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      status: 'healthy',
      service: 'LeaseWatch',
      timestamp: new Date().toISOString()
    }));
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
      error: 'Not Found',
      availableEndpoints: ['/health (GET)', '/scrape (POST)']
    }));
  }
});

server.listen(PORT, () => {
  console.log(`🌐 LeaseWatch server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log(`  - GET  http://localhost:${PORT}/health`);
  console.log(`  - POST http://localhost:${PORT}/scrape`);
});

export { server };
