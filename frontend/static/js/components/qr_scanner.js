/**
 * Camera-based QR scanner using the native BarcodeDetector API where available,
 * with a manual token-paste fallback for browsers that don't support it (no
 * external QR-decoding library is loaded, keeping the app's strict CSP intact).
 */
function initQrScanner(containerId, onTokenScanned) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const supportsDetector = "BarcodeDetector" in window;

  container.innerHTML = `
    <div class="card">
      <h3>Scan evidence QR code</h3>
      ${supportsDetector ? '<video id="qr-video" width="320" height="240" autoplay playsinline></video><div><button id="qr-start" class="btn">Start camera</button> <button id="qr-stop" class="btn secondary hidden">Stop</button></div>' : ""}
      <p class="form-help">${supportsDetector ? "Point your camera at the QR code, or paste the token manually below." : "Live camera scanning isn't supported in this browser. Paste the QR token below instead."}</p>
      <label for="qr-token-input">QR token</label>
      <textarea id="qr-token-input" rows="2" placeholder="Paste QR token here"></textarea>
      <button id="qr-verify-btn" class="btn" style="margin-top:0.5rem;">Verify</button>
      <div id="qr-result" style="margin-top:0.75rem;"></div>
    </div>
  `;

  const resultEl = container.querySelector("#qr-result");
  const tokenInput = container.querySelector("#qr-token-input");

  container.querySelector("#qr-verify-btn").addEventListener("click", () => {
    const token = tokenInput.value.trim();
    if (!token) {
      resultEl.innerHTML = '<div class="alert error">Enter or scan a QR token first.</div>';
      return;
    }
    onTokenScanned(token, resultEl);
  });

  if (!supportsDetector) return;

  let stream = null;
  let detectorInterval = null;
  const video = container.querySelector("#qr-video");
  const startBtn = container.querySelector("#qr-start");
  const stopBtn = container.querySelector("#qr-stop");

  startBtn.addEventListener("click", async () => {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      video.srcObject = stream;
      startBtn.classList.add("hidden");
      stopBtn.classList.remove("hidden");

      const detector = new window.BarcodeDetector({ formats: ["qr_code"] });
      detectorInterval = setInterval(async () => {
        try {
          const barcodes = await detector.detect(video);
          if (barcodes.length > 0) {
            tokenInput.value = barcodes[0].rawValue;
            stopScanning();
            onTokenScanned(barcodes[0].rawValue, resultEl);
          }
        } catch (_err) { /* detection frame failed; keep trying */ }
      }, 500);
    } catch (_err) {
      resultEl.innerHTML = '<div class="alert error">Camera access was denied or is unavailable.</div>';
    }
  });

  function stopScanning() {
    if (detectorInterval) clearInterval(detectorInterval);
    if (stream) stream.getTracks().forEach((track) => track.stop());
    startBtn.classList.remove("hidden");
    stopBtn.classList.add("hidden");
  }

  stopBtn.addEventListener("click", stopScanning);
}
