import cp, { ChildProcessWithoutNullStreams } from "child_process";
import { runCommand } from "../utils";

export class AVD {
  public proc?: ChildProcessWithoutNullStreams;

  constructor(public readonly uuid: string) { }

  public async start(): Promise<void> {
    return new Promise((resolve) => {
      this.proc = cp.spawn(
        "emulator",
        [
          "-avd",
          "challenge_avd",
          "-port",
          "5556",
          "-no-window",
          "-no-audio",
          "-no-boot-anim",
          "-snapshot",
          "post_setup",
        ],
        { stdio: "pipe" }
      );
      this.proc.stdout.setEncoding("utf-8");
      this.proc.stderr.setEncoding("utf-8");

      this.proc.stdin.write("no\n");
      this.proc.stdout.on("data", (data: string) => {
        console.log(data);
        if (data.includes("Successfully loaded snapshot")) {
          resolve();
        }
      });
      this.proc.stderr.on("data", (data: string) => {
        console.error(data);
      });
    });
  }

  public stop() {
    return new Promise((resolve, reject) => {
      if (!this.proc) {
        return reject("Process is not running");
      }
      if (!this.proc.pid) {
        return reject("Emulator is not running");
      }
      this.proc.once("exit", (code) => resolve(code));
      this.proc.kill("SIGKILL");
    });
  }

  public async adbListen(): Promise<void> {
    await runCommand("adb", ["start-server"]);
    console.log("ADB started");

    console.log("Waiting for AVD to be available ...");
    await runCommand("adb", [
      "wait-for-device",
      "shell",
      "while [ -z $(getprop sys.boot_completed) ]; do sleep 1; done;",
    ]);
    console.log("AVD is available");
  }

  public async adbStop(): Promise<void> {
    await runCommand("adb", ["kill-server"]);
  }

  public async screenShot(): Promise<Buffer> {
    return new Promise((resolve) => {
      cp.execFile(
        "adb",
        ["exec-out", "screencap", "-p"],
        { encoding: "buffer" },
        (_err, stdout: Buffer, _stderr) => resolve(stdout)
      );
    });
  }
}
