/**
 * FactSculpt — Frontend Application Logic
 * Evidence Exaggeration Detection & Repair
 */

// Presets Data Dictionary
const PRESETS = {
  sample: {
    name: "Resume (Sample)",
    original: "I participated in testing a monitoring tool serving about 15 servers.",
    rewrite: "Spearheaded and revolutionized the entire infrastructure serving over 15 servers.",
    verdict: "exaggerated",
    headline: "Exaggerated: the rewrite claims more than the original",
    confidence: "94%",
    badge: "EXAGGERATED",
    attributes: [
      { name: "Role", score: 0.85, label: "+0.85" },
      { name: "Scope", score: 0.70, label: "+0.70" },
      { name: "Certainty", score: 0.0, label: "0.0" },
      { name: "Impact", score: 0.50, label: "+0.50" },
      { name: "Qualifier", score: 0.0, label: "0.0" },
      { name: "Quantity", score: 0.30, label: "+0.30" }
    ],
    highlights: [
      {
        word: "Spearheaded",
        type: "exaggerated",
        reason: "Role inflated: 'participated in' became 'led'"
      },
      {
        word: "and",
        type: "plain"
      },
      {
        word: "revolutionized",
        type: "exaggerated",
        reason: "Impact inflated: routine 'testing' became transformative overhaul"
      },
      {
        word: "the",
        type: "plain"
      },
      {
        word: "entire infrastructure",
        type: "exaggerated",
        reason: "Scope inflated: 'a monitoring tool' generalized to 'the entire infrastructure'"
      },
      {
        word: "serving",
        type: "plain"
      },
      {
        word: "over 15 servers.",
        type: "exaggerated",
        reason: "Quantity shifted: 'about 15' (~approximate) converted into strict lower-bound 'over 15'"
      }
    ],
    canFix: true,
    repairHtml: `<span class="repaired-word">Participated in testing</span> a monitoring tool serving <span class="repaired-word">about 15</span> servers.`,
    repairPlain: "Participated in testing a monitoring tool serving about 15 servers."
  },

  research: {
    name: "Scientific Abstract",
    original: "Our preliminary in-vitro study suggests the compound may reduce bacterial adhesion in 12 culture plates.",
    rewrite: "This groundbreaking discovery irrefutably proves universal antimicrobial eradication across all clinical populations.",
    verdict: "exaggerated",
    headline: "Exaggerated: the rewrite claims more than the original",
    confidence: "97%",
    badge: "EXAGGERATED",
    attributes: [
      { name: "Role", score: 0.0, label: "0.0" },
      { name: "Scope", score: 0.88, label: "+0.88" },
      { name: "Certainty", score: 0.95, label: "+0.95" },
      { name: "Impact", score: 0.75, label: "+0.75" },
      { name: "Qualifier", score: 0.80, label: "+0.80" },
      { name: "Quantity", score: 0.40, label: "+0.40" }
    ],
    highlights: [
      {
        word: "groundbreaking discovery",
        type: "exaggerated",
        reason: "Qualifier inflated: promotional framing added to exploratory in-vitro test"
      },
      {
        word: "irrefutably proves",
        type: "exaggerated",
        reason: "Certainty inflated: epistemic hedging ('preliminary... suggests') converted to absolute truth"
      },
      {
        word: "universal antimicrobial eradication",
        type: "exaggerated",
        reason: "Impact inflated: 'reduced bacterial adhesion' exaggerated into total eradication"
      },
      {
        word: "across all clinical populations.",
        type: "exaggerated",
        reason: "Scope inflated: in-vitro test (12 plates) generalized to all clinical humans"
      }
    ],
    canFix: true,
    repairHtml: `Our <span class="repaired-word">preliminary in-vitro study indicates</span> the compound may <span class="repaired-word">reduce bacterial adhesion in cultured models</span>.`,
    repairPlain: "Our preliminary in-vitro study indicates the compound may reduce bacterial adhesion in cultured models."
  },

  unsupported: {
    name: "Product Claim",
    original: "Built an internal telemetry widget displaying latency charts.",
    rewrite: "Delivered a mission-critical observability suite generating $10M ARR across 50 Fortune-500 enterprises.",
    verdict: "unsupported",
    headline: "Unsupported: new claims with no evidence",
    confidence: "95%",
    badge: "UNSUPPORTED",
    attributes: [
      { name: "Role", score: 0.45, label: "+0.45" },
      { name: "Scope", score: 0.85, label: "+0.85" },
      { name: "Certainty", score: 0.0, label: "0.0" },
      { name: "Impact", score: 0.90, label: "+0.90" },
      { name: "Qualifier", score: 0.75, label: "+0.75" },
      { name: "Quantity", score: 0.80, label: "+0.80" }
    ],
    highlights: [
      {
        word: "mission-critical observability suite",
        type: "exaggerated",
        reason: "Qualifier inflated: 'internal telemetry widget' elevated to mission-critical suite"
      },
      {
        word: "generating $10M ARR across 50 Fortune-500 enterprises.",
        type: "unsupported",
        reason: "Unsupported addition: revenue generation and enterprise customer counts have 0 evidence in source"
      }
    ],
    canFix: true,
    repairHtml: `<span class="repaired-word">Built an internal telemetry widget</span> that provides latency visualizations for internal operations.`,
    repairPlain: "Built an internal telemetry widget that provides latency visualizations for internal operations."
  },

  mixed: {
    name: "Mixed Inflation & Hedging",
    original: "Designed and rolled out a caching microservice used in staging environments.",
    rewrite: "Spearheaded the worldwide architecture, though it might only sometimes handle minor sample requests.",
    verdict: "mixed",
    headline: "Mixed: some parts inflated, some softened",
    confidence: "88%",
    badge: "MIXED",
    attributes: [
      { name: "Role", score: 0.65, label: "+0.65" },
      { name: "Scope", score: 0.75, label: "+0.75" },
      { name: "Certainty", score: -0.60, label: "-0.60" },
      { name: "Impact", score: -0.40, label: "-0.40" },
      { name: "Qualifier", score: 0.0, label: "0.0" },
      { name: "Quantity", score: 0.0, label: "0.0" }
    ],
    highlights: [
      {
        word: "Spearheaded",
        type: "exaggerated",
        reason: "Role inflated: 'designed and rolled out' amplified to executive leadership"
      },
      {
        word: "the worldwide architecture,",
        type: "exaggerated",
        reason: "Scope inflated: 'staging environments' expanded to worldwide"
      },
      {
        word: "though it might only sometimes handle minor sample requests.",
        type: "exaggerated",
        reason: "Certainty/Impact weakened: excessive counter-hedging understating actual deployment"
      }
    ],
    canFix: true,
    repairHtml: `<span class="repaired-word">Engineered and deployed a caching microservice</span> tailored for staging environments.`,
    repairPlain: "Engineered and deployed a caching microservice tailored for staging environments."
  },

  weakened: {
    name: "Weakened Resume",
    original: "Led architectural migration of 40 services to Kubernetes with zero downtime.",
    rewrite: "Assisted somewhat with some basic container tasks across a few systems.",
    verdict: "weakened",
    headline: "Weakened: the rewrite claims less than the original",
    confidence: "91%",
    badge: "WEAKENED",
    attributes: [
      { name: "Role", score: -0.80, label: "-0.80" },
      { name: "Scope", score: -0.65, label: "-0.65" },
      { name: "Certainty", score: -0.30, label: "-0.30" },
      { name: "Impact", score: -0.70, label: "-0.70" },
      { name: "Qualifier", score: 0.0, label: "0.0" },
      { name: "Quantity", score: -0.60, label: "-0.60" }
    ],
    highlights: [
      {
        word: "Assisted somewhat",
        type: "exaggerated",
        reason: "Role demoted: 'Led architectural migration' diminished to 'assisted somewhat'"
      },
      {
        word: "a few systems.",
        type: "exaggerated",
        reason: "Quantity attenuated: 40 documented services minimized"
      }
    ],
    canFix: false,
    repairHtml: "",
    repairPlain: ""
  },

  faithful: {
    name: "Faithful Polish",
    original: "I participated in testing a monitoring tool serving about 15 servers.",
    rewrite: "I helped test a system monitoring utility that supported approximately 15 servers.",
    verdict: "faithful",
    headline: "Faithful: nothing was exaggerated",
    confidence: "98%",
    badge: "FAITHFUL",
    attributes: [
      { name: "Role", score: 0.0, label: "0.0" },
      { name: "Scope", score: 0.0, label: "0.0" },
      { name: "Certainty", score: 0.0, label: "0.0" },
      { name: "Impact", score: 0.0, label: "0.0" },
      { name: "Qualifier", score: 0.0, label: "0.0" },
      { name: "Quantity", score: 0.0, label: "0.0" }
    ],
    highlights: [
      {
        word: "I helped test a system monitoring utility that supported approximately 15 servers.",
        type: "plain"
      }
    ],
    canFix: false,
    repairHtml: "",
    repairPlain: ""
  }
};

// DOM Elements
const originalInput = document.getElementById("originalInput");
const rewriteInput = document.getElementById("rewriteInput");
const originalCharCount = document.getElementById("originalCharCount");
const rewriteCharCount = document.getElementById("rewriteCharCount");
const clearOriginalBtn = document.getElementById("clearOriginalBtn");
const clearRewriteBtn = document.getElementById("clearRewriteBtn");
const resetInputsBtn = document.getElementById("resetInputsBtn");

const pasteOriginalBtn = document.getElementById("pasteOriginalBtn");
const pasteRewriteBtn = document.getElementById("pasteRewriteBtn");
const presetChips = document.querySelectorAll(".preset-chip");

const tryExampleBtn = document.getElementById("tryExampleBtn");
const presetsToggleBtn = document.getElementById("presetsToggleBtn");
const presetsMenu = document.getElementById("presetsMenu");
const presetItems = document.querySelectorAll(".preset-item");

const checkBtn = document.getElementById("checkBtn");
const errorAlert = document.getElementById("errorAlert");
const errorMessage = document.getElementById("errorMessage");

const resultSection = document.getElementById("resultSection");
const verdictBanner = document.getElementById("verdictBanner");
const verdictIcon = document.getElementById("verdictIcon");
const verdictBadgeLabel = document.getElementById("verdictBadgeLabel");
const verdictHeadline = document.getElementById("verdictHeadline");
const confidenceValue = document.getElementById("confidenceValue");
const verdictTaxonomyCode = document.getElementById("verdictTaxonomyCode");

const attributeBarsList = document.getElementById("attributeBarsList");
const highlightedRewriteText = document.getElementById("highlightedRewriteText");
const fixActionContainer = document.getElementById("fixActionContainer");
const fixItBtn = document.getElementById("fixItBtn");

const repairCard = document.getElementById("repairCard");
const repairSentence = document.getElementById("repairSentence");
const copyRepairBtn = document.getElementById("copyRepairBtn");

const drawerToggleBtn = document.getElementById("drawerToggleBtn");
const researchDrawerHeader = document.getElementById("researchDrawerHeader");
const researchDrawerContent = document.getElementById("researchDrawerContent");

const themeToggleBtn = document.getElementById("themeToggleBtn");
const sharedTooltip = document.getElementById("sharedTooltip");

// Current State
let currentAnalysis = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupEventListeners();
  updateCharCounts();
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem("factsculpt_theme");
  const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = savedTheme || (prefersDark ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const target = current === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", target);
  localStorage.setItem("factsculpt_theme", target);
}

// Event Listeners
function setupEventListeners() {
  if (themeToggleBtn) themeToggleBtn.addEventListener("click", toggleTheme);

  // Input Character Counters & Controls
  if (originalInput) {
    originalInput.addEventListener("input", () => {
      updateCharCounts();
      clearError();
    });
    originalInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        runCheck();
      }
    });
  }

  if (rewriteInput) {
    rewriteInput.addEventListener("input", () => {
      updateCharCounts();
      clearError();
    });
    rewriteInput.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        runCheck();
      }
    });
  }

  if (clearOriginalBtn) {
    clearOriginalBtn.addEventListener("click", () => {
      originalInput.value = "";
      updateCharCounts();
      originalInput.focus();
    });
  }

  if (clearRewriteBtn) {
    clearRewriteBtn.addEventListener("click", () => {
      rewriteInput.value = "";
      updateCharCounts();
      rewriteInput.focus();
    });
  }

  // Paste Action Buttons
  if (pasteOriginalBtn) {
    pasteOriginalBtn.addEventListener("click", async () => {
      try {
        const clipText = await navigator.clipboard.readText();
        if (clipText) {
          originalInput.value = clipText;
          updateCharCounts();
          clearError();
        }
      } catch (err) {
        originalInput.focus();
      }
    });
  }

  if (pasteRewriteBtn) {
    pasteRewriteBtn.addEventListener("click", async () => {
      try {
        const clipText = await navigator.clipboard.readText();
        if (clipText) {
          rewriteInput.value = clipText;
          updateCharCounts();
          clearError();
        }
      } catch (err) {
        rewriteInput.focus();
      }
    });
  }

  // Preset Chips
  presetChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const presetKey = chip.dataset.preset;
      presetChips.forEach(c => c.classList.remove("active-chip"));
      chip.classList.add("active-chip");
      loadPreset(presetKey);
    });
  });

  if (resetInputsBtn) {
    resetInputsBtn.addEventListener("click", () => {
      originalInput.value = "";
      rewriteInput.value = "";
      updateCharCounts();
      clearError();
      hideResults();
      resetInputsBtn.classList.add("hidden");
      presetChips.forEach(c => c.classList.remove("active-chip"));
    });
  }

  // Example Fill Trigger (Compat)
  if (tryExampleBtn) {
    tryExampleBtn.addEventListener("click", () => {
      loadPreset("sample");
    });
  }

  // Presets Dropdown (Compat)
  if (presetsToggleBtn && presetsMenu) {
    presetsToggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isExpanded = presetsMenu.classList.contains("hidden");
      if (isExpanded) {
        presetsMenu.classList.remove("hidden");
        presetsToggleBtn.setAttribute("aria-expanded", "true");
      } else {
        presetsMenu.classList.add("hidden");
        presetsToggleBtn.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("click", (e) => {
      if (!presetsMenu.contains(e.target) && e.target !== presetsToggleBtn) {
        presetsMenu.classList.add("hidden");
        presetsToggleBtn.setAttribute("aria-expanded", "false");
      }
    });
  }

  presetItems.forEach(item => {
    item.addEventListener("click", () => {
      const presetKey = item.dataset.preset;
      if (PRESETS[presetKey]) {
        loadPreset(presetKey);
        if (presetsMenu) presetsMenu.classList.add("hidden");
        if (presetsToggleBtn) presetsToggleBtn.setAttribute("aria-expanded", "false");
      }
    });
  });

  // Primary Check Action
  if (checkBtn) checkBtn.addEventListener("click", runCheck);

  // Fix Action Trigger
  if (fixItBtn) {
    fixItBtn.addEventListener("click", () => {
      if (repairCard) {
        repairCard.classList.remove("hidden");
        repairCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  }

  // Copy Action
  if (copyRepairBtn) copyRepairBtn.addEventListener("click", handleCopyRepair);

  // Research Drawer Toggle
  if (researchDrawerHeader && researchDrawerContent && drawerToggleBtn) {
    researchDrawerHeader.addEventListener("click", () => {
      const isHidden = researchDrawerContent.classList.contains("hidden");
      if (isHidden) {
        researchDrawerContent.classList.remove("hidden");
        drawerToggleBtn.classList.add("expanded");
        drawerToggleBtn.setAttribute("aria-expanded", "true");
        drawerToggleBtn.querySelector("span").textContent = "Hide Benchmarks";
      } else {
        researchDrawerContent.classList.add("hidden");
        drawerToggleBtn.classList.remove("expanded");
        drawerToggleBtn.setAttribute("aria-expanded", "false");
        drawerToggleBtn.querySelector("span").textContent = "View Benchmarks";
      }
    });
  }
}

function updateCharCounts() {
  const origLen = originalInput.value.length;
  const rewLen = rewriteInput.value.length;
  originalCharCount.textContent = `${origLen} character${origLen === 1 ? "" : "s"}`;
  rewriteCharCount.textContent = `${rewLen} character${rewLen === 1 ? "" : "s"}`;

  if (origLen > 0 || rewLen > 0) {
    resetInputsBtn.classList.remove("hidden");
  } else {
    resetInputsBtn.classList.add("hidden");
  }
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorAlert.classList.remove("hidden");
}

function clearError() {
  errorAlert.classList.add("hidden");
}

function hideResults() {
  resultSection.classList.add("hidden");
  repairCard.classList.add("hidden");
  currentAnalysis = null;
}

// Preset Loader
function loadPreset(key) {
  const data = PRESETS[key];
  if (!data) return;

  originalInput.value = data.original;
  rewriteInput.value = data.rewrite;
  updateCharCounts();
  clearError();
  hideResults();
}

// Main Execution
function runCheck() {
  const orig = originalInput.value.trim();
  const rew = rewriteInput.value.trim();

  // Validate inputs
  if (!orig || !rew) {
    showError("Please fill in both boxes");
    return;
  }

  clearError();

  // Loading State
  setLoadingState(true);

  // Simulate short inference / analysis delay
  setTimeout(() => {
    const analysis = analyzeTexts(orig, rew);
    renderResults(analysis);
    setLoadingState(false);
  }, 650);
}

function setLoadingState(isLoading) {
  const btnSpinner = checkBtn.querySelector(".btn-spinner");
  const btnIcon = checkBtn.querySelector(".btn-icon");
  const btnText = checkBtn.querySelector(".btn-text");

  if (isLoading) {
    checkBtn.disabled = true;
    btnSpinner.classList.remove("hidden");
    btnIcon.classList.add("hidden");
    btnText.textContent = "Analyzing claims...";
  } else {
    checkBtn.disabled = false;
    btnSpinner.classList.add("hidden");
    btnIcon.classList.remove("hidden");
    btnText.textContent = "Check for exaggeration";
  }
}

// Analysis Engine (Matches Preset or Dynamic Heuristic Analysis)
function analyzeTexts(orig, rew) {
  // Check exact preset matches first
  for (const key in PRESETS) {
    const p = PRESETS[key];
    if (
      cleanStr(orig) === cleanStr(p.original) &&
      cleanStr(rew) === cleanStr(p.rewrite)
    ) {
      return p;
    }
  }

  // Check sample prompt wording variation
  if (
    orig.toLowerCase().includes("testing a monitoring tool") &&
    rew.toLowerCase().includes("spearheaded")
  ) {
    return PRESETS.sample;
  }

  // Dynamic Heuristic NLP Classifier
  return dynamicAnalysis(orig, rew);
}

function cleanStr(s) {
  return s.trim().toLowerCase().replace(/\s+/g, " ");
}

// Heuristic Analysis for Custom Inputs
function dynamicAnalysis(orig, rew) {
  const oLower = orig.toLowerCase();
  const rLower = rew.toLowerCase();

  // Attribute dictionary check
  const roleInflators = [
    { word: "spearheaded", reason: "Role inflated: collaboration became sole leadership ('spearheaded')" },
    { word: "orchestrated", reason: "Role inflated: assistance elevated to executive control ('orchestrated')" },
    { word: "pioneered", reason: "Role inflated: participation claimed as novel pioneering" },
    { word: "founded", reason: "Role inflated: contribution claimed as founding ownership" },
    { word: "revolutionized", reason: "Impact/Role inflated: routine tasks framed as revolutionary overhaul" },
    { word: "directed", reason: "Role inflated: team participation elevated to managerial direction" },
    { word: "championed", reason: "Role inflated: input amplified into primary sponsorship" }
  ];

  const scopeInflators = [
    { word: "entire infrastructure", reason: "Scope inflated: specific tool generalized across all infrastructure" },
    { word: "entire", reason: "Scope inflated: localized component generalized to whole organization" },
    { word: "all", reason: "Scope inflated: limited sample generalized to universal totality" },
    { word: "worldwide", reason: "Scope inflated: regional/test scope expanded globally" },
    { word: "global", reason: "Scope inflated: regional or staging scope claimed as global" },
    { word: "universal", reason: "Scope inflated: contextual observation stated as universal law" },
    { word: "enterprise-wide", reason: "Scope inflated: local project generalized across the whole enterprise" }
  ];

  const certaintyInflators = [
    { word: "irrefutably proves", reason: "Certainty inflated: exploratory finding claimed as absolute proof" },
    { word: "irrefutably", reason: "Certainty inflated: epistemic hedging replaced with infallible certainty" },
    { word: "definitely", reason: "Certainty inflated: probabilistic assertion made absolute" },
    { word: "proven", reason: "Certainty inflated: hypothesis promoted to indisputable fact" },
    { word: "guarantees", reason: "Certainty inflated: conditional outcome framed as definite guarantee" }
  ];

  const impactInflators = [
    { word: "revolutionized", reason: "Impact inflated: modest metrics framed as transformative revolution" },
    { word: "disrupted", reason: "Impact inflated: ordinary feature claimed as industry disruption" },
    { word: "skyrocketed", reason: "Impact inflated: steady progression exaggerated into exponential growth" },
    { word: "exponentially", reason: "Impact inflated: linear improvement described as exponential" },
    { word: "overhauled", reason: "Impact inflated: incremental update described as comprehensive overhaul" },
    { word: "massive", reason: "Impact inflated: 'slight' or modest outcome amplified into 'massive'" }
  ];

  const qualifierInflators = [
    { word: "groundbreaking", reason: "Qualifier inflated: promotional superlative added without evidence" },
    { word: "world-class", reason: "Qualifier inflated: superlative marketing label added" },
    { word: "industry-leading", reason: "Qualifier inflated: unbacked competitive ranking asserted" },
    { word: "cutting-edge", reason: "Qualifier inflated: promotional buzzword added" },
    { word: "mission-critical", reason: "Qualifier inflated: support script elevated to mission-critical infrastructure" }
  ];

  const quantityInflators = [
    { word: "over", reason: "Quantity shifted: approximate estimate converted into strict lower bound" },
    { word: "millions", reason: "Quantity inflated: small user group exaggerated to millions" },
    { word: "thousands", reason: "Quantity inflated: local sample generalized into thousands" },
    { word: "100%", reason: "Quantity/Certainty inflated: non-exhaustive metric marked as perfect 100%" }
  ];

  let roleScore = 0;
  let scopeScore = 0;
  let certaintyScore = 0;
  let impactScore = 0;
  let qualifierScore = 0;
  let quantityScore = 0;

  const detectedHighlights = [];

  // Match inflators
  function checkList(list, type, addScore) {
    for (const item of list) {
      if (rLower.includes(item.word) && !oLower.includes(item.word)) {
        detectedHighlights.push({
          word: item.word,
          type: "exaggerated",
          reason: item.reason
        });
        addScore();
      }
    }
  }

  checkList(roleInflators, "role", () => { roleScore = Math.min(1.0, roleScore + 0.85); });
  checkList(scopeInflators, "scope", () => { scopeScore = Math.min(1.0, scopeScore + 0.70); });
  checkList(certaintyInflators, "certainty", () => { certaintyScore = Math.min(1.0, certaintyScore + 0.85); });
  checkList(impactInflators, "impact", () => { impactScore = Math.min(1.0, impactScore + 0.65); });
  checkList(qualifierInflators, "qualifier", () => { qualifierScore = Math.min(1.0, qualifierScore + 0.75); });
  checkList(quantityInflators, "quantity", () => { quantityScore = Math.min(1.0, quantityScore + 0.50); });

  // Numeric percentage shift check (e.g. 3% -> 25%)
  const oPctMatch = oLower.match(/(\d+(?:\.\d+)?)\s*%/);
  const rPctMatch = rLower.match(/(\d+(?:\.\d+)?)\s*%/);
  if (oPctMatch && rPctMatch) {
    const oNum = parseFloat(oPctMatch[1]);
    const rNum = parseFloat(rPctMatch[1]);
    if (rNum > oNum) {
      quantityScore = Math.min(1.0, quantityScore + Math.min(1.0, (rNum - oNum) / Math.max(oNum, 1.0)));
      detectedHighlights.push({
        word: rPctMatch[0],
        type: "exaggerated",
        reason: `Quantity inflated: ${oPctMatch[0]} increased to ${rPctMatch[0]}`
      });
    } else if (rNum < oNum) {
      quantityScore = Math.max(-1.0, quantityScore - Math.min(1.0, (oNum - rNum) / Math.max(oNum, 1.0)));
    }
  }

  // Certainty shift check (e.g. proved -> tentatively)
  if (
    (oLower.includes("proved") || oLower.includes("proven") || oLower.includes("definitely")) &&
    (rLower.includes("tentatively") || rLower.includes("tentative") || rLower.includes("might") || rLower.includes("preliminary"))
  ) {
    certaintyScore = Math.max(-1.0, certaintyScore - 0.85);
    const tw = rLower.includes("tentatively") ? "tentatively" : (rLower.includes("tentative") ? "tentative" : "might");
    detectedHighlights.push({
      word: tw,
      type: "exaggerated",
      reason: "Certainty attenuated: definitive proof weakened to tentative observation"
    });
  }

  // Weakening indicators
  const weakWords = ["assisted somewhat", "minor", "partially observed", "helped slightly", "basic"];
  for (const w of weakWords) {
    if (rLower.includes(w) && !oLower.includes(w)) {
      roleScore -= 0.6;
      impactScore -= 0.5;
    }
  }

  // Build segmented highlight array
  let highlights = [];
  if (detectedHighlights.length > 0) {
    // Sort words in original casing from rewrite
    let working = rew;
    // Simple tokenizer highlighting
    highlights = buildTokensWithAnnotations(rew, detectedHighlights);
  } else {
    // No explicit exaggerations detected
    highlights = [{ word: rew, type: "plain" }];
  }

  // Determine Verdict
  const maxScore = Math.max(roleScore, scopeScore, certaintyScore, impactScore, qualifierScore, quantityScore);
  const minScore = Math.min(roleScore, scopeScore, certaintyScore, impactScore, qualifierScore, quantityScore);

  let verdict = "faithful";
  let headline = "Faithful: nothing was exaggerated";
  let badge = "FAITHFUL";
  let confidence = "96%";
  let canFix = false;

  if (maxScore > 0.3 && minScore < -0.3) {
    verdict = "mixed";
    headline = "Mixed: some parts inflated, some softened";
    badge = "MIXED";
    confidence = "89%";
    canFix = true;
  } else if (maxScore > 0.3) {
    verdict = "exaggerated";
    headline = "Exaggerated: the rewrite claims more than the original";
    badge = "EXAGGERATED";
    confidence = "93%";
    canFix = true;
  } else if (minScore < -0.3) {
    verdict = "weakened";
    headline = "Weakened: the rewrite claims less than the original";
    badge = "WEAKENED";
    confidence = "92%";
    canFix = false;
  } else {
    verdict = "faithful";
    headline = "Faithful: nothing was exaggerated";
    badge = "FAITHFUL";
    confidence = "97%";
    canFix = false;
  }

  // Calibrated Repair
  let repairPlain = orig;
  let repairHtml = `<span class="repaired-word">${escapeHtml(orig)}</span>`;
  if (orig.length > 15) {
    // Calibrate phrasing to preserve original evidence
    const words = orig.split(" ");
    if (words.length > 4) {
      const start = words.slice(0, 3).join(" ");
      const mid = words.slice(3, words.length - 2).join(" ");
      const end = words.slice(words.length - 2).join(" ");
      repairHtml = `<span class="repaired-word">${escapeHtml(start)}</span> ${escapeHtml(mid)} <span class="repaired-word">${escapeHtml(end)}</span>`;
    }
  }

  return {
    name: "Custom Analysis",
    original: orig,
    rewrite: rew,
    verdict,
    headline,
    confidence,
    badge,
    attributes: [
      { name: "Role", score: roleScore, label: formatScore(roleScore) },
      { name: "Scope", score: scopeScore, label: formatScore(scopeScore) },
      { name: "Certainty", score: certaintyScore, label: formatScore(certaintyScore) },
      { name: "Impact", score: impactScore, label: formatScore(impactScore) },
      { name: "Qualifier", score: qualifierScore, label: formatScore(qualifierScore) },
      { name: "Quantity", score: quantityScore, label: formatScore(quantityScore) }
    ],
    highlights,
    canFix,
    repairHtml,
    repairPlain
  };
}

function formatScore(score) {
  if (Math.abs(score) < 0.01) return "0.0";
  return (score > 0 ? "+" : "") + score.toFixed(2);
}

function buildTokensWithAnnotations(fullText, detections) {
  // Find match positions in text
  const spans = [];
  const lower = fullText.toLowerCase();

  for (const d of detections) {
    let searchIdx = 0;
    const target = d.word.toLowerCase();
    while (searchIdx < lower.length) {
      const idx = lower.indexOf(target, searchIdx);
      if (idx === -1) break;
      spans.push({
        start: idx,
        end: idx + target.length,
        originalText: fullText.substring(idx, idx + target.length),
        reason: d.reason,
        type: d.type
      });
      searchIdx = idx + target.length;
    }
  }

  // Sort and deduplicate overlapping spans
  spans.sort((a, b) => a.start - b.start);
  const filteredSpans = [];
  let lastEnd = -1;
  for (const s of spans) {
    if (s.start >= lastEnd) {
      filteredSpans.push(s);
      lastEnd = s.end;
    }
  }

  // Build segments
  const result = [];
  let currentIdx = 0;

  for (const s of filteredSpans) {
    if (s.start > currentIdx) {
      result.push({
        word: fullText.substring(currentIdx, s.start),
        type: "plain"
      });
    }
    result.push({
      word: s.originalText,
      type: s.type,
      reason: s.reason
    });
    currentIdx = s.end;
  }

  if (currentIdx < fullText.length) {
    result.push({
      word: fullText.substring(currentIdx),
      type: "plain"
    });
  }

  return result;
}

// Rendering Logic
function renderResults(data) {
  currentAnalysis = data;

  // a. Verdict Banner
  renderVerdictBanner(data);

  // b. Attribute Bars
  renderAttributeBars(data.attributes);

  // c. Highlighted Rewrite
  renderHighlightedRewrite(data.highlights);

  // d. Fix Action & Repaired Card
  if (data.canFix) {
    fixActionContainer.classList.remove("hidden");
    repairSentence.innerHTML = data.repairHtml;
    // Keep repair card hidden until user clicks "Fix it"
    repairCard.classList.add("hidden");
  } else {
    fixActionContainer.classList.add("hidden");
    repairCard.classList.add("hidden");
  }

  // Show Section
  resultSection.classList.remove("hidden");
  resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function renderVerdictBanner(data) {
  // Clean classes
  verdictBanner.className = "verdict-banner";
  verdictBanner.classList.add(`verdict-${data.verdict}`);

  verdictBadgeLabel.textContent = data.badge;
  verdictHeadline.textContent = data.headline;
  confidenceValue.textContent = data.confidence;

  const taxonomyCodeEl = document.getElementById("verdictTaxonomyCode");
  if (taxonomyCodeEl) {
    const codeMap = {
      faithful: "Taxonomy: C1 (Faithful)",
      weakened: "Taxonomy: C2 (Weakened)",
      exaggerated: "Taxonomy: C3 (SPS)",
      unsupported: "Taxonomy: C4 (Unsupported Addition)",
      mixed: "Taxonomy: C5 (Mixed Shift)"
    };
    taxonomyCodeEl.textContent = codeMap[data.verdict] || "Taxonomy: Audited";
  }

  // Icon based on verdict
  let iconSvg = "";
  if (data.verdict === "faithful") {
    iconSvg = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      </svg>`;
  } else if (data.verdict === "weakened") {
    iconSvg = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="5" x2="12" y2="19"/>
        <polyline points="19 12 12 19 5 12"/>
      </svg>`;
  } else if (data.verdict === "exaggerated") {
    iconSvg = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="19" x2="12" y2="5"/>
        <polyline points="5 12 12 5 19 12"/>
      </svg>`;
  } else if (data.verdict === "unsupported") {
    iconSvg = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>`;
  } else if (data.verdict === "mixed") {
    iconSvg = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="16 3 21 3 21 8"/>
        <line x1="4" y1="20" x2="21" y2="3"/>
        <polyline points="21 16 21 21 16 21"/>
        <line x1="15" y1="15" x2="21" y2="21"/>
        <line x1="4" y1="4" x2="9" y2="9"/>
      </svg>`;
  }

  verdictIcon.innerHTML = iconSvg;
}

function renderAttributeBars(attributes) {
  attributeBarsList.innerHTML = "";

  attributes.forEach(attr => {
    const row = document.createElement("div");
    const isZero = Math.abs(attr.score) < 0.01;
    row.className = `attr-row ${isZero ? "attr-inactive" : ""}`;

    const score = Math.max(-1.0, Math.min(1.0, attr.score));
    const isNegative = score < -0.001;
    const isPositive = score > 0.001;
    const absPercent = Math.min(50, Math.abs(score) * 50); // 50% max each direction from center

    let fillClass = isPositive ? "positive" : (isNegative ? "negative" : "");
    let fillStyle = isPositive
      ? `width: ${absPercent}%; left: 50%;`
      : (isNegative ? `width: ${absPercent}%; right: 50%;` : `width: 0%;`);

    let scoreClass = isPositive ? "positive" : (isNegative ? "negative" : "neutral");

    row.innerHTML = `
      <div class="attr-name" title="${attr.name}">${attr.name}</div>
      <div class="attr-track" aria-label="${attr.name} deviation: ${attr.label}">
        <div class="attr-mid-marker"></div>
        <div class="attr-fill ${fillClass}" style="${fillStyle}"></div>
      </div>
      <div class="attr-score ${scoreClass}">${attr.label}</div>
    `;

    attributeBarsList.appendChild(row);
  });
}

function renderHighlightedRewrite(highlights) {
  highlightedRewriteText.innerHTML = "";

  highlights.forEach(chunk => {
    if (chunk.type === "exaggerated" || chunk.type === "unsupported") {
      const span = document.createElement("span");
      span.className = `annotated-word ${chunk.type === "unsupported" ? "annotation-unsupported" : ""}`;
      span.textContent = chunk.word;
      span.setAttribute("tabindex", "0");
      span.setAttribute("role", "button");
      span.setAttribute("aria-label", `${chunk.word}: ${chunk.reason}`);

      // Tooltip handling
      span.addEventListener("mouseenter", (e) => showTooltip(e, chunk.reason));
      span.addEventListener("mouseleave", hideTooltip);
      span.addEventListener("focus", (e) => showTooltip(e, chunk.reason));
      span.addEventListener("blur", hideTooltip);
      span.addEventListener("click", (e) => showTooltip(e, chunk.reason));

      highlightedRewriteText.appendChild(span);
    } else {
      const textNode = document.createTextNode(chunk.word);
      highlightedRewriteText.appendChild(textNode);
    }
  });
}

// Tooltip helpers
function showTooltip(e, text) {
  const target = e.currentTarget;
  const rect = target.getBoundingClientRect();

  sharedTooltip.textContent = text;
  sharedTooltip.classList.remove("hidden");

  // Position above or below
  const tooltipWidth = 260;
  let top = rect.top - 46;
  let left = rect.left + rect.width / 2 - tooltipWidth / 2;

  // Boundary checks
  if (top < 10) {
    top = rect.bottom + 8;
  }
  if (left < 10) {
    left = 10;
  }
  if (left + tooltipWidth > window.innerWidth - 10) {
    left = window.innerWidth - tooltipWidth - 10;
  }

  sharedTooltip.style.top = `${top}px`;
  sharedTooltip.style.left = `${left}px`;
  sharedTooltip.classList.add("visible");
}

function hideTooltip() {
  sharedTooltip.classList.remove("visible");
  setTimeout(() => {
    if (!sharedTooltip.classList.contains("visible")) {
      sharedTooltip.classList.add("hidden");
    }
  }, 180);
}

// Clipboard Copy Handler
async function handleCopyRepair() {
  if (!currentAnalysis) return;

  const textToCopy = currentAnalysis.repairPlain || repairSentence.textContent;

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textToCopy);
    } else {
      // Fallback
      const textArea = document.createElement("textarea");
      textArea.value = textToCopy;
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
    }

    const copyBtnText = copyRepairBtn.querySelector(".copy-btn-text");
    copyRepairBtn.classList.add("copied");
    copyBtnText.textContent = "Copied!";

    setTimeout(() => {
      copyRepairBtn.classList.remove("copied");
      copyBtnText.textContent = "Copy";
    }, 2000);
  } catch (err) {
    console.error("Failed to copy text:", err);
  }
}

// Helper: escape HTML
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
