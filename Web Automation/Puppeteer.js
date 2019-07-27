// npm i -g pkg
// npm init
// npm i puppeteer-core

const fs = require('fs');
const http = require('http');
const puppeteer = require('puppeteer-core');
const child_process = require('child_process');

const port = 9222;
const data = JSON.parse(fs.readFileSync('data.json', 'UTF-8'));

function startChrome() {
    return new Promise(resolve => {
        child_process.exec(`start /b "dumpster" "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" --remote-debugging-port=${port}`);
        resolve();
    });
}

function getBrowserWSEndpoint() {
    return new Promise(resolve => {
        http.get(`http://localhost:${port}/json/version`, (res) => {
            res.on('data', function (chunk) {
                resolve(JSON.parse(chunk)['webSocketDebuggerUrl']);
            });
        });
    });
}

async function loggedIn(page) {
    return await page.evaluate(new Function(
        'let el = document.querySelector("span.uid");' +
        'return Promise.resolve(el ? el.getAttribute("id").match(/[0-9]+/)[0] : null)'
    ));
}

async function login(page) {
    await page.goto('https://login-url.com/');
    if (!loggedIn) {
        await (await page.$('input#email')).type(data['name'], {delay: 50});
        await (await page.$('input#pass')).type(data['pass'], {delay: 50});
        await (await page.$('button#login')).click();
        await page.waitFor(5000);
    }
}

(async () => {
    await startChrome();
    const browserWSEndpoint = await getBrowserWSEndpoint();
    const browser = await puppeteer.connect({browserWSEndpoint});
    const newPage = await browser.newPage();
    await newPage.on('console', msg => console.log(msg.text()));
    await newPage._client.send('Emulation.clearDeviceMetricsOverride');
    await login(newPage);
	
	// do stuff
    
	await browser.close();
})();
