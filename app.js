const $ = (id) => document.getElementById(id);
const form = $("calculator");

function format(value) {
  if (!Number.isFinite(value)) return "undefined";
  if (value === 0) return "0";
  const magnitude = Math.abs(value);
  if (magnitude >= 1e7 || magnitude < 1e-6) return value.toExponential(6);
  return Number(value.toPrecision(10)).toString();
}

function logistic(value) {
  if (value >= 0) {
    const z = Math.exp(-value);
    return 1 / (1 + z);
  }
  const z = Math.exp(value);
  return z / (1 + z);
}

function setInvalid(message) {
  [
    "original",
    "transient",
    "cumulative",
    "bounded",
    "original-derivative",
    "transient-derivative",
    "cumulative-derivative",
  ].forEach((id) => { $(id).textContent = "undefined"; });
  $("convergence").textContent = "invalid domain";
  $("finding").textContent = `Rejected: ${message}`;
  $("finding").dataset.status = "failed";
}

function audit(event) {
  event?.preventDefault();

  const rho = Number($("rho").value);
  const power = Number($("power").value);
  const x = Number($("x").value);
  const n = Number($("n").value);
  const normalization = Number($("E").value);
  const penaltyWeight = Number($("lambda").value);
  const inputs = [rho, power, x, n, normalization, penaltyWeight];

  if (!inputs.every(Number.isFinite)) {
    setInvalid("all inputs must be finite numbers.");
    return;
  }
  if (rho < 0 || penaltyWeight < 0) {
    setInvalid("require ρ ≥ 0 and λ ≥ 0.");
    return;
  }
  if (n < 0 || !Number.isInteger(n)) {
    setInvalid("n must be a non-negative integer.");
    return;
  }
  if (normalization <= 0) {
    setInvalid("normalization E must be strictly positive.");
    return;
  }

  let powerTerm;
  try {
    powerTerm = Math.abs(x) ** n;
  } catch {
    setInvalid("the exponentiation could not be evaluated.");
    return;
  }

  const signedPowerTerm = x ** n;
  const original = (rho + power - rho * signedPowerTerm) / normalization;
  const transient = (
    power - penaltyWeight * rho * powerTerm
  ) / normalization;
  const cumulative = (
    power - penaltyWeight * rho * (1 - powerTerm)
  ) / normalization;
  const originalDerivative = (1 - signedPowerTerm) / normalization;
  const transientDerivative = -(
    penaltyWeight * powerTerm
  ) / normalization;
  const cumulativeDerivative = -(
    penaltyWeight * (1 - powerTerm)
  ) / normalization;
  const converges = rho === 0 || Math.abs(x) < 1;

  const results = [
    original,
    transient,
    cumulative,
    originalDerivative,
    transientDerivative,
    cumulativeDerivative,
  ];
  if (!results.every(Number.isFinite)) {
    setInvalid("finite inputs produced overflow or an undefined numerical result.");
    return;
  }

  $("original").textContent = format(original);
  $("transient").textContent = format(transient);
  $("cumulative").textContent = format(cumulative);
  $("bounded").textContent = format(logistic(cumulative));
  $("original-derivative").textContent = format(originalDerivative);
  $("transient-derivative").textContent = format(transientDerivative);
  $("cumulative-derivative").textContent = format(cumulativeDerivative);
  $("convergence").textContent = converges ? "yes" : "no";

  const findings = [];
  let status = "conditional";

  if (originalDerivative > 0) {
    findings.push("Original model failure: increasing ρ raises the score.");
    status = "failed";
  } else if (originalDerivative === 0) {
    findings.push("The original model is locally insensitive to ρ at this state.");
  } else {
    findings.push("The original model penalizes ρ only in this restricted state.");
  }

  if (transientDerivative > 0) {
    findings.push("Transient candidate violates its declared contradiction-penalty sign.");
    status = "failed";
  } else {
    findings.push("Transient candidate has a non-positive contradiction derivative.");
  }

  if (Math.abs(x) <= 1 && cumulativeDerivative <= 0) {
    findings.push("Cumulative candidate passes its derivative sign gate in the declared |x| ≤ 1 domain.");
  } else if (cumulativeDerivative > 0) {
    findings.push("Cumulative candidate rewards contradiction outside its declared |x| ≤ 1 domain.");
    status = "failed";
  }

  if (!converges) {
    findings.push("The residual ρxⁿ does not tend to zero.");
    status = "failed";
  }
  if (Math.abs(x) === 1 && rho !== 0) {
    findings.push(x === -1 ? "The signed residual oscillates." : "The residual remains constant.");
  }
  if (Math.abs(x) < 1 && rho > 0 && penaltyWeight > 0) {
    findings.push("At large n, the transient penalty vanishes while the cumulative penalty approaches λρ/E.");
  }

  findings.push("Passing algebraic gates does not establish empirical validity.");
  $("finding").textContent = findings.join(" ");
  $("finding").dataset.status = status;
}

form.addEventListener("submit", audit);
audit();
