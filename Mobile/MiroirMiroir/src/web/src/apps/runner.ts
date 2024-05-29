import path from "path";
import * as fs from "fs/promises";
import * as winston from "winston";
import { AVD } from "../classes/avd.class";
import { runCommand, getApkMain, sleep } from "../utils";

// Global app logger
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
  defaultMeta: { scope: "runner" },
});

// Logger dedicated to user output
const userLogger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
  defaultMeta: { scope: "user" },
});

// Logger dedicated to send callbacks to web app
const screenshotLogger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
  defaultMeta: { scope: "screenshot" },
});

const waitApk = async (path: string) => {
  for (let i = 0; i < 60; i++) {
    try {
      await fs.stat(path);
      await sleep(5);
      return true;
    } catch (_) {
      logger.verbose("Waiting for APK to be dropped");
    }
    await sleep(1);
  }
  throw new Error("Unable to find APK");
};

export const checkExploit = async (
  avd: AVD,
  apk: string,
  userCallback: (message: string) => any
) => {
  userLogger.info("Préparation de l'AVD ...");

  await runCommand("adb", ["shell", "locksettings", "get-disabled"]);

  // Stop all apps
  await runCommand("bash", [
    "-c",
    "apps=$(adb shell dumpsys window windows | grep -P 'topApp.* u0 ([^/]+)' | grep -oP '(?<= u0 )[^/]+') ; [ -z \"$apps\" ] || echo $apps | xargs -l adb shell am force-stop",
  ]);

  // Extra safe : ensure screen is locked. If not, set a random password.
  await runCommand("bash", [
    "-c",
    '([ $(adb shell locksettings get-disabled) = "false" ] || adb shell locksettings set-password "$(openssl rand -hex 8)")',
  ]);

  // Turn off screen
  await runCommand("bash", [
    "-c",
    'if adb shell dumpsys input_method | grep -q "mInteractive=true"; then adb shell input keyevent KEYCODE_POWER;fi && while adb shell dumpsys input_method | grep -q "mInteractive=true"; do sleep 0.1; done',
  ]);

  // Wake up screen
  await runCommand("bash", [
    "-c",
    'adb shell input keyevent KEYCODE_WAKEUP && while adb shell dumpsys input_method | grep -q "mInteractive=false"; do sleep 0.1; done',
  ]);

  // Ensure screen is locked
  await runCommand("bash", [
    "-c",
    'while adb shell dumpsys power | grep -q "mUserActivityTimeoutOverrideFromWindowManager=-1"; do sleep 0.1; done && sleep 1',
  ]);

  // Wait
  await sleep(5);

  userCallback("AVD prêt !");

  userCallback("Screenshot n.1 : l'écran est vérouillé 🔒");
  await fs.writeFile(`/tmp/${avd.uuid}-pre.png`, await avd.screenShot());
  screenshotLogger.info("pre");

  // Install APK
  userCallback("Installation de votre APK ...");
  await runCommand("adb", ["install", "-r", apk]);

  // Run main activity
  const mainActivity = await getApkMain(apk);
  userCallback(`Lancement de votre APK (${mainActivity}) ...`);
  await runCommand("adb", ["shell", "am", "start", "-W", "-n", mainActivity]);
  await sleep(5);

  await runCommand("bash", [
    "-c",
    'adb shell input keyevent KEYCODE_WAKEUP && while adb shell dumpsys input_method | grep -q "mInteractive=false"; do sleep 0.1; done',
  ]);
  await sleep(2);

  // Go to home screen
  await runCommand("adb", ["shell", "input", "keyevent", "KEYCODE_HOME"]);
  await sleep(2);

  userCallback("Installation de l'APK flag ...");
  await runCommand("adb", ["install", "-r", "/challenge/flag_1a2a7.apk"]);

  userCallback("Lancement de l'APK flag 🚩");
  await runCommand("adb", [
    "shell",
    "am",
    "start",
    "-W",
    "-n",
    "com.mirror.flag/com.mirror.flag.MainActivity",
  ]);
  userCallback(
    "Screenshot n.2 : l'écran devrait être vérouillé (enfin on espère 😰)"
  );
  await sleep(5);
  await fs.writeFile(`/tmp/${avd.uuid}-post.png`, await avd.screenShot());
  screenshotLogger.info("post");
};

export const start = async () => {
  if (!process.env.JOB_ID) {
    logger.error("JOB_ID is missing from environment");
    process.exit(1);
  }

  const uid = process.env.JOB_ID;
  const apkPath = path.join("/tmp", uid + ".apk");
  await waitApk(apkPath);

  // await fs.writeFile(apkPath, file);
  const avd = new AVD(uid);

  try {
    userLogger.info("Lancement de l'AVD ..."); // socket.emit
    const pleaseWait = setInterval(
      () =>
        userLogger.info("Merci de patienter, le lancement peut être long ..."),
      10000
    );
    await avd.start();
    userLogger.info("L'AVD est démarré !"); // socket.emit
    clearInterval(pleaseWait);

    userLogger.info("En attente de ADB ..."); // socket.emit
    await avd.adbListen();

    await checkExploit(avd, apkPath, line => userLogger.info(line));
  } catch (err) {
    logger.error(err);
    userLogger.info("Une erreur est survenue !"); // socket.emit
  } finally {
    userLogger.info("Arrêt de l'AVD ..."); // socket.emit
    await avd.stop();
    userLogger.info("AVD arrêté."); // socket.emit
    userLogger.info("Arrêt de ADB ..."); // socket.emit
    await avd.adbStop();
    userLogger.info("ADB arrêté."); // socket.emit
    logger.info("DONE");
    await sleep(60);
  }
};
