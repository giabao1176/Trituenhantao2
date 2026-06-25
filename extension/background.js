chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "translate_envit5",
        title: "Dịch bằng Envit5",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "translate_envit5") {
        const selectedText = info.selectionText;
        
        chrome.tabs.sendMessage(tab.id, { 
            action: "show_loading", 
            text: selectedText 
        });

        chrome.storage.local.get(['hfApiKey'], async (result) => {
            const token = result.hfApiKey;
            if (!token) {
                chrome.tabs.sendMessage(tab.id, { 
                    action: "show_result", 
                    error: "Chưa cấu hình API Key!" 
                });
                return;
            }

            const isVietnamese = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i.test(selectedText);
            const direction = isVietnamese ? "vi: " : "en: ";
            
            try {
                const response = await fetch("http://localhost:5000/translate", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ 
                        text: selectedText,
                        direction: direction
                    })
                });

                if (!response.ok) {
                    chrome.tabs.sendMessage(tab.id, { 
                        action: "show_result", 
                        error: "Lỗi: Hãy đảm bảo server_translate.py đang chạy!" 
                    });
                    return;
                }

                const data = await response.json();
                let resultText = data.translation || "";
                
                if (resultText) {
                    let phonetic = '';
                    if (direction === "en: " && selectedText.split(' ').length <= 2) {
                        try {
                            let cleanWord = selectedText.replace(/[^\w\s]/gi, '').trim();
                            const res = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${cleanWord}`);
                            if (res.ok) {
                                const pData = await res.json();
                                if (pData && pData[0] && pData[0].phonetic) phonetic = pData[0].phonetic;
                                else if (pData && pData[0] && pData[0].phonetics) {
                                    let p = pData[0].phonetics.find(x => x.text);
                                    if(p) phonetic = p.text;
                                }
                            }
                        } catch (e) {}
                    }

                    chrome.storage.local.get({history: []}, (res) => {
                        let hist = res.history;
                        hist.push({
                            time: new Date().toLocaleString(),
                            source: selectedText,
                            translation: resultText
                        });
                        chrome.storage.local.set({history: hist});
                    });

                    chrome.tabs.sendMessage(tab.id, { 
                        action: "show_result", 
                        source: selectedText,
                        translation: resultText,
                        phonetic: phonetic,
                        sourceLang: direction === "en: " ? 'en-US' : 'vi-VN',
                        targetLang: direction === "en: " ? 'vi-VN' : 'en-US'
                    });
                } else if (data.error) {
                    chrome.tabs.sendMessage(tab.id, { 
                        action: "show_result", 
                        error: `Server Lỗi: ${data.error}` 
                    });
                }
            } catch (e) {
                chrome.tabs.sendMessage(tab.id, { 
                    action: "show_result", 
                    error: "Không thể kết nối tới Server Local (localhost:5000)" 
                });
            }
        });
    }
});
