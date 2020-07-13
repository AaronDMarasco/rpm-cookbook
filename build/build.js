#!/usr/bin/env node
'use strict';

var markdownInclude = require('markdown-include');

// Allow this script to be called from own directory or top-level
try {
  process.chdir('build');
}
catch (x) {}

// Add "fake" plugin w/ comment leader...
markdownInclude.registerPlugin(/^#comment.*$/gm, function (tag) {
	return '';
});

markdownInclude.compileFiles("markdown.json").then(function () {
	console.info(markdownInclude.options.build + ' built successfully');
});
