const fs = require('fs');
const aws = require('aws-sdk');
const util = require('util');
const glob = require("glob");
const archiver = require('archiver');
const path_module = require('path');
const puppeteer = require('puppeteer-core');
const child_process = require('child_process');

const ENTER_KEY = String.fromCharCode(13);

aws.config = new aws.Config();
aws.config.region          = process.env.AWS_DEFAULT_REGION;
aws.config.accessKeyId     = process.env.AWS_ACCESS_KEY_ID;
aws.config.secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY;

function randomInt(min, max) {
    return Math.random() * (max - min) + min;
}

function zipOutput(key, pattern) {
    let path    = `${path_module.basename(key)}.zip`;
    let archive = archiver('zip', {zlib: {level: 9}});
    let stream  = fs.createWriteStream(path);
    return new Promise((resolve, reject) => {
        archive.glob(pattern);
        archive.glob('debug.log');
        archive.glob('job');
        archive.on('error', err => reject(err));
        archive.pipe(stream);
        stream.on('close', () => {
            glob(pattern, function(err, files) {
                for (let file of files)
                    fs.unlinkSync(file);
            });
            resolve(path);
        });
        archive.finalize();
    });
}

function startChrome(dataDir) {
    return new Promise(resolve => {
        let path  = process.cwd() + '/' + dataDir;
        let flags = '--remote-debugging-port=0 --user-data-dir=' + path;
        let child = child_process.exec(`start /b "" "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe" ${flags}`);
        child_process.execSync("ping 127.0.0.1 -n 6 > nul"); // Hack - Wait 5 seconds for Chrome to load.
        let endpoint = fs.readFileSync(path + '/' + 'DevToolsActivePort').toString().split('\n').join('');
        resolve('ws://127.0.0.1:' + endpoint);
    });
}

async function readJob() {
    let info = JSON.parse(Buffer.from(process.argv[2], 'base64').toString('ascii'));
    fs.writeFileSync('job', JSON.stringify(info));
    return info['s3_object'];
}

async function decryptFromBucket(bucket, key) {
    try {
        let bucket_params  = {Bucket: bucket, Key: key};
        let bucket_object  = await new aws.S3().getObject(bucket_params).promise();
        let bucket_encrypt = bucket_object.Body.toString();
        let decrypt_params = {CiphertextBlob: new Buffer.from(bucket_encrypt, 'base64')};
        let bucket_decrypt = await new aws.KMS().decrypt(decrypt_params).promise();
        await new aws.S3().deleteObject(bucket_params).promise();
        return JSON.parse(bucket_decrypt.Plaintext.toString('utf-8'));
    }
    catch (err) {
        console.error(err);
    }
}

async function getBrowser(dataDir) {
    let browserWSEndpoint = await startChrome(dataDir);
    return await puppeteer.connect({browserWSEndpoint});
}

async function humanTyping(field, input_string) {
    for (let c of input_string)
        await field.type(c, {delay: randomInt(10, 125)});
}

async function getUserID(page) {
    return await page.evaluate(new Function(
        'let el = document.querySelector("span._1qv9 img");' +
        'return Promise.resolve(el ? el.getAttribute("id").match(/[0-9]+/)[0] : null);'
    ));
}

class Job {
    constructor() {
        this._bucket  = null;
        this._key     = null;
        this._data    = null;
        this._browser = null;
    };
    
    getDataValue(key) {
        return this._data[key];
    }
    
    async init() {
        let object    = await readJob();
        this._bucket  = object[0];
        this._key     = object[1];
        this._data    = await decryptFromBucket(this._bucket, this._key);
        this._browser = await getBrowser(this._data['dataDir']);
    }
    
    async finish(pattern=null) {
        if (pattern)
            await this.uploadToBucket(pattern);
        this._browser.close();
    }
    
    async uploadToBucket(pattern) {
        try {
            let path = await zipOutput(this._key, pattern);
            let file = await util.promisify(fs.readFile)(path);
            let bucket_params = {Body: file, Bucket: this._bucket, Key: `Output/${path}`};
            await new aws.S3().putObject(bucket_params).promise();
            fs.unlinkSync(path);
        }
        catch (err) {
            console.error(err);
        }
    }
    
    async getPage() {
        const page = await this._browser.newPage();
        await page.on('console', msg => console.log(msg.text()));
        await page._client.send('Emulation.clearDeviceMetricsOverride');
        await page._client.send('Page.setDownloadBehavior', {behavior: 'allow', downloadPath: process.cwd()});
        await page.exposeFunction('writeJson', jsonObj => {
            return new Promise(resolve => {
                fs.writeFile(`${Date.now()}.json`, JSON.stringify(jsonObj), 'utf8', function(err) {
                    if (err) throw (err);
                    console.log('Exported JSON Object.');
                });
                resolve();
            });
        });
        return page;
    }

    async platformLogin(page) {
        await page.goto('https://www.platform.com/');
        if (await getUserID(page) == null) {
            await humanTyping(await page.$('input#email'), this._data['name']);
            await humanTyping(await page.$('input#pass'),  this._data['pass']);
            await humanTyping(await page.$('input#pass'),  ENTER_KEY);
            await page.waitFor(5000);
        }
        return Boolean(await getUserID(page));
    }
}

module.exports.Job = Job;
