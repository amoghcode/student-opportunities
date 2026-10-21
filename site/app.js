"use strict";

const filters = document.querySelector("#filters");
const searchInput = document.querySelector("#search-input");
const results = document.querySelector("#results");
const summary = document.querySelector("#results-summary");
const emptyState = document.querySelector("#empty-state");
const loadError = document.querySelector("#load-error");
const categoryFilter = document.querySelector("#category-filter");
const levelFilter = document.querySelector("#level-filter");
const fieldFilter = document.querySelector("#field-filter");
const eligibilityFilter = document.querySelector("#eligibility-filter");
const deliveryFilter = document.querySelector("#delivery-filter");
const statusFilter = document.querySelector("#status-filter");
const sortFilter = document.querySelector("#sort-filter");
const totalCount = document.querySelector("#total-count");
const openCount = document.querySelector("#open-count");

let opportunities = [];
const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

function humanize(value) {
  return String(value || "").replace(/[-_]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function uniqueValues(records, getter) {
  return [...new Set(records.flatMap(getter).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function fieldValues(record) {
  return (record.fields || []).map((value) => value.trim().toLowerCase().replace(/[\s_]+/g, "-"));
}

function addOptions(select, values, labelFor = humanize) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = labelFor(value);
    select.append(option);
  }
}

function geographies(record) {
  const entries = record.eligibility_geographies || record.geographies || [];
  return entries.flatMap((entry) => {
    if (entry.scope === "global") return ["Worldwide"];
    return entry.values || [];
  });
}

function localDateTime(timeZone, instant = new Date()) {
  const zone = timeZone || "UTC";
  try {
    const parts = new Intl.DateTimeFormat("en-GB", {
      timeZone: zone,
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23",
    }).formatToParts(instant);
    const part = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
    return `${part.year}-${part.month}-${part.day}T${part.hour}:${part.minute}`;
  } catch {
    return instant.toISOString().slice(0, 16);
  }
}

function cyclePhase(cycle, timeZone, nowText) {
  const opening = cycle.opens_on ? `${cycle.opens_on}T00:00` : null;
  const closing = cycle.deadline
    ? `${cycle.deadline}T${cycle.deadline_time || "23:59"}`
    : null;

  if (opening && nowText < opening) return "upcoming";
  if (opening && (!closing || nowText <= closing)) return "open";
  if (closing && nowText <= closing) return "uncertain";
  if (closing && nowText > closing) return "closed";
  return "uncertain";
}

function getStatus(record, instant = new Date()) {
  const lifecycle = record.lifecycle || "unknown";
  if (lifecycle !== "active") {
    const label = {
      paused: "Program paused",
      discontinued: "Program ended",
      archived: "Archived program",
      unknown: "Program status unknown",
    }[lifecycle] || "Program status unknown";
    return { key: lifecycle, label, dateText: record.lifecycle_note || "Check the official page for current details.", deadline: null };
  }

  const schedule = record.schedule || {};
  if (schedule.type === "rolling") {
    return { key: "rolling", label: "Rolling applications", dateText: "No fixed deadline listed", deadline: null };
  }

  const cycles = schedule.cycles || [];
  const nowText = localDateTime(schedule.timezone, instant);
  const classified = cycles.map((cycle) => ({
    cycle,
    phase: cyclePhase(cycle, schedule.timezone, nowText),
  }));
  const open = classified.find((item) => item.phase === "open");
  const upcoming = classified
    .filter((item) => item.phase === "upcoming")
    .sort((a, b) => a.cycle.opens_on.localeCompare(b.cycle.opens_on))[0];
  const uncertain = classified
    .filter((item) => item.phase === "uncertain")
    .sort((a, b) => (a.cycle.deadline || "9999").localeCompare(b.cycle.deadline || "9999"))[0];
  const futureDeadline = classified
    .filter((item) => item.cycle.deadline && `${item.cycle.deadline}T${item.cycle.deadline_time || "23:59"}` >= nowText)
    .sort((a, b) => a.cycle.deadline.localeCompare(b.cycle.deadline))[0];

  if (open) {
    return {
      key: "open",
      label: "Open by recorded dates",
      dateText: open.cycle.deadline ? `Deadline ${formatDate(open.cycle.deadline)}${formatTime(open.cycle, schedule.timezone)}` : "Opening date is recorded; deadline not announced",
      deadline: open.cycle.deadline || null,
    };
  }

  // A future deadline alone does not prove that applications have opened.
  if (uncertain) {
    return {
      key: "uncertain",
      label: "Dates not fully confirmed",
      dateText: uncertain.cycle.deadline ? `Deadline ${formatDate(uncertain.cycle.deadline)}; opening date not confirmed` : "Application dates are not confirmed",
      deadline: uncertain.cycle.deadline || null,
    };
  }

  if (upcoming) {
    return {
      key: "upcoming",
      label: "Opening date announced",
      dateText: `Opens ${formatDate(upcoming.cycle.opens_on)}`,
      deadline: upcoming.cycle.deadline || null,
    };
  }

  if (cycles.length && classified.every((item) => item.phase === "closed")) {
    const last = classified
      .filter((item) => item.cycle.deadline)
      .sort((a, b) => b.cycle.deadline.localeCompare(a.cycle.deadline))[0];
    return {
      key: "closed",
      label: "Recorded cycle closed",
      dateText: last ? `Last deadline ${formatDate(last.cycle.deadline)}` : "No current application cycle listed",
      deadline: null,
    };
  }

  const typicalMonths = schedule.typical_open_months || [];
  if (typicalMonths.length) {
    const months = typicalMonths.map((month) => monthNames[month - 1]).filter(Boolean).join(", ");
    return { key: "uncertain", label: "Dates not announced", dateText: `Usually opens in ${months}; check the official page`, deadline: null };
  }

  return { key: "uncertain", label: "Dates not announced", dateText: "Check the official page for the next cycle", deadline: futureDeadline?.cycle.deadline || null };
}

function formatDate(value) {
  if (!value) return "Date not announced";
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" })
    .format(new Date(Date.UTC(year, month - 1, day)));
}

function formatTime(cycle, timeZone) {
  if (!cycle.deadline_time) return "";
  const zoneLabel = timeZone ? ` ${timeZone}` : "";
  return ` at ${cycle.deadline_time}${zoneLabel}`;
}

function locationText(record) {
  const locations = record.locations || [];
  if (!locations.length) {
    if (record.delivery === "remote") return "Remote";
    if (["hybrid", "varies"].includes(record.delivery)) return "Varies by program";
    return "Location not listed";
  }
  const values = locations.flatMap((item) => item.scope === "global" ? ["Worldwide"] : (item.values || []));
  return values.length ? [...new Set(values)].join(", ") : "Location varies";
}

function eligibilityText(record) {
  return record.eligibility_summary || geographies(record).join(", ") || "Check official eligibility details";
}

function feeText(record) {
  const fee = record.application_fee;
  if (!fee) return "Fee details not listed";
  if (fee.required === false) return "No application fee";
  if (fee.required === true && fee.amount != null) return `Application fee: ${fee.currency || ""} ${fee.amount}`.trim();
  if (fee.required === true) return "An application fee is required";
  return "Application fee not confirmed";
}

function allSearchText(record) {
  return [
    record.name, record.organization, record.description, record.eligibility_summary,
    record.benefits?.summary, record.notes, ...(record.categories || []),
    ...(record.student_levels || []), ...(record.fields || []), ...(record.tags || []),
    ...geographies(record), locationText(record),
  ].filter(Boolean).join(" ").toLocaleLowerCase();
}

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text != null) element.textContent = text;
  return element;
}

function appendDetail(parent, label, value, extraClass = "") {
  const wrap = createElement("div", `detail-item ${extraClass}`.trim());
  wrap.append(createElement("dt", "", label), createElement("dd", "", value));
  parent.append(wrap);
  return wrap;
}

function createCard(record) {
  const status = getStatus(record);
  const card = createElement("article", "opportunity-card");
  const topline = createElement("div", "card-topline");
  const tags = createElement("div", "tag-list");
  for (const category of (record.categories || []).slice(0, 2)) {
    tags.append(createElement("span", "category-tag", humanize(category)));
  }
  const statusTag = createElement("span", `status-tag is-${status.key}`, status.label);
  topline.append(tags, statusTag);

  const heading = createElement("h3", "", record.name || "Untitled opportunity");
  const organization = createElement("p", "organization", record.organization || "Organization not listed");
  const description = createElement("p", "card-description", record.description || "No summary provided.");

  const details = createElement("dl", "detail-grid");
  appendDetail(details, "Who can apply", eligibilityText(record));
  appendDetail(details, "Location", locationText(record));
  appendDetail(details, "Support", record.benefits?.summary || "Details not listed");
  const timing = appendDetail(details, "Application timing", status.dateText);
  if (status.key === "uncertain" && /opening date not confirmed|dates are not confirmed/i.test(status.dateText)) {
    timing.querySelector("dd").append(createElement("span", "date-caveat", "Not labelled open because a start date is missing."));
  }
  appendDetail(details, "Application fee", feeText(record));

  const bottom = createElement("div", "card-bottom");
  const verified = createElement("span", "verified-date", record.last_verified ? `Source checked ${formatDate(record.last_verified)}` : "Verification date not listed");
  const link = document.createElement("a");
  link.className = "official-link";
  link.href = record.application_url || record.official_url || "#";
  link.rel = "noopener noreferrer";
  link.append(document.createTextNode(record.application_url ? "Go to application" : "Official program page"), createElement("span", "", "↗"));
  bottom.append(verified, link);

  card.append(topline, heading, organization, description, details, bottom);
  return card;
}

function selectedMatches(record, select, values) {
  if (!select.value) return true;
  return values.includes(select.value);
}

function matches(record) {
  const query = searchInput.value.trim().toLocaleLowerCase();
  const searchMatch = !query || allSearchText(record).includes(query);
  const status = getStatus(record);
  return searchMatch
    && selectedMatches(record, categoryFilter, record.categories || [])
    && (selectedMatches(record, levelFilter, record.student_levels || [])
      || (["secondary-school", "undergraduate", "postgraduate", "doctoral"].includes(levelFilter.value)
        && (record.student_levels || []).includes("any-student")))
    && (selectedMatches(record, fieldFilter, fieldValues(record)) || fieldValues(record).includes("all-fields"))
    && (selectedMatches(record, eligibilityFilter, geographies(record)) || geographies(record).includes("Worldwide"))
    && selectedMatches(record, deliveryFilter, [record.delivery || ""])
    && (!statusFilter.value || status.key === statusFilter.value);
}

function deadlineForSort(record) {
  const today = localDateTime(record.schedule?.timezone).slice(0, 10);
  const dates = (record.schedule?.cycles || [])
    .map((cycle) => cycle.deadline)
    .filter((date) => date && date >= today)
    .sort();
  return dates[0] || "9999-12-31";
}

function render() {
  const filtered = opportunities.filter(matches);
  if (sortFilter.value === "name") {
    filtered.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  } else if (sortFilter.value === "verified") {
    filtered.sort((a, b) => (b.last_verified || "").localeCompare(a.last_verified || ""));
  } else {
    filtered.sort((a, b) => deadlineForSort(a).localeCompare(deadlineForSort(b)) || (a.name || "").localeCompare(b.name || ""));
  }

  results.replaceChildren(...filtered.map(createCard));
  summary.textContent = `Showing ${filtered.length} of ${opportunities.length} opportunities`;
  emptyState.hidden = filtered.length !== 0;
}

function resetFilters() {
  filters.reset();
  render();
  searchInput.focus();
}

function setupFilters() {
  addOptions(categoryFilter, uniqueValues(opportunities, (record) => record.categories || []));
  addOptions(levelFilter, uniqueValues(opportunities, (record) => record.student_levels || []));
  addOptions(fieldFilter, uniqueValues(opportunities, fieldValues));
  addOptions(eligibilityFilter, uniqueValues(opportunities, geographies));
  addOptions(deliveryFilter, uniqueValues(opportunities, (record) => [record.delivery].filter(Boolean)));
}

async function start() {
  try {
    const response = await fetch("./opportunities.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load opportunity data (${response.status}).`);
    opportunities = await response.json();
    if (!Array.isArray(opportunities)) throw new Error("Opportunity data has the wrong format.");
    setupFilters();
    totalCount.textContent = String(opportunities.length);
    openCount.textContent = String(opportunities.filter((record) => getStatus(record).key === "open").length);
    render();
  } catch (error) {
    console.error(error);
    summary.textContent = "Opportunity list unavailable";
    loadError.hidden = false;
    results.hidden = true;
  }
}

filters.addEventListener("input", render);
filters.addEventListener("submit", (event) => event.preventDefault());
filters.addEventListener("change", render);
filters.addEventListener("reset", () => requestAnimationFrame(render));
document.querySelector("#reset-filters").addEventListener("click", (event) => {
  event.preventDefault();
  resetFilters();
});
document.querySelector("#empty-reset").addEventListener("click", resetFilters);
document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

start();
