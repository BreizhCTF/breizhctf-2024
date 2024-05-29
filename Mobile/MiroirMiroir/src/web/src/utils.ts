import * as cp from "child_process";

export const sleep = (timeS: number) =>
  new Promise((resolve) =>
    setTimeout(() => {
      resolve(null);
    }, timeS * 1e3)
  );
export const runCommand = (
  cmd: string,
  args: string[],
  output?: (data: string) => any
): Promise<number> => {
  return new Promise((resolve) => {
    const proc = cp.spawn(cmd, args, { shell: false });
    proc.stdout.setEncoding("utf-8");
    proc.stderr.setEncoding("utf-8");

    proc.stdin.write("no\n");
    proc.stdout.on("data", (data: string) => {
      console.log(data);
      if (output) {
        output(data);
      }
    });
    proc.stderr.on("data", (data: string) => {
      console.error(data);
      if (output) {
        output(data);
      }
    });

    proc.on("exit", (code) => resolve(code ?? -1));
  });
};

export const getApkMain = async (apk: string): Promise<string> => {
  return await new Promise((resolve, reject) => {
    cp.execFile(
      "/opt/Android/build-tools/34.0.0/aapt2",
      ["dump", "badging", apk],
      (err, stdout, stderr) => {
        const match = stdout.match(
          /launchable-activity: name='([\w.]+)'/i
        )?.[1];
        if (!match) {
          reject("Unable to find MainActivity");
          return;
        }
        const activity = [match.split(".").slice(0, -1).join("."), match].join(
          "/"
        );
        resolve(activity);
      }
    );
  });
};
