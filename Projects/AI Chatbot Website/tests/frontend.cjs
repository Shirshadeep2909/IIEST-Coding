// Run with jsdom installed and available through NODE_PATH (see README).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM} = require('jsdom');
const root = path.join(__dirname, '..');
const dom = new JSDOM(fs.readFileSync(path.join(root, 'templates/index.html'), 'utf8'), {runScripts: 'outside-only'});
const w = dom.window;
const pending = [];
w.fetch = async (url) => {
    if (url === '/history') return {ok: true, json: async () => ({messages: []})};
    if (url === '/new-chat') return {ok: true, json: async () => ({messages: []})};
    return new Promise(resolve => pending.push(resolve));
};
for (const file of ['vendor/marked.min.js', 'vendor/purify.min.js', 'script.js']) {
    w.eval(fs.readFileSync(path.join(root, 'static', file), 'utf8'));
}
const tick = () => new Promise(resolve => setImmediate(resolve));
(async () => {
    await tick();
    const box = w.document.getElementById('msg');
    box.value = '<img src=x onerror="alert(1)">';
    const first = w.send();
    assert.equal(w.document.querySelector('.user img'), null);
    const bubble = w.document.querySelector('.ai');
    box.value = 'duplicate';
    await w.send();
    assert.equal(pending.length, 1);
    assert.equal(bubble.isConnected, true);
    pending.shift()({ok: true, json: async () => ({reply: '**Hello** <img src=x onerror="alert(1)"><script>alert(1)</script>'})});
    await first;
    assert.equal(bubble.querySelector('strong').textContent, 'Hello');
    assert.equal(bubble.querySelector('[onerror], script'), null);
    box.value = 'retry me';
    const failure = w.send();
    pending.shift()({ok: false, json: async () => ({error: 'Model unavailable'})});
    await failure;
    assert.equal(box.value, 'retry me');
    assert.equal(w.document.querySelector('.error').textContent, 'Model unavailable');
    assert.equal(w.document.getElementById('send-button').disabled, false);
    await w.newChat();
    assert.equal(w.document.getElementById('chat').children.length, 0);
    console.log('Frontend passed: HTML escaping, sanitized Markdown, duplicate-send guard, attached reply, error/retry, New Chat.');
    dom.window.close();
})().catch(error => {console.error(error); dom.window.close(); process.exitCode = 1;});
