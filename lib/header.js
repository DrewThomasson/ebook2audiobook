()=>{
	try{
		let gr_root = (window.gradioApp && window.gradioApp()) || document;
		let gr_checkboxes;
		let gr_radios;
		let gr_voice_player_hidden;
		let gr_audiobook_vtt;
		let gr_audiobook_sentence;
		let gr_audiobook_player;
		let gr_playback_time;
		let gr_progress;
		let gr_voice_play;
		let gr_ebook_textarea;
		let tabs_open = false;
		let init_elements_timeout;
		let init_audiobook_player_timeout;
		let audio_filter = "none";
		let cues = [];
		if(typeof window.onElementAvailable !== "function"){
			window.onElementAvailable = (selector, callback, { root = (window.gradioApp && window.gradioApp()) || document, once = false } = {})=> {
				const seen = new WeakSet();
				const fireFor = (context) => {
					context.querySelectorAll(selector).forEach((el) => {
						if (seen.has(el)) return;
						const success = callback(el);
						if (success !== false) {
							// Mark as seen only if callback succeeded
							seen.add(el);
							if (once) return;
						} else {
							// Retry check later (in case conditions weren’t met yet)
							setTimeout(() => fireFor(root), 300);
						}
					});
				};
				fireFor(root);
				const observer = new MutationObserver((mutations) => {
					for (const m of mutations) {
						for (const n of m.addedNodes) {
							if (n.nodeType !== 1) continue;
							if (n.matches?.(selector)) {
								if (!seen.has(n)) {
									const success = callback(n);
									if (success !== false) {
										seen.add(n);
										if (once) {
											observer.disconnect();
											return;
										}
									} else {
										setTimeout(() => fireFor(root), 300);
									}
								}
							} else {
								fireFor(n);
							}
						}
					}
				});
				observer.observe(root, { childList: true, subtree: true });
				return () => observer.disconnect();
			}
		}
		if(typeof window.init_interface !== "function"){
			window.init_interface = ()=>{
				try {
					gr_root = (window.gradioApp && window.gradioApp()) || document;
					gr_progress = (gr_root) ? gr_root.querySelector("#gr_progress") : undefined;
					if(!gr_root || !gr_progress){
						clearTimeout(init_elements_timeout);
						console.warn("Components not ready… retrying");
						init_elements_timeout = setTimeout(init_interface, 1000);
						return;
					}
					// Function to apply theme borders
					function applyThemeBorders(){
						const url = new URL(window.location);
						const theme = url.searchParams.get("__theme");
						let elColor = "#666666";
						if(theme == "dark"){
							elColor = "#fff";
						}else if(!theme){
							const osTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
							if(osTheme){
								elColor = "#fff";
							}
						}
						gr_root.querySelectorAll("input[type='checkbox'], input[type='radio']")
							.forEach(cb => cb.style.border = "1px solid " + elColor);
					}
					// Run once on init
					applyThemeBorders();
					// Re-run when DOM changes (tabs, redraws, etc.)
					new MutationObserver(applyThemeBorders).observe(gr_root, {
						childList: true,
						subtree: true
					});
					// Keep your progress observer
					new MutationObserver(tab_progress).observe(gr_progress, {
						attributes: true,
						childList: true,
						subtree: true,
						characterData: true
					});
					// new MutationObserver(tab_progress).observe(gr_progress.parentElement, { ... });
					// gr_progress.addEventListener("change", tab_progress);
					if(!window._tab_progress_interval){
						window._tab_progress_interval = setInterval(tab_progress, 500);
					}
					window.gr_ebook_textarea_counter();
				}catch(e){
					console.warn("init_interface error:", e);
				}
			};
		}
		if(typeof(window._restoreSlider) !== "function"){
			window._restoreSlider = (slider, parseFn = parseFloat)=>{
				if(!slider) return;
				const container = slider.closest("div[id]");
				if(!container) return;
				const key = container.id.replace(/^gr_/, "");
				const saved = window.session_storage?.[key];
				if(saved === undefined || saved === null || saved === ""){
					return;
				}
				const parsed = parseFn(saved);
				if(!Number.isFinite(parsed)){
					return;
				}
				slider.value = parsed;
				slider.dispatchEvent(new Event("input", { bubbles: true }));
			};
		}
		if(typeof(window.init_xtts_sliders) !== "function"){
			window.init_xtts_sliders = ()=>{
				try{
					const q = (id) => gr_root.querySelector(`#gr_${id} input[type=number]`);
					window._restoreSlider(q("xtts_temperature"));
					window._restoreSlider(q("xtts_repetition_penalty"));
					window._restoreSlider(q("xtts_top_k"), (v) => parseInt(v, 10));
					window._restoreSlider(q("xtts_top_p"));
					window._restoreSlider(q("xtts_speed"));
				}catch(e){
					console.warn("init_xtts_sliders error:", e);
				}
			};
		}
		if(typeof(window.init_bark_sliders) !== "function"){
			window.init_bark_sliders = ()=>{
				try{
					const q = (id) => gr_root.querySelector(`#gr_${id} input[type=number]`);
					window._restoreSlider(q("bark_text_temp"));
					window._restoreSlider(q("bark_waveform_temp"));
				}catch(e){
					console.warn("init_bark_sliders error:", e);
				}
			};
		}
		if(typeof window.init_voice_player_hidden !== "function"){
			window.init_voice_player_hidden = ()=>{
				try{
					const gr_voice_player_hidden = gr_root.querySelector("#gr_voice_player_hidden audio");
					const gr_voice_play = gr_root.querySelector("#gr_voice_play");
					if(gr_voice_player_hidden && gr_voice_play){
						if(gr_voice_play.dataset.bound === "true") return;
						gr_voice_play.dataset.bound = "true";
						gr_voice_player_hidden.addEventListener("loadeddata", ()=>{
							gr_voice_play.textContent = "▶";
						});
						gr_voice_play.addEventListener("click", ()=>{
							if(gr_voice_player_hidden.paused){
								gr_voice_player_hidden.play().then(()=>{
									gr_voice_play.textContent = "⏸";
								}).catch(err => console.warn("Play failed:", err));
							}else{
								gr_voice_player_hidden.pause();
								gr_voice_play.textContent = "▶";
							}
						});
						gr_voice_player_hidden.addEventListener("pause", ()=>{
							gr_voice_play.textContent = "▶";
						});
						gr_voice_player_hidden.addEventListener("ended", ()=>{
							gr_voice_play.textContent = "▶";
						});
						gr_voice_player_hidden.addEventListener("play", ()=>{
							const v = window.session_storage?.playback_volume ?? 1;
							gr_voice_player_hidden.volume = v;
						});
						return true;
					}
				}catch(e){
					console.warn("init_voice_player_hidden error:", e);
				}
				return false;
			};
		}
		if(typeof(window.init_audiobook_player) !== "function"){
			window.init_audiobook_player = (el)=>{
				try{
					gr_root = (window.gradioApp && window.gradioApp()) || document;
					if(!gr_root){
						return false;
					}
					const player = (el && el.isConnected) ? el : gr_root.querySelector("#gr_audiobook_player audio");
					if(!player){
						return false;
					}
					gr_audiobook_player = player;
					if(player.dataset.bound === "true"){
						return true;
					}
					player.dataset.bound = "true";
					let lastCue = null;
					let fade_timeout = null;
					let raf_id = null;
					function q_sentence(){
						if(!gr_audiobook_sentence || !gr_audiobook_sentence.isConnected){
							gr_audiobook_sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
						}
						return gr_audiobook_sentence;
					}
					function q_playback_time(){
						if(!gr_playback_time || !gr_playback_time.isConnected){
							gr_playback_time = gr_root.querySelector("#gr_playback_time input, #gr_playback_time textarea");
						}
						return gr_playback_time;
					}
					function push_time(value){
						const el = q_playback_time();
						if(!el){
							return false;
						}
						el.value = String(value);
						el.dispatchEvent(new Event("input", {bubbles: true}));
						return true;
					}
					function safe_volume(value){
						const vol = parseFloat(value);
						return Number.isFinite(vol) ? Math.min(Math.max(vol, 0), 1) : 1;
					}
					function is_playing(){
						return !!(player.isConnected && !player.paused && !player.ended && player.readyState >= 2);
					}
					function start_playback(){
						if(raf_id === null && is_playing()){
							raf_id = requestAnimationFrame(trackPlayback);
						}
					}
					function stop_playback(){
						if(raf_id !== null){
							cancelAnimationFrame(raf_id);
							raf_id = null;
						}
					}
					function trackPlayback(){
						raf_id = null;
						try{
							window.session_storage.playback_time = parseFloat(player.currentTime);
							const sentence = q_sentence();
							const cue = findCue(window.session_storage.playback_time);
							if(sentence && cue && cue !== lastCue){
								if(fade_timeout){
									sentence.style.opacity = "1";
								}else{
									sentence.style.opacity = "0";
								}
								sentence.style.transition = "none";
								sentence.value = cue.text;
								clearTimeout(fade_timeout);
								fade_timeout = setTimeout(() => {
									const el = q_sentence();
									if(el){
										el.style.transition = "opacity 0.15s ease-in";
										el.style.opacity = "1";
									}
									fade_timeout = null;
								}, 33);
								lastCue = cue;
							}else if(!cue && lastCue !== null){
								lastCue = null;
							}
						}catch(e){
							console.warn("gr_audiobook_player tracking error:", e);
						}
						if(is_playing()){
							raf_id = requestAnimationFrame(trackPlayback);
						}
					}
					player.addEventListener("loadeddata", ()=>{
						player.style.transition = "filter 1s ease";
						player.style.filter = audio_filter;
						player.currentTime = parseFloat(window.session_storage?.playback_time) || 0;
						player.volume = safe_volume(window.session_storage?.playback_volume);
					});
					player.addEventListener("play", start_playback);
					player.addEventListener("playing", start_playback);
					player.addEventListener("waiting", stop_playback);
					player.addEventListener("pause", ()=>{
						stop_playback();
						push_time(player.currentTime);
					});
					player.addEventListener("seeked", ()=>{
						window.session_storage.playback_time = player.currentTime;
						stop_playback();
						trackPlayback();
					});
					player.addEventListener("ended", ()=>{
						stop_playback();
						const sentence = q_sentence();
						if(sentence){
							sentence.value = "…";
						}
						window.session_storage.playback_time = 0;
						lastCue = null;
						push_time(0);
					});
					player.addEventListener("emptied", stop_playback);
					player.addEventListener("abort", stop_playback);
					player.addEventListener("error", stop_playback);
					player.addEventListener("volumechange", ()=>{
						window.session_storage.playback_volume = player.volume;
						gr_voice_player_hidden = gr_root.querySelector("#gr_voice_player_hidden audio");
						if(gr_voice_player_hidden){
							gr_voice_player_hidden.volume = player.volume;
							gr_voice_player_hidden.dispatchEvent(new Event("volumechange", { bubbles: true }));
						}
					});
					const themURL = new URL(window.location);
					const theme = themURL.searchParams.get("__theme");
					const is_dark = theme ? (theme === "dark") : !!window.matchMedia?.("(prefers-color-scheme: dark)").matches;
					// Gecko draws a dark native control bar, Blink/WebKit a light one
					const native_dark = !!window.CSS?.supports?.("selector(::-moz-range-thumb)");
					audio_filter = (is_dark !== native_dark) ? "invert(1) hue-rotate(180deg)" : "none";
					player.style.transition = "filter 1s ease";
					player.style.filter = audio_filter;
					player.volume = safe_volume(window.session_storage?.playback_volume);
					q_sentence();
					q_playback_time();
					start_playback();
					return true;
				}catch(e){
					console.warn("init_audiobook_player error:", e);
				}
				return false;
			};
		}
		if(typeof window.gr_ebook_textarea_counter !== "function"){
			window.gr_ebook_textarea_counter = function(){
				const container = document.querySelector("#gr_ebook_textarea");
				if(container){
					const textarea = container.querySelector("textarea");
					const max_ebook_textarea_length = textarea.maxLength;
					const ebook_textarea_toolbar = document.querySelector("#ebook_textarea_toolbar");
					document.querySelector("#ebook_textarea_toolbar")?.remove();
					container.style.position = "relative";
					const toolbar = document.createElement("div");
					toolbar.id = toolbar.name = "ebook_textarea_toolbar";
					toolbar.style.cssText = "position:absolute;top:4px;right:8px;display:flex;align-items:center;gap:6px;z-index:1;";
					const counter = document.createElement("span");
					counter.style.cssText = "font-size:0.85em;color:var(--body-text-color);";
					counter.textContent = textarea.value.length + " / " + max_ebook_textarea_length;
					toolbar.appendChild(counter);
					const btn = document.createElement("button");
					btn.textContent = "🗑";
					btn.id = btn.name = "clear_ebook_textarea";
					btn.className = "micro-btn";
					btn.addEventListener("click", ()=>{
						textarea.value = "";
						textarea.dispatchEvent(new Event("input", {bubbles: true}));
						counter.textContent = "0 / " + max_ebook_textarea_length;
						counter.style.color = "var(--body-text-color)";
					});
					textarea.addEventListener("input", ()=>{
						const len = textarea.value.length;
						counter.textContent = len + " / " + max_ebook_textarea_length;
						counter.style.color = len >= max_ebook_textarea_length ? "red" : "var(--body-text-color)";
					});
					toolbar.appendChild(btn);
					container.appendChild(toolbar);
				}
			};
		}
		if(typeof(window.tab_progress) !== "function"){
			window.tab_progress = ()=>{
				try{
					const gr_root = (window.gradioApp && window.gradioApp()) || document;
					const el = gr_root.querySelector("#gr_progress");
					const val = el?.value || el?.textContent || "";
					const valArray = splitAtLastDash(val);
					if(valArray[1]){
						const title = valArray[0].trim().split(/ (.*)/)[1].trim();
						const percentage = valArray[1].trim();
						const titleShort = title.length >= 20 ? title.slice(0, 20).trimEnd() + "…" : title;
						document.title = titleShort + ": " + percentage;
					}else{
						document.title = "Ebook2Audiobook";
					}
				}catch(e){
					console.warn("tab_progress error:", e);
				}
			};
		}
		if(typeof(window.splitAtLastDash) !== "function"){
			window.splitAtLastDash = function(s){
				const idx = s.lastIndexOf("-");
				if(idx === -1){
					return [s];
				}
				return [s.slice(0, idx).trim(), s.slice(idx + 1).trim()];
			};
		}
		if(typeof(window.load_vtt) !== "function"){
			window.load_vtt = ()=>{
				try{
					gr_audiobook_vtt = gr_root.querySelector("#gr_audiobook_vtt textarea");
					gr_audiobook_sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
					if(gr_audiobook_sentence){
						gr_audiobook_sentence.style.fontSize = "14px";
						gr_audiobook_sentence.style.fontWeight = "bold";
						gr_audiobook_sentence.style.width = "100%";
						gr_audiobook_sentence.style.height = "auto";
						gr_audiobook_sentence.style.textAlign = "center";
						gr_audiobook_sentence.style.margin = "0";
						gr_audiobook_sentence.style.padding = "7px 0 7px 0";
						gr_audiobook_sentence.style.lineHeight = "14px";
						const txt = gr_audiobook_vtt.value;
						if(txt == ""){
							gr_audiobook_sentence.value = "…";
						}else{
							parseVTT(txt);
						}
					}
				}catch(e){
					console.warn("load_vtt error:", e);
				}
			};
		}
		if(typeof(window.parseVTT) !== "function"){
			 window.parseVTT = (vtt)=>{
				function pushCue(){
					if(start !== null && end !== null && textBuffer.length){
						cues.push({ start, end, text: textBuffer.join("\n") });
					}
					start = end = null;
					textBuffer.length = 0;
				}
				const lines = vtt.split(/\r?\n/);
				const timePattern = /(\d{2}:)?\d{2}:\d{2}\.\d{3}/;
				let start = null, end = null;
				cues = [];
				const textBuffer = [];
				for(let i = 0, len = lines.length; i < len; i++){
					const line = lines[i];
					if(!line.trim()){ pushCue(); continue; }
					if(line.includes("-->")){
						const [s, e] = line.split("-->").map(l => l.trim().split(" ")[0]);
						if(timePattern.test(s) && timePattern.test(e)){
							start = toSeconds(s);
							end = toSeconds(e);
						}
					}else if(!timePattern.test(line)){
						textBuffer.push(line);
					}
				}
				pushCue();
			}
		}
		if(typeof(window.toSeconds) !== "function"){
			window.toSeconds = function(ts){
				const parts = ts.split(":");
				if(parts.length === 3){
					return parseInt(parts[0], 10) * 3600 +
						   parseInt(parts[1], 10) * 60 +
						   parseFloat(parts[2]);
				}
				return parseInt(parts[0], 10) * 60 + parseFloat(parts[1]);
			};
		}
		if(typeof(window.findCue) !== "function"){
			window.findCue = function(time){
				let lo = 0, hi = cues.length - 1;
				while(lo <= hi){
					const mid = (lo + hi) >> 1;
					const cue = cues[mid];
					if(time < cue.start){
						hi = mid - 1;
					}else if(time >= cue.end){
						lo = mid + 1;
					}else{
						return cue;
					}
				}
				return null;
			};
		}
		if(typeof(window.show_glassmask) !== "function"){
			window.show_glassmask = function(msg){
				let glassmask = document.querySelector("#gr_glassmask");
				if(!glassmask){
					glassmask = document.createElement("div");
					glassmask.id = "gr_glassmask";
					document.body.appendChild(glassmask);
				}
				glassmask.className = "gr-glass-mask";
				glassmask.innerHTML = `${msg}`;
			};
		}
		if(typeof(window.create_uuid) !== "function"){
			window.create_uuid = function(){
				try{
					return crypto.randomUUID();
				}catch(e){
					return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c =>{
						const r = Math.random() * 16 | 0;
						const v = c === "x" ? r : (r & 0x3 | 0x8);
						return v.toString(16);
					});
				}
			};
		}
		//////////////////////
		const bc = new BroadcastChannel("E2A-channel");
		const tab_id = create_uuid();
		const currentStorage = localStorage.getItem("data");
		if(currentStorage){
			window.session_storage = JSON.parse(currentStorage);
			window.session_storage.tab_id = tab_id;
			if(window.session_storage.playback_volume === 0){
				window.session_storage.playback_volume = 1.0;
			}
		}else{
			window.session_storage = {};
			window.session_storage.playback_time = 0;
			window.session_storage.playback_volume = 1.0;
		}
		bc.onmessage = (event)=>{
			try{
				const msg = event.data;
				if(!msg || msg.senderId === tab_id){
					return;
				}
				switch (msg.type){
					case "check-existing":
						bc.postMessage({ type: "already-open", senderId: tab_id });
						break;
					case "already-open":
						tabs_open = true;
						break;
					case "new-tab-open":
						show_glassmask(msg.text);
						break;
				}
			}catch(e){
				console.warn("bc.onmessage error:", e);
			}
		};
		window.addEventListener("beforeunload", ()=>{
			try{
				const newStorage = JSON.parse(localStorage.getItem("data") || "{}");
				if(newStorage.tab_id == window.session_storage.tab_id || !newStorage.tab_id){
					delete newStorage.tab_id;
					delete newStorage.status;
					newStorage.playback_time = Number(window.session_storage.playback_time);
					newStorage.playback_volume = parseFloat(window.session_storage.playback_volume);
					localStorage.setItem("data", JSON.stringify(newStorage));
				}
			}catch(e){
				console.warn("Error updating status on unload:", e);
			}
		});
		window.onElementAvailable("input:not([type='hidden']), textarea", (el)=>{
			el.setAttribute("autocomplete", "off");
		}, {once: false});
		window.onElementAvailable("#gr_voice_player_hidden audio", (el)=>{
			return window.init_voice_player_hidden();
		}, {once: false});
		window.onElementAvailable("#gr_audiobook_player audio", (el)=>{
			return window.init_audiobook_player(el);
		}, {once: false});
		window.onElementAvailable("#gr_playback_time input, #gr_playback_time textarea", (el)=>{
			gr_playback_time = el;
		}, {once: false});
		window.onElementAvailable("#gr_audiobook_sentence textarea", (el)=>{
			gr_audiobook_sentence = el;
		}, {once: false});
		if (!window._fetch_patched) {
			const originalFetch = window.fetch;
			window._original_fetch = window._original_fetch || originalFetch;
			window.fetch = async function(url, options) {
				if (typeof url === "string" && url.includes("/upload") && options?.body instanceof FormData){
					let has_files = false;
					for(const [, value] of options.body.entries()){
						if(value instanceof File && value.size > 0){
							has_files = true;
							break;
						}
					}
					if(!has_files){
						console.warn("Blocked empty folder upload");
						return new Response(JSON.stringify([]), {
							status: 200,
							headers: {"Content-Type": "application/json"},
						});
					}
				}
				return window._original_fetch.apply(this, arguments);
			};
			window._fetch_patched = true;
		}
		try{
			bc.postMessage({ type: "check-existing", senderId: tab_id });
			setTimeout(()=>{
				if(tabs_open){
					bc.postMessage({
						type: "new-tab-open",
						text: "Session expired.<br/>You can close this window",
						senderId: tab_id
					});
				}
			}, 250);
		}catch(e){
			console.warn("bc.postMessage error:", e);
		}
		return window.session_storage;
	}catch(e){
		console.warn("gr_raed_data js error:", e);
	}
	return null;
}