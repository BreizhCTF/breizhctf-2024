const puppeteer = require("puppeteer");

async function goto(url) {
	const browser = await puppeteer.launch({
		headless: "new",
		ignoreHTTPSErrors: true,
    executablePath: "/usr/bin/chromium",
		args: [
            "--no-sandbox",
            "--ignore-certificate-errors"
        ],
    });

  /**
   * À cause des règles firewall du BreizhCTF, le challenge ne peut pas accèder à https://ownform.ctf.bzh
   * À la place il accède à https://localhost:443
   * Pensez à utiliser https://localhost au lieu de https://ownform.ctf.bzh dans vos exploit
   */
	const page = await browser.newPage();
  await page.setCookie({
    name: "flag",
    value: process.env.FLAG ?? "BZHCTF{fakeflag}",
    domain: "localhost",
    path: "/",
    httpOnly: false,
    secure: false
  });

  await page.waitForFrame
  
	try {
	    await page.goto(url);
	} catch {
  }

  await page.close();
  browser.close();

	return;
}

module.exports = {goto};
