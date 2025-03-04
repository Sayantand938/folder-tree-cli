import fs from "fs";
import path from "path";
import fg from "fast-glob";
import archy from "archy";
import chalk from "chalk";
import { Command } from "commander";

const EXCLUDED_FOLDERS = ["node_modules", "__pycache__", ".git"];

/**
 * @typedef {Object} TreeNode
 * @property {string} label - Display name of the node
 * @property {TreeNode[]} nodes - Child nodes
 */

/**
 * @typedef {Object} Options
 * @property {string} path - Directory path to scan
 * @property {number} [depth] - Maximum recursion depth
 * @property {string} [ignore] - Pattern to ignore files/folders
 */

/**
 * Builds a tree structure from a directory.
 * @param {string} dir - Directory path to scan
 * @param {Options} options - Configuration options
 * @param {number} depth - Current recursion depth
 * @returns {Promise<TreeNode[]>} Array of tree nodes
 */
async function buildTree(dir, options, depth = 0) {
  if (options.depth !== undefined && depth > options.depth) return [];

  try {
    const entries = await fs.promises.readdir(dir, { withFileTypes: true });

    const nodes = await Promise.all(
      entries.map(async (entry) => {
        if (EXCLUDED_FOLDERS.includes(entry.name)) return null;
        if (options.ignore && new RegExp(options.ignore).test(entry.name))
          return null;

        const fullPath = path.join(dir, entry.name);
        const isDir = entry.isDirectory();

        const node = {
          label: isDir
            ? chalk.hex("#DAA520").bold(entry.name) + "/"
            : entry.name,
          nodes: [],
        };

        if (isDir) {
          try {
            node.nodes = await buildTree(fullPath, options, depth + 1);
          } catch (err) {
            console.error(
              chalk.red(`Error reading ${entry.name}: ${err.message}`)
            );
          }
        }

        return node;
      })
    );

    return nodes.filter(Boolean).sort((a, b) => a.label.localeCompare(b.label));
  } catch (err) {
    console.error(
      chalk.red(`Failed to read directory '${dir}': ${err.message}`)
    );
    return [];
  }
}

/**
 * Generates and displays a directory tree.
 * @param {import('commander').Command} parentProgram - Commander program instance
 */
function generateTreeCommand(parentProgram) {
  parentProgram
    .option("-p, --path <path>", "The path to generate the tree from", ".")
    .option(
      "-d, --depth <number>",
      "Maximum depth of the tree",
      (val) => parseInt(val, 10),
      undefined
    )
    .option("-i, --ignore <pattern>", "Ignore files/folders matching a pattern")
    .action(async (options) => {
      try {
        const startDir = path.resolve(options.path);
        await fs.promises.access(startDir, fs.constants.R_OK);

        const treeData = {
          label: path.basename(startDir),
          nodes: await buildTree(startDir, options),
        };

        console.log(chalk.green(`Project Root Directory: ${startDir}`));
        console.log(archy(treeData));
      } catch (err) {
        console.error(chalk.red(`Error: ${err.message}`));
        process.exit(1);
      }
    });
}

export { generateTreeCommand, buildTree };
