export default async function handler(req, res) {
  // CORS configuration to allow the Render backend to hit this endpoint
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, x-discord-webhook, x-proxy-secret'
  );

  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST' && req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Security check: Verify PROXY_SECRET
  const expectedSecret = process.env.PROXY_SECRET;
  const providedSecret = req.headers['x-proxy-secret'];

  // Only enforce if the environment variable is configured
  if (expectedSecret && providedSecret !== expectedSecret) {
    return res.status(401).json({ error: 'Unauthorized: Invalid proxy secret' });
  }

  // Get the target Discord webhook from headers
  const webhookUrl = req.headers['x-discord-webhook'];
  
  if (!webhookUrl || !webhookUrl.startsWith('https://discord.com/api/webhooks/')) {
    return res.status(400).json({ error: 'Invalid or missing Discord webhook URL in headers' });
  }

  try {
    // Determine fetch options
    const fetchOptions = {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        // Spoof the User-Agent slightly to avoid default fetch blocking
        'User-Agent': 'SynapseSync/1.0 (https://synapsesync-sam.vercel.app, 1.0)',
      },
    };

    if (req.method === 'POST') {
      fetchOptions.body = JSON.stringify(req.body);
    }

    // Forward the request to Discord
    const discordRes = await fetch(webhookUrl, fetchOptions);

    if (discordRes.ok) {
      // If Discord returns 204 No Content, we can't parse JSON
      if (discordRes.status === 204) {
        return res.status(204).send();
      }
      
      const data = await discordRes.json();
      return res.status(discordRes.status).json(data);
    } else {
      const errorText = await discordRes.text();
      return res.status(discordRes.status).send(errorText);
    }
  } catch (error) {
    console.error('Discord Proxy Error:', error);
    return res.status(500).json({ error: 'Failed to proxy request to Discord' });
  }
}
