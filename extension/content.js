let currentModal = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "show_loading") {
        createModal();
        currentModal.querySelector('.envit5-body').innerHTML = `
            <p class="envit5-source">${escapeHtml(request.text)}</p>
            <p>Đang dịch...</p>
        `;
    } else if (request.action === "show_result") {
        if (!currentModal) createModal();
        
        if (request.error) {
            currentModal.querySelector('.envit5-body').innerHTML = `
                <p id="envit5-ext-error">Lỗi: ${escapeHtml(request.error)}</p>
            `;
            return;
        }

        let phoneticHtml = request.phonetic ? `<p class="envit5-phonetic">${escapeHtml(request.phonetic)}</p>` : '';

        currentModal.querySelector('.envit5-body').innerHTML = `
            <p class="envit5-source">${escapeHtml(request.source)}</p>
            ${phoneticHtml}
            <p class="envit5-result-area">
                <span class="envit5-translation">${escapeHtml(request.translation)}</span>
            </p>
            <div class="envit5-actions">
                <button class="envit5-btn" id="envit5-speak-src">🔊 Nguồn</button>
                <button class="envit5-btn" id="envit5-speak-tgt">🔊 Dịch</button>
                <button class="envit5-btn" id="envit5-explain">🔍 Giải thích</button>
            </div>
        `;

        document.getElementById('envit5-speak-src').addEventListener('click', () => {
            speakText(request.source, request.sourceLang);
        });
        document.getElementById('envit5-speak-tgt').addEventListener('click', () => {
            speakText(request.translation, request.targetLang);
        });
        document.getElementById('envit5-explain').addEventListener('click', async () => {
            const btn = document.getElementById('envit5-explain');
            const resultArea = currentModal.querySelector('.envit5-result-area');
            btn.innerText = "Đang tra...";
            try {
                const response = await fetch("http://localhost:5000/explain", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ word: request.source })
                });
                const data = await response.json();
                if (data.explanation) {
                    resultArea.innerHTML += `<div style="margin-top:10px; padding-top:10px; border-top:1px dashed #ccc; font-size: 0.9em; color: #444;"><strong>💡 Giải nghĩa:</strong><br>${escapeHtml(data.explanation)}</div>`;
                    btn.remove();
                }
            } catch (e) {
                alert("Lỗi: Server Python chưa chạy!");
                btn.innerText = "🔍 Giải thích";
            }
        });
    }
});

function createModal() {
    if (currentModal) {
        currentModal.remove();
    }
    
    currentModal = document.createElement('div');
    currentModal.id = 'envit5-ext-modal';
    currentModal.innerHTML = `
        <div class="envit5-header">
            <h3>Envit5 Translator</h3>
            <button class="envit5-close">✖</button>
        </div>
        <div class="envit5-body"></div>
    `;
    
    document.body.appendChild(currentModal);
    
    currentModal.querySelector('.envit5-close').addEventListener('click', () => {
        currentModal.remove();
        currentModal = null;
    });
    
    // Đã bỏ tính năng tự động xóa (Auto remove) để người dùng chủ động đóng
}

function escapeHtml(unsafe) {
    if (!unsafe) return "";
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function speakText(text, lang) {
    if (!window.speechSynthesis) return;
    const msg = new SpeechSynthesisUtterance(text);
    msg.lang = lang;
    window.speechSynthesis.speak(msg);
}
