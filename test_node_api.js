const axios = require('axios');

async function testAPI() {
  try {
    console.log('Testing Node.js backend API...');

    // Health check
    const healthResponse = await axios.get('http://localhost:3001/health');
    console.log('✅ Health:', healthResponse.data);

    // Status
    const statusResponse = await axios.get('http://localhost:3001/api/status');
    console.log('✅ Status:', statusResponse.data);

    // Market
    const marketResponse = await axios.get('http://localhost:3001/api/market');
    console.log('✅ Market:', marketResponse.data);

    console.log('🎉 All API endpoints working!');

  } catch (error) {
    console.error('❌ API test failed:', error.message);
  }
}

testAPI();