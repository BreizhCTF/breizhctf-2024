import { start as startWebserver } from "./apps/web";
import { start as startRunner } from "./apps/runner";

switch (process.argv.at(-1)) {
  case "runner":
    startRunner();
    break;

  case "web":
  default:
    startWebserver();
    break;
}
