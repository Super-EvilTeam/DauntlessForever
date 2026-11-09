// Dauntless Forever - launcher dev runner
// Licence: AGPL-3.0-only
'use strict';
process.env.DL_MOCK = '1';
const { spawn } = require('child_process');
const electron = require('electron');
const child = spawn(electron, ['.'], { stdio: 'inherit', windowsHide: false });
child.on('close', (code) => process.exit(code || 0));
