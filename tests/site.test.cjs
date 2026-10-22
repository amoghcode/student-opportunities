const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Supply only the startup DOM; exercise the actual status and filter functions.
function app() {
  const nodes = new Map();
  const context = vm.createContext({
    console,
    document: {
      querySelector(selector) {
        if (!nodes.has(selector)) nodes.set(selector, {
          value: "", addEventListener() {}, replaceChildren() {},
        });
        return nodes.get(selector);
      },
      addEventListener() {},
    },
    fetch: async () => ({ ok: true, json: async () => [] }),
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, "../site/app.js"), "utf8"), context);
  return { context, nodes, run: (code) => vm.runInContext(code, context) };
}

test("future deadline without opening date never claims applications are open", () => {
  const { context, run } = app();
  context.record = { lifecycle: "active", schedule: { cycles: [{ deadline: "2026-11-15" }] } };
  assert.equal(run('getStatus(record, new Date("2026-10-22T12:00:00Z")).key'), "uncertain");
});

test("deadline boundaries follow the program timezone", () => {
  const { context, run } = app();
  context.record = { lifecycle: "active", schedule: {
    timezone: "Asia/Kolkata", cycles: [{ opens_on: "2026-10-01", deadline: "2026-10-22", deadline_time: "17:00" }],
  } };
  assert.equal(run('getStatus(record, new Date("2026-10-22T11:30:00Z")).key'), "open");
  assert.equal(run('getStatus(record, new Date("2026-10-22T11:31:00Z")).key'), "closed");
});

test("future cycles and paused rolling programs retain their status", () => {
  const { context, run } = app();
  context.record = { lifecycle: "active", schedule: { cycles: [{ opens_on: "2027-01-01" }] } };
  assert.equal(run('getStatus(record, new Date("2026-10-22T12:00:00Z")).key'), "upcoming");
  context.record = { lifecycle: "paused", schedule: { type: "rolling" } };
  assert.equal(run("getStatus(record).key"), "paused");
});

test("India filter includes global opportunities and excludes other country-only records", () => {
  const { context, nodes, run } = app();
  nodes.get("#eligibility-filter").value = "India";
  context.record = { eligibility_geographies: [{ scope: "global", values: [] }] };
  assert.equal(run("matches(record)"), true);
  context.record = { eligibility_geographies: [{ scope: "country", values: ["Canada"] }] };
  assert.equal(run("matches(record)"), false);
});

test("subject filter handles spaces, hyphens, and explicitly all-field records", () => {
  const { context, nodes, run } = app();
  nodes.get("#field-filter").value = "computer-science";
  for (const fields of [["computer science"], ["computer-science"], ["all-fields"]]) {
    context.record = { fields };
    assert.equal(run("matches(record)"), true);
  }
  context.record = { fields: ["biology"] };
  assert.equal(run("matches(record)"), false);
  assert.equal(run('uniqueValues([{fields:["life sciences", "life-sciences"]}], fieldValues).length'), 1);
});

test("any-student matches enrolled study levels without implying graduate eligibility", () => {
  const { context, nodes, run } = app();
  context.record = { student_levels: ["any-student"] };
  nodes.get("#level-filter").value = "undergraduate";
  assert.equal(run("matches(record)"), true);
  nodes.get("#level-filter").value = "recent-graduate";
  assert.equal(run("matches(record)"), false);
});
