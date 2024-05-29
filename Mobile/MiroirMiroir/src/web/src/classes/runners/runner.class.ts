import { Readable } from "stream";
import winston from 'winston';

export abstract class Runner {
  protected readonly logger = winston.createLogger({
    format: winston.format.prettyPrint(),
    transports: [new winston.transports.Console()]
  });

  public onUserLog?: (message: string) => any;
  public onScreenshot?: (type: 'pre' | 'post', file: Buffer) => any;
  public onKilled?: () => any;

  constructor(public readonly uid: string) {}

  abstract start(): Promise<void>;

  abstract pushApk(file: Buffer): Promise<void>;

  abstract kill(): Promise<void>;
}
