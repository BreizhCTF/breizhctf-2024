import * as path from "path";

import { AVD } from "../avd.class";
import { Runner } from "./runner.class";
import { checkExploit } from "../../apps/runner";
import { readFile, writeFile } from "fs/promises";
import { Socket } from "socket.io";

export class LocalRunner extends Runner {
  public avd?: AVD;
  public onUserLog?: (message: string) => any;

  constructor(uid: string, private readonly socket: Socket) {
    super(uid);
  }

  async start(): Promise<void> {
    this.avd = new AVD(this.uid);
    await this.avd.start();
    await this.avd.adbListen();
  }

  async pushApk(file: Buffer): Promise<void> {
    if (!this.avd) {
      throw new Error("AVD has not started");
    }

    const apkPath = path.join("/tmp", `${this.uid}.apk`);

    await writeFile(apkPath, file);
    await checkExploit(this.avd, apkPath, (line) =>
      this.socket.emit("log", line)
    );
    if (this.onScreenshot) {
        this.onScreenshot('pre', await readFile(path.join("/tmp", `${this.uid}-pre.png`)));
        this.onScreenshot('post', await readFile(path.join("/tmp", `${this.uid}-post.png`)));
    }
  }

  async kill(): Promise<void> {
    await this.avd?.stop();
    await this.avd?.adbStop();

    if (this.onKilled) {
      this.onKilled();
    }
  }
}
