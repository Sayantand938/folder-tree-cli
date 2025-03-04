import { program } from "commander";
import { generateTreeCommand } from "./commands/generateTree.js";

function run() {
  program
    .name("folder-tree-cli")
    .version("1.0.0")
    .description("A CLI tool to generate folder trees.");

  generateTreeCommand(program);

  program.parse(process.argv);
}

export { run };
