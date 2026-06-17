import re

path = r"C:\Projects\quarryai\apps\ws\test_call.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_func = '''        function playMulaw(mulawData) {
            try {
                const ctx = new AudioContext();
                const samples = new Float32Array(mulawData.length);
                for (let i = 0; i < mulawData.length; i++) {
                    const mu = 255;
                    const x = mulawData.charCodeAt(i) / 128;
                    samples[i] = Math.sign(x) * (Math.pow(1 + mu, Math.abs(x)) - 1) / mu;
                }
                const buffer = ctx.createBuffer(1, samples.length, 8000);
                buffer.copyToChannel(samples, 0);
                const source = ctx.createBufferSource();
                source.buffer = buffer;
                source.connect(ctx.destination);
                source.start();
            } catch(e) {
                addLog('⚠️ Audio playback error: ' + e);
            }
        }'''

new_func = '''        // Proper G.711 mu-law decode (mu-law byte -> 16-bit signed PCM)
        function mulawByteToPcm(muByte) {
            muByte = ~muByte & 0xFF;
            const sign = muByte & 0x80;
            const exponent = (muByte >> 4) & 0x07;
            const mantissa = muByte & 0x0F;
            let sample = ((mantissa << 3) + 0x84) << exponent;
            sample -= 0x84;
            return sign ? -sample : sample;
        }

        let sharedAudioCtx = null;
        function playMulaw(mulawData) {
            try {
                if (!sharedAudioCtx) {
                    sharedAudioCtx = new AudioContext();
                }
                const ctx = sharedAudioCtx;
                const len = mulawData.length;
                const samples = new Float32Array(len);
                for (let i = 0; i < len; i++) {
                    const pcm16 = mulawByteToPcm(mulawData.charCodeAt(i) & 0xFF);
                    samples[i] = pcm16 / 32768;
                }
                const buffer = ctx.createBuffer(1, len, 8000);
                buffer.copyToChannel(samples, 0);
                const source = ctx.createBufferSource();
                source.buffer = buffer;
                source.connect(ctx.destination);
                source.start();
            } catch(e) {
                addLog('⚠️ Audio playback error: ' + e);
            }
        }'''

if old_func not in content:
    print("ERROR: old function not found — file may have changed.")
else:
    content = content.replace(old_func, new_func)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS: playMulaw() fixed.")