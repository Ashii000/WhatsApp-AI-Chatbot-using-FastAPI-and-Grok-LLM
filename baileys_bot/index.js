/**
 * index.js
 *
 * Baileys WhatsApp bot — unofficial library, no Meta Business Verification needed.
 *
 * RUN:
 *   node index.js
 *
 * Then open in browser:
 *   http://<your-server-ip>:3000/qr
 *
 * Scan the QR with the WhatsApp app (Settings > Linked Devices > Link a Device)
 * on the phone number you want the bot to use.
 */

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const QRCode = require('qrcode');
const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

let latestQR = null;        // stores the current QR as a base64 image string
let connectionStatus = 'starting';  // starting | qr_ready | connected | disconnected

// ---------------------------------------------------------
// 1. WhatsApp connection setup
// ---------------------------------------------------------
async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false, // we render it on the website instead
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            // Convert the raw QR text into a real PNG image (base64 data URL)
            latestQR = await QRCode.toDataURL(qr);
            connectionStatus = 'qr_ready';
            console.log('📷 New QR code generated. Open /qr in your browser to scan it.');
        }

        if (connection === 'open') {
            connectionStatus = 'connected';
            latestQR = null;
            console.log('✅ WhatsApp connected successfully!');
        }

        if (connection === 'close') {
            connectionStatus = 'disconnected';
            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('⚠️ Connection closed. Reconnecting:', shouldReconnect);
            if (shouldReconnect) {
                startBot();
            }
        }
    });

    // ---------------------------------------------------------
    // 2. Incoming message handler
    // ---------------------------------------------------------
    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0];
        if (!msg.message || msg.key.fromMe) return; // ignore our own messages

        const from = msg.key.remoteJid;       // e.g. "923001234567@s.whatsapp.net"
        const text =
            msg.message.conversation ||
            msg.message.extendedTextMessage?.text ||
            '';

        if (!text) return; // ignore non-text messages for now (images/voice etc.)

        console.log(`📥 Message from ${from}: ${text}`);

        try {
            const reply = await generateAIReply(from, text);
            await sock.sendMessage(from, { text: reply });
            console.log(`📤 Replied to ${from}: ${reply}`);
        } catch (err) {
            console.error('❌ Error handling message:', err.message);
        }
    });
}

// ---------------------------------------------------------
// 3. AI reply generation (placeholder — wire up your provider here)
// ---------------------------------------------------------
async function generateAIReply(from, userMessage) {
    // TODO: connect this to your existing memory/storyline system.
    // For now this calls OpenRouter directly as a minimal working example.
    const response = await axios.post(
        'https://openrouter.ai/api/v1/chat/completions',
        {
            model: 'gryphe/mythomax-l2-13b',
            messages: [
                { role: 'system', content: 'You are a warm, emotionally intelligent romantic chat partner. Reply naturally like a real person texting.' },
                { role: 'user', content: userMessage },
            ],
            max_tokens: 150,
            temperature: 0.85,
        },
        {
            headers: {
                Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
                'Content-Type': 'application/json',
            },
        }
    );
    return response.data.choices[0].message.content;
}

// ---------------------------------------------------------
// 4. Web server to show the QR code in a browser
// ---------------------------------------------------------
app.get('/qr', (req, res) => {
    if (connectionStatus === 'connected') {
        return res.send('<h2>✅ Already connected! No QR needed.</h2>');
    }
    if (!latestQR) {
        return res.send('<h2>⏳ QR not generated yet, refresh in a few seconds...</h2>');
    }
    res.send(`
        <html>
            <body style="text-align:center; font-family:sans-serif;">
                <h2>Scan this QR code with WhatsApp</h2>
                <img src="${latestQR}" style="width:300px;height:300px;" />
                <p>Status: ${connectionStatus}</p>
            </body>
        </html>
    `);
});

app.get('/status', (req, res) => {
    res.json({ status: connectionStatus });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌐 QR web server running. Open http://<server-ip>:${PORT}/qr in your browser.`);
});

startBot();
