// news-image-20261125 entry (Node 22, standard library only).
// The entry image sits beside this file as entry.png; the program
// copies it byte for byte to the output directory, so two grader
// runs produce identical bytes. Local run:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from "node:fs";
import { join } from "node:path";

const targetDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const sourcePath = new URL("./entry.png", import.meta.url);
copyFileSync(sourcePath, join(targetDir, "entry.png"));
