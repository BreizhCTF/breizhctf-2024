import * as path from "path";
import { writeFile } from "fs/promises";
import { PassThrough } from "stream";
import readline from "readline";

import { WritableStreamBuffer } from "stream-buffers";
import * as k8s from "@kubernetes/client-node";
import type { Request } from "request";

import { Runner } from "./runner.class";
import { sleep } from "../../utils";

export class KubernetesRunner extends Runner {
  private namespace = process.env.TARGET_NAMESPACE ?? "miroir-miroir";

  private kubeconfig = new k8s.KubeConfig();

  private readonly kubeLog = new k8s.Log(this.kubeconfig);
  private readonly batchApi: k8s.BatchV1Api;
  private readonly coreApi: k8s.CoreV1Api;

  private job?: k8s.V1Job;
  private pod?: k8s.V1Pod;
  private logRequest?: Request;

  constructor(uid: string) {
    super(uid);
    this.kubeconfig.loadFromDefault();
    this.batchApi = this.kubeconfig.makeApiClient(k8s.BatchV1Api);
    this.coreApi = this.kubeconfig.makeApiClient(k8s.CoreV1Api);
  }

  /**
   * Start the kubernetes job and wait for the pod to be ready
   */
  async start(): Promise<void> {
    // Create a job and wait for the pod to be runing
    this.logger.info("Creating kubernetes job");
    this.job = await this.createJob();
    this.pod = await this.findPod(this.job);
    this.logger.info("Found associated pod", { pod: this.pod.metadata?.name });

    // Setup log parsing
    this.logger.info("Starting log streaming");
    const logStream = new PassThrough();
    const lineStream = readline.createInterface(logStream);
    lineStream.on("line", (line) => this.parseLine(line));

    this.logRequest = await this.kubeLog.log(
      this.namespace,
      this.pod.metadata!.name!,
      "avd",
      logStream,
      {
        follow: true,
        pretty: false,
        timestamps: false,
      }
    );
  }

  /**
   * Copy APK to remote pod
   */
  async pushApk(file: Buffer): Promise<void> {
    const copy = new k8s.Cp(this.kubeconfig);
    const apkPath = path.join(path.join("/tmp", this.uid + ".apk"));
    this.logger.info(`Pushing APK ${apkPath} into pod filesystem`);

    await writeFile(apkPath, file);
    await copy.cpToPod(
      this.namespace,
      this.pod!.metadata!.name!,
      "avd",
      this.uid + ".apk",
      "/tmp",
      "/tmp"
    );
    this.logger.info("APK pushed successfully");
  }

  /**
   * Stop kubernetes job and remove pod
   */
  async kill(): Promise<void> {
    this.logger.warn("Killing kubernetes pod+job");
    this.logRequest?.abort();
    if (this.pod?.metadata?.name) {
      await this.coreApi.deleteNamespacedPod(
        this.pod!.metadata!.name!,
        this.namespace
      );
    }

    if (this.job?.metadata?.name) {
      await this.batchApi.deleteNamespacedJob(
        this.job!.metadata!.name!,
        this.namespace
      )
    }

    if (this.onKilled) {
      this.onKilled();
    }
  }

  /**
   * Create a new kubernetes job runing the AVD
   * @returns The newly create job
   */
  private async createJob(): Promise<k8s.V1Job> {
    const jobName = `avd-${this.uid}`;

    const jobResponse = await this.batchApi.createNamespacedJob(this.namespace, {
      metadata: {
        name: jobName,
        namespace: this.namespace,
        annotations: {
          "janitor/ttl": "10m",
        },
        labels: {
          uid: this.uid,
        },
      },
      spec: {
        ttlSecondsAfterFinished: 60,
        backoffLimit: 0,
        template: {
          spec: {
            restartPolicy: "Never",
            terminationGracePeriodSeconds: 1,
            containers: [
              {
                name: "avd",
                image:
                  "registry-bzh.alfred.cafe/breizh-ctf-2024/challenges/miroirmiroir:latest",
                args: ["index.js", "runner"],
                env: [
                  {
                    name: "JOB_ID",
                    value: this.uid,
                  },
                ],
                securityContext: {
                  allowPrivilegeEscalation: false,
                  capabilities: {
                    drop: ["ALL"],
                  },
                  privileged: false,
                  runAsNonRoot: true,
                  runAsUser: 666,
                  runAsGroup: 103,
                  seccompProfile: {
                    type: "RuntimeDefault",
                  },
                },
                resources: {
                  requests: {
                    memory: "3Gi", // QEMU uses ~3Gi
                    cpu: "1000m",
                  },
                  limits: {
                    memory: "4Gi", // Limit to 4Gi to prevent OOM Killer
                    cpu: "1000m",
                    "ephemeral-storage": "2Gi",
                    "squat.ai/kvm": "1", // Request for /dev/kvm device
                  },
                },
              },
            ],
            imagePullSecrets: [{ name: "docker-registry-secret" }], // Docker registry secret
            nodeSelector: {
              // This should not be required since /dev/kvm is only available on chall7
              // but we are never too safe
              challs: "android", 
            },
            enableServiceLinks: false,
            automountServiceAccountToken: false,
          },
        },
      },
    });

    return jobResponse.body;
  }

  /**
   * Find the pod associated to a job a wait for the pod to be running
   * @returns The running pod associated to the job
   */
  private async findPod(job: k8s.V1Job): Promise<k8s.V1Pod> {
    for (let i = 0; i < 60; i++) {
      const pods = await this.coreApi.listNamespacedPod(
        this.namespace,
        undefined,
        undefined,
        undefined,
        undefined,
        "job-name=" + job.metadata?.name
      );
      if (pods.body.items.length > 1) {
        throw new Error("Found more than one pod");
      } else if (pods.body.items.length === 1) {
        if (pods.body.items.at(0)?.status?.containerStatuses?.at(0)?.ready) {
          return pods.body.items.pop() as k8s.V1Pod;
        } else {
          this.logger.info("Pod has not started yet");
        }
      }
      await sleep(1);
    }
    throw new Error("Timeout while waiting for pod to show up");
  }

  /**
   * Copy a pre-install or post-install screenshot of the AVD
   * @param type Type of screenshot
   * @returns A buffer containing the raw PNG
   */
  private async pullScreenshot(type: "post" | "pre"): Promise<Buffer> {
    const exec = new k8s.Exec(this.kubeconfig);
    const pngPath = path.join("/tmp", `${this.uid}-${type}.png`);

    const writerStream = new WritableStreamBuffer();
    const png: Buffer = await new Promise((resolve, reject) => exec.exec(
      this.namespace,
      this.pod!.metadata!.name!,
      'avd',
      ["cat", pngPath],
      writerStream,
      null,
      null,
      false,
      async ({ status }) => {
        if (status === "Failure") {
          reject(
            `Error from cpFromPod`
          );
        }
        resolve(writerStream.getContents() as Buffer);
      }
    ));
    
    return png;
  }

  /**
   * Parse log lines issued by the pod and call associated callback functions
   * @param line The log line to parse
   */
  private async parseLine(line: string) {
    try {
      const log = JSON.parse(line);

      switch (log.scope) {
        case "user":
          this.logger.info("User log received", { message: log.message });
          if (this.onUserLog) {
            this.onUserLog(log.message);
          }
          break;

        case "screenshot":
          const type: string = log.message;
          this.logger.info("Screenshot received", { type });
          if (this.onScreenshot && (type === "pre" || type === "post")) {
            this.onScreenshot(type, await this.pullScreenshot(type));
          }
          break;
      }
    } catch (error) {
      if (!(error instanceof SyntaxError)) {
        this.logger.error(error);
        this.kill();
      }
    }
  }
}
