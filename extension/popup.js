document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('apiKey');
    const saveApiKeyBtn = document.getElementById('saveApiKey');
    const inputText = document.getElementById('inputText');
    const directionSelect = document.getElementById('direction');
    const translateBtn = document.getElementById('translateBtn');
    const loading = document.getElementById('loading');
    const resultBox = document.getElementById('resultBox');
    const outputText = document.getElementById('outputText');
    const phoneticText = document.getElementById('phonetic');
    const speakInputBtn = document.getElementById('speakInputBtn');
    const speakOutputBtn = document.getElementById('speakOutputBtn');
    const exportHistoryBtn = document.getElementById('exportHistoryBtn');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    // Pre-fill API key from storage or fallback to default
    chrome.storage.local.get(['hfApiKey'], (result) => {
        if (result.hfApiKey) {
            apiKeyInput.value = result.hfApiKey;
        } else {
            apiKeyInput.value = '';
            chrome.storage.local.set({ hfApiKey: apiKeyInput.value });
        }
    });

    saveApiKeyBtn.addEventListener('click', () => {
        chrome.storage.local.set({ hfApiKey: apiKeyInput.value }, () => {
            alert('Đã lưu API Key!');
        });
    });

    async function getPhonetics(word) {
        try {
            if (word.split(' ').length > 2) return ''; 
            let cleanWord = word.replace(/[^\w\s]/gi, '').trim();
            if(!cleanWord) return '';
            const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${cleanWord}`);
            if (res.ok) {
                const data = await res.json();
                if (data && data[0] && data[0].phonetic) {
                    return data[0].phonetic;
                } else if (data && data[0] && data[0].phonetics) {
                    let p = data[0].phonetics.find(x => x.text);
                    return p ? p.text : '';
                }
            }
            return '';
        } catch (e) {
            return '';
        }
    }

    async function translate(text, direction) {
        return new Promise(async (resolve, reject) => {
            try {
                const response = await fetch("http://localhost:5000/translate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ 
                        text: text,
                        direction: direction
                    })
                });
                
                if (!response.ok) {
                    reject('Lỗi: Bạn đã chạy file server_translate.py chưa?');
                    return;
                }
                
                const data = await response.json();
                if (data.translation) {
                    resolve(data.translation);
                } else if (data.error) {
                    reject(`Server Lỗi: ${data.error}`);
                } else {
                    resolve(JSON.stringify(data));
                }
            } catch (e) {
                reject('Không thể kết nối tới Server Local. Hãy đảm bảo bạn đã chạy file server_translate.py');
            }
        });
    }

    function speakText(text, lang) {
        if (!window.speechSynthesis) return;
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = lang;
        window.speechSynthesis.speak(msg);
    }

    function saveHistory(source, translation) {
        chrome.storage.local.get({history: []}, (res) => {
            let hist = res.history;
            hist.push({
                time: new Date().toLocaleString(),
                source: source,
                translation: translation
            });
            chrome.storage.local.set({history: hist});
        });
    }

    translateBtn.addEventListener('click', async () => {
        const text = inputText.value.trim();
        const dir = directionSelect.value;
        
        if (!text) return;
        
        loading.classList.remove('hidden');
        resultBox.classList.add('hidden');
        phoneticText.innerText = '';
        outputText.innerText = '';

        try {
            if (dir === 'en: ') {
                let p = await getPhonetics(text);
                if (p) phoneticText.innerText = p;
            }

            const trans = await translate(text, dir);
            outputText.innerText = trans;
            resultBox.classList.remove('hidden');
            
            saveHistory(text, trans);
        } catch (e) {
            alert(e);
        } finally {
            loading.classList.add('hidden');
        }
    });

    speakInputBtn.addEventListener('click', () => {
        let text = inputText.value.trim();
        let dir = directionSelect.value;
        speakText(text, dir === 'en: ' ? 'en-US' : 'vi-VN');
    });

    speakOutputBtn.addEventListener('click', () => {
        let text = outputText.innerText;
        let dir = directionSelect.value;
        speakText(text, dir === 'en: ' ? 'vi-VN' : 'en-US');
    });

    exportHistoryBtn.addEventListener('click', () => {
        chrome.storage.local.get({history: []}, (res) => {
            let hist = res.history;
            if (hist.length === 0) {
                alert("Lịch sử trống!");
                return;
            }
            let mdContent = "# Lịch sử Dịch Thuật\n\n";
            hist.forEach(item => {
                mdContent += `**Thời gian:** ${item.time}\n\n`;
                mdContent += `**Nguồn:** ${item.source}\n\n`;
                mdContent += `**Dịch:** ${item.translation}\n\n`;
                mdContent += `---\n\n`;
            });
            
            const blob = new Blob([mdContent], { type: "text/markdown" });
            const url = URL.createObjectURL(blob);
            
            chrome.downloads.download({
                url: url,
                filename: "translation_history.md",
                saveAs: true
            });
        });
    });

    clearHistoryBtn.addEventListener('click', () => {
        if(confirm("Bạn có chắc muốn xóa toàn bộ lịch sử?")) {
            chrome.storage.local.set({history: []}, () => {
                alert("Đã xóa lịch sử.");
            });
        }
    });
});
