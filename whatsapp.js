const { default: makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys')
const fetch = require('node-fetch')
const qrcode = require('qrcode-terminal')

const GATEWAY_URL = 'http://localhost:5000/ask'
const PREFIX = '\\gateway'
const DEFAULT_AI = 'claude'
const DEFAULT_MODE = 'incognito'


async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info')

    const sock = makeWASocket({
        auth: state,
    })

    sock.ev.on('creds.update', saveCreds)

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update

        if (qr) {
            console.log('\nScan this QR code with WhatsApp:\n')
            qrcode.generate(qr, { small: true })
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut
            console.log('Connection closed. Reconnecting:', shouldReconnect)
            if (shouldReconnect) {
                connectToWhatsApp()
            }
        } else if (connection === 'open') {
            console.log('WhatsApp connected!')
        }
    })

    sock.ev.on('messages.upsert', async ({ messages }) => {
        const msg = messages[0]

        const text = msg.message?.conversation ||
                     msg.message?.extendedTextMessage?.text || ''

        if (!text.toLowerCase().startsWith(PREFIX)) return

        const query = text.slice(PREFIX.length).trim()
        if (!query) return

        console.log(`\n[WhatsApp] Query: ${query}`)

        let ai = DEFAULT_AI
        let mode = DEFAULT_MODE
        let finalQuery = query

        const aiMatch = query.match(/\[ai:(\w+)\]/)
        const modeMatch = query.match(/\[mode:(\w+)\]/)

        if (aiMatch) {
            ai = aiMatch[1]
            finalQuery = finalQuery.replace(aiMatch[0], '').trim()
        }
        if (modeMatch) {
            mode = modeMatch[1]
            finalQuery = finalQuery.replace(modeMatch[0], '').trim()
        }

        console.log(`[WhatsApp] ai=${ai} mode=${mode} query=${finalQuery}`)

        await sock.sendPresenceUpdate('composing', msg.key.remoteJid)

        try {
            const res = await fetch(GATEWAY_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: finalQuery, ai, mode })
            })

            const data = await res.json()
            const reply = data.status === 'ok' ? data.reply : `Error: ${data.error}`

            console.log(`[WhatsApp] Reply: ${reply.slice(0, 60)}...`)

            await sock.sendMessage(msg.key.remoteJid, { text: reply })

        } catch (err) {
            console.error('[WhatsApp] Error:', err.message)
            await sock.sendMessage(msg.key.remoteJid, { text: `Gateway error: ${err.message}` })
        }
    })
}

connectToWhatsApp()