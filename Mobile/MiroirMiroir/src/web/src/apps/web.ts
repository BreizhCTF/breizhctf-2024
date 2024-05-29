import path from "path";
import http from "http";
import express from "express";
import { v4 as uuid } from "uuid";
import { Socket, Server as SocketServer } from "socket.io";
import { createChallenge, verifySolution } from "altcha-lib";

import { Runner } from "../classes/runners/runner.class";
import { KubernetesRunner } from "../classes/runners/kubernetes.runner";
import { LocalRunner } from "../classes/runners/LocalRunner.runner";

const app = express();
const server = http.createServer(app);
const io = new SocketServer(server, { maxHttpBufferSize: 1e8 });

let captchaVerified = false;
let runner: Runner | undefined;

const createRunner = (uid: string, socket: Socket) => {
  const type = process.env.RUNNER ?? "local";
  switch (type) {
    case "kubernetes":
      return new KubernetesRunner(uid);

    case "local":
    default:
      return new LocalRunner(uid, socket);
  }
};

app.use(express.static(path.join(path.dirname(__dirname), "static")));

app.get("/", (_req, res) => {
  res.sendFile(path.join(path.dirname(__dirname), "templates", "index.html"));
});

io.on("connection", (socket) => {
  console.log("New socket");

  socket.on("getCaptcha", async (callback) => {
    const challenge = await createChallenge({
      hmacKey: "ABCDEF",
    });
    callback(challenge);
  });

  socket.on("submitCaptcha", async (captcha, callback) => {
    captchaVerified = await verifySolution(captcha, "ABCDEF");
    callback(captchaVerified);
  });

  socket.on("submitApk", async (file, callback) => {
    if (!captchaVerified) {
      socket.emit("log", "Captcha has not been verified");
      return;
    }
    captchaVerified = false;

    if (runner) {
      socket.emit("log", "Another AVD is already runing");
      return;
    }

    socket.emit(
      "log",
      "Allocation des ressources pour l'AVD, cela peu être plus ou moins rapide en fonction de la charge des serveurs"
    );

    const uid = uuid();
    runner = createRunner(uid, socket);
    runner.onKilled = () => {
      console.log("On Killed");
      runner = undefined;
      callback();
    };

    try {
      runner.onUserLog = (message) => socket.emit("log", message);
      runner.onScreenshot = (type, file) => {
        socket.emit(`${type}-screenshot`, file);

        if (type === "post") {
          runner?.kill();
        }
      };

      await runner.start();
      socket.emit("log", "Conteneur lancé ! Démarrage de l'AVD ...")

      await runner.pushApk(file);
    } catch (error) {
      console.error(error);
      try {
        runner?.kill();
      } catch {}
    }

    console.log("DONE");
  });
});

export const start = () => {
  server
    .listen(3000, () => {
      console.log("Express is listening on port 3000");
    })
    .on("error", (err: Error) => {
      console.error(err);
    });
};

process.on("SIGINT", async () => {
  try {
    await runner?.kill();
  } catch {}
  process.exit(0);
});

process.on("SIGTERM", async () => {
  try {
    await runner?.kill();
  } catch {}
  process.exit(0);
});

process.on("uncaughtException", async (err) => {
  console.log(err);
  try {
    await runner?.kill();
  } catch {}
  process.exit(1);
});

process.on("unhandledRejection", async (err) => {
  console.log(err);
  try {
    await runner?.kill();
  } catch {}
  process.exit(1);
});
