const $ = (id) => document.getElementById(id);
const form = $("calculator");
const format = (value) => Number.isFinite(value) ? value.toPrecision(10).replace(/\.?0+$/, "") : "undefined";

function audit(event) {
  event?.preventDefault();
  const rho = Number($("rho").value);
  const power = Number($("power").value);
  const x = Number($("x").value);
  const n = Number($("n").value);
  const E = Number($("E").value);
  const inputs = [rho, power, x, n, E];

  if (!inputs.every(Number.isFinite) || rho < 0 || n < 0 || !Number.isInteger(n) || E <= 0) {
    $("original").textContent = "undefined";
    $("candidate").textContent = "undefined";
    $("derivative").textContent = "undefined";
    $("convergence").textContent = "invalid domain";
    $("finding").textContent = "Rejected: require finite inputs, ρ ≥ 0, integer n ≥ 0, and E > 0.";
    return;
  }

  const original = (rho + power - rho * x ** n) / E;
  const candidate = (power - rho * Math.abs(x) ** n) / E;
  const derivative = (1 - x ** n) / E;
  const converges = rho === 0 || Math.abs(x) < 1;

  $("original").textContent = format(original);
  $("candidate").textContent = format(candidate);
  $("derivative").textContent = format(derivative);
  $("convergence").textContent = converges ? "yes" : "no";

  const findings = [];
  if (derivative > 0) findings.push("Fatal monotonicity conflict: increasing ρ raises the original score.");
  if (derivative === 0) findings.push("The original score is locally insensitive to ρ for these inputs.");
  if (derivative < 0) findings.push("The original score penalizes ρ only in this restricted input case.");
  if (!converges) findings.push("The stated residual does not tend to zero.");
  if (Math.abs(x) === 1 && rho !== 0) findings.push(x === -1 ? "The residual oscillates." : "The residual remains constant.");
  $("finding").textContent = findings.join(" ");
}

form.addEventListener("submit", audit);
audit();
