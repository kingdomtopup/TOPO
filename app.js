const form = document.querySelector("#builder-form");
const amountInput = document.querySelector("#amount");
const currencySelect = document.querySelector("#currency");
const typeSelect = document.querySelector("#qr-type");
const codeOutput = document.querySelector("#python-code");
const message = document.querySelector("#form-message");
const copyButton = document.querySelector("#copy-code");
const previewQr = document.querySelector("#preview-qr");

function pythonString(value) {
  return JSON.stringify(value);
}

function getValues() {
  const data = new FormData(form);
  return {
    merchantName: String(data.get("merchantName")).trim(),
    merchantCity: String(data.get("merchantCity")).trim(),
    bankAccount: String(data.get("bankAccount")).trim(),
    amount: String(data.get("amount")).trim(),
    currency: String(data.get("currency")),
    qrType: String(data.get("qrType")),
    billNumber: String(data.get("billNumber")).trim(),
  };
}

function renderCode(values) {
  const isStatic = values.qrType === "static";
  const args = [
    `    merchant=${pythonString(values.bankAccount)},`,
    `    merchant_name=${pythonString(values.merchantName)},`,
    `    merchant_city=${pythonString(values.merchantCity)},`,
  ];

  if (!isStatic && values.amount !== "") {
    args.push(`    amount=${Number(values.amount)},`);
  }
  args.push(`    currency=${pythonString(values.currency)},`);
  args.push(`    static=${isStatic ? "True" : "False"},`);
  if (values.billNumber) {
    args.push(`    bill_number=${pythonString(values.billNumber)},`);
  }

  return [
    "import os",
    "from khqr_payment import KHQRClient",
    "",
    'client = KHQRClient(os.environ["BAKONG_API_TOKEN"])',
    "",
    "qr = client.create_qr_string(",
    ...args,
    ")",
    "",
    "print(qr.md5)  # use this hash to check payment status",
  ].join("\n");
}

function hashText(value) {
  let hash = 2166136261;
  for (const char of value) {
    hash ^= char.codePointAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function isFinderCell(row, column, startRow, startColumn) {
  const localRow = row - startRow;
  const localColumn = column - startColumn;
  if (localRow < 0 || localRow > 6 || localColumn < 0 || localColumn > 6) return null;
  return localRow === 0 || localRow === 6 || localColumn === 0 || localColumn === 6
    || (localRow >= 2 && localRow <= 4 && localColumn >= 2 && localColumn <= 4);
}

function drawPreview(seedText) {
  const seed = hashText(seedText);
  let state = seed || 1;
  const nextBit = () => {
    state ^= state << 13;
    state ^= state >>> 17;
    state ^= state << 5;
    return (state >>> 0) % 2 === 0;
  };
  const fragment = document.createDocumentFragment();

  for (let row = 0; row < 21; row += 1) {
    for (let column = 0; column < 21; column += 1) {
      const cell = document.createElement("span");
      cell.className = "qr-cell";
      const finder = isFinderCell(row, column, 0, 0)
        ?? isFinderCell(row, column, 0, 14)
        ?? isFinderCell(row, column, 14, 0);
      if (finder === true || (finder === null && nextBit())) {
        cell.classList.add("is-dark");
      }
      fragment.append(cell);
    }
  }
  previewQr.replaceChildren(fragment);
}

function renderDemo() {
  const values = getValues();
  const isStatic = values.qrType === "static";
  amountInput.disabled = isStatic;
  amountInput.required = !isStatic;
  codeOutput.textContent = renderCode(values);

  const amount = Number(values.amount);
  const amountText = isStatic || values.amount === "" || !Number.isFinite(amount)
    ? "Enter amount in banking app"
    : `${values.currency === "KHR" ? "៛" : "$"}${amount.toFixed(2)} ${values.currency}`;
  document.querySelector("#preview-merchant").textContent = values.merchantName || "Your merchant";
  document.querySelector("#preview-total").textContent = amountText;
  document.querySelector("#preview-total").classList.toggle("is-static", isStatic || values.amount === "");
  drawPreview(`${values.merchantName}|${values.merchantCity}|${values.bankAccount}|${values.amount}|${values.currency}|${values.qrType}|${values.billNumber}`);
  message.textContent = "Example only. Keep API tokens on your server, never in browser code.";
  copyButton.textContent = "Copy code";
}

form.addEventListener("input", renderDemo);
form.addEventListener("change", renderDemo);
form.addEventListener("submit", (event) => event.preventDefault());

copyButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(codeOutput.textContent);
    copyButton.textContent = "Copied";
    message.textContent = "Python snippet copied. Add your token securely on the server.";
  } catch {
    message.textContent = "Clipboard access is unavailable. Select and copy the snippet manually.";
  }
});

renderDemo();
