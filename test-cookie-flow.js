/**
 * Debug Script: Test Cookie Flow from Next.js SSR to Backend
 *
 * This script simulates what happens in the E2E test:
 * 1. Get a valid auth token from backend
 * 2. Simulate Next.js SSR fetching with Cookie header
 * 3. Check if backend accepts the cookie
 */

const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmUwMDAwMC0wMDAwLTAwMDAtMDAwMS0wMDAwMDAwMDAwMDEiLCJleHAiOjE3Mzc1ODgwMDB9.test'; // Placeholder - replace with real token

const BACKEND_URL = 'http://localhost:8000/api/v1';
const TEAM_ID = 'e2e00000-0000-0000-0004-000000000001';

async function testCookieFlow() {
  console.log('=== Testing Cookie Flow ===\n');

  // Test 1: Direct backend call with Authorization header
  console.log('Test 1: Backend with Authorization header');
  try {
    const response1 = await fetch(`${BACKEND_URL}/teams/${TEAM_ID}`, {
      headers: {
        'Authorization': `Bearer ${TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    console.log(`  Status: ${response1.status}`);
    if (!response1.ok) {
      const error = await response1.json();
      console.log(`  Error: ${JSON.stringify(error)}`);
    } else {
      const data = await response1.json();
      console.log(`  Success: Team "${data.name}"`);
    }
  } catch (e) {
    console.log(`  Exception: ${e.message}`);
  }

  console.log('');

  // Test 2: Backend call with Cookie header (simulating Next.js SSR)
  console.log('Test 2: Backend with Cookie header (SSR simulation)');
  try {
    const response2 = await fetch(`${BACKEND_URL}/teams/${TEAM_ID}`, {
      headers: {
        'Cookie': `hb_access_token=${TOKEN}`,
        'Content-Type': 'application/json'
      }
    });
    console.log(`  Status: ${response2.status}`);
    if (!response2.ok) {
      const error = await response2.json();
      console.log(`  Error: ${JSON.stringify(error)}`);
    } else {
      const data = await response2.json();
      console.log(`  Success: Team "${data.name}"`);
    }
  } catch (e) {
    console.log(`  Exception: ${e.message}`);
  }

  console.log('');

  // Test 3: Login to get real token
  console.log('Test 3: Getting real token via login');
  try {
    const formData = new URLSearchParams();
    formData.append('username', 'admin@e2e.com');
    formData.append('password', 'Admin@123');

    const loginResponse = await fetch(`${BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    });
    console.log(`  Login Status: ${loginResponse.status}`);

    if (loginResponse.ok) {
      // Check for token in cookies
      const cookies = loginResponse.headers.get('set-cookie');
      console.log(`  Set-Cookie header: ${cookies ? 'Present' : 'Not present'}`);

      if (cookies) {
        const tokenMatch = cookies.match(/hb_access_token=([^;]+)/);
        if (tokenMatch) {
          const realToken = tokenMatch[1];
          console.log(`  Token extracted: ${realToken.substring(0, 50)}...`);

          // Test 4: Use real token with Cookie header
          console.log('\nTest 4: Using real token with Cookie header');
          const response4 = await fetch(`${BACKEND_URL}/teams/${TEAM_ID}`, {
            headers: {
              'Cookie': `hb_access_token=${realToken}`,
              'Content-Type': 'application/json'
            }
          });
          console.log(`  Status: ${response4.status}`);
          if (!response4.ok) {
            const error = await response4.json();
            console.log(`  Error: ${JSON.stringify(error)}`);
          } else {
            const data = await response4.json();
            console.log(`  ✅ SUCCESS: Team "${data.name}"`);
            console.log(`  → Cookie forwarding is WORKING!`);
          }
        }
      }
    } else {
      const error = await loginResponse.json();
      console.log(`  Login failed: ${JSON.stringify(error)}`);
    }
  } catch (e) {
    console.log(`  Exception: ${e.message}`);
  }
}

testCookieFlow().catch(console.error);
