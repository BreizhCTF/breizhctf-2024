const puppeteer = require("puppeteer");

const FLAG = process.env.FLAG ?? "BZHCTF{fake_flag}";

async function goto(port, reference, reason) {
	let ret = true;
	const browser = await puppeteer.launch({
		headless: "new",
		ignoreHTTPSErrors: true,
		executablePath: "/usr/bin/chromium",
		args: [
			"--no-sandbox",
			"--ignore-certificate-errors"
		],
	});

	const page = await browser.newPage();

	await page.waitForFrame;

	try {
		await page.setJavaScriptEnabled(false); // On m'a toujours dit de ne jamais faire confiance aux utilisateurs
		await page.goto(`http://localhost:${port}/reports?ref=${encodeURIComponent(reference)}&reason=${encodeURIComponent(reason)}&flag=${encodeURIComponent(FLAG)}`);
		await page.waitForSelector("#delete");
		await page.click('#delete');
		// TODO: intégrer une IA pour déterminer si oui ou non il faut supprimer
	} catch (err) {
		console.log(`[BOT - ERROR] ${err}`)
		ret = false;
	}

	await page.close();
	browser.close();

	return ret;
}

module.exports = { goto };
