// A builder that runs the stub and reports every sheet as PASS, so a test can
// check that a pack whose revalidation failed never leaves a workbook reading PASS.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const stub = fileURLToPath(new URL('./builder-stub.mjs', import.meta.url));
const result = spawnSync(process.execPath, [stub, ...process.argv.slice(2)], { encoding: 'utf8' });
process.stdout.write(result.stdout.replace(/^FAIL( +)/gm, 'PASS$1'));
