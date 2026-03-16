"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// mcp/cdk/lambda/index.ts
var lambda_exports = {};
__export(lambda_exports, {
  lambdaHandler: () => lambdaHandler
});
module.exports = __toCommonJS(lambda_exports);
var import_promises = require("node:stream/promises");
var import_node_stream = require("node:stream");
var lambdaHandler = awslambda.streamifyResponse(
  async (event, responseStream, _context) => {
    const metadata = {
      statusCode: 200,
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8"
      }
    };
    responseStream = awslambda.HttpResponseStream.from(responseStream, metadata);
    const readable = import_node_stream.Readable.from([
      "DB\u306E\u5185\u5BB9\u3067\u3059\n",
      "2026-03-01T10:00:00+09:00 1\u4EF6\n",
      "2026-03-02T11:00:00+09:00 3\u4EF6\n",
      "2026-03-03T13:00:00+09:00 1\u4EF6\n"
    ]);
    await (0, import_promises.pipeline)(readable, responseStream);
  }
);
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  lambdaHandler
});
//# sourceMappingURL=index.js.map
