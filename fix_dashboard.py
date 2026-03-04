
content = """
<!DOCTYPE html>
<!-- Agenticana v6.0 Secretary Bird Edition 🦅 — High-End Dashboard -->
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agenticana | Sovereign Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Grotesk:wght@300;500;700&display=swap" rel="stylesheet">
    <script>
        window.tailwindConfig = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Outfit', 'sans-serif'],
                        display: ['Space Grotesk', 'sans-serif'],
                    },
                    colors: {
                        bird: {
                            deep: '#030712',
                            slate: '#111827',
                            accent: '#38bdf8',
                            success: '#10b981',
                            gold: '#f59e0b',
                            crimson: '#ef4444',
                        }
                    }
                }
            }
        };
        // Use timeout to ensure tailwind is ready
        setTimeout(() => { if (window.tailwind) window.tailwind.config = window.tailwindConfig; }, 100);
    </script>
    <style>
        body { background-color: #030712; color: #f1f5f9; }
        .glass { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.05); }
        .bird-gradient { background: linear-gradient(135deg, #38bdf8 0%, #1e40af 100%); }
        .glow-accent { box-shadow: 0 0 30px rgba(56, 189, 248, 0.15); }
        .stomp-shadow { box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .card-hover:hover { border-color: rgba(56, 189, 248, 0.3); transform: translateY(-2px); transition: all 0.3s; }
    </style>
</head>
<body class="min-h-screen py-6 px-4 md:px-12 font-sans">
    <div class="max-w-[1600px] mx-auto">

        <!-- TOP NAVIGATION -->
        <nav class="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 bird-gradient rounded-2xl flex items-center justify-center text-3xl shadow-lg stomp-shadow">🦅</div>
                <div>
                    <h1 class="text-3xl font-display font-bold tracking-tight">Agenticana <span class="text-bird-accent">v6.0</span></h1>
                    <div class="flex items-center gap-2 text-xs text-slate-500 uppercase tracking-widest font-semibold mt-1">
                        <span class="w-2 h-2 rounded-full bg-bird-success animate-pulse"></span>
                        Sovereign Loop Active
                    </div>
                </div>
            </div>

            <div class="flex gap-4">
                <div class="glass px-6 py-3 rounded-2xl flex items-center gap-4 border-bird-accent/20">
                    <div class="text-right">
                        <p class="text-[10px] text-slate-500 uppercase font-bold tracking-tighter">System Health</p>
                        <p class="text-sm font-bold text-bird-accent" id="status-text">SYNCING...</p>
                    </div>
                    <div class="h-8 w-px bg-white/10"></div>
                    <button onclick="localStorage.removeItem('agentica_auth'); location.reload();" class="text-xs text-slate-400 hover:text-white transition-colors">Logout</button>
                </div>
            </div>
        </nav>

        <!-- MAIN GRID -->
        <div class="grid grid-cols-1 xl:grid-cols-12 gap-8">

            <!-- LEFT COLUMN: INTEL & SWARM -->
            <div class="xl:col-span-8 space-y-8">

                <!-- MARKET INTELLIGENCE (MASSIVE FEED) -->
                <section class="glass rounded-[40px] p-8 glow-accent border-bird-accent/10">
                    <div class="flex justify-between items-end mb-8">
                        <div>
                            <h2 class="text-2xl font-display font-bold">Market Intelligence Swarm</h2>
                            <p class="text-slate-400 text-sm mt-1">Tracking 11 competitors for feature gaps & weaknesses.</p>
                        </div>
                        <div class="bg-bird-accent/10 px-4 py-2 rounded-xl text-bird-accent border border-bird-accent/20 font-bold text-xs uppercase">
                            Autonomous Tracking
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 h-[400px] overflow-y-auto scrollbar-hide pr-2" id="intel-grid">
                        <!-- Intel Cards Injected Here -->
                        <div class="flex items-center justify-center col-span-full h-full text-slate-600 italic">
                            Scanning repositories for gaps...
                        </div>
                    </div>
                </section>

                <!-- BRAIN DEBATE CHAMBER (SIMULACRUM) -->
                <section class="glass rounded-[40px] p-8 border-white/5 relative overflow-hidden">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="text-2xl font-display font-bold flex items-center gap-3">
                            <span class="p-2 bird-gradient rounded-lg text-lg">🧠</span>
                            Debate Chamber
                        </h2>
                        <div id="debate-status" class="text-xs font-mono text-bird-gold bg-bird-gold/10 px-3 py-1 rounded-full border border-bird-gold/20">
                            IDLE
                        </div>
                    </div>

                    <div class="bg-bird-deep/50 rounded-3xl p-6 min-h-[300px] border border-white/5 mb-6" id="debate-content">
                        <p class="text-slate-500 italic text-center mt-12">Launch a new swarm to see agent debates in real-time.</p>
                    </div>

                    <div class="flex justify-between items-center bg-white/5 -mx-8 -mb-8 px-8 py-4">
                        <div class="text-xs text-slate-500">
                            Target Topic: <span class="text-slate-300 font-semibold" id="debate-topic">None</span>
                        </div>
                        <div class="flex -space-x-2" id="debate-agents">
                            <!-- Agent Avatars -->
                        </div>
                    </div>
                </section>
            </div>

            <!-- RIGHT COLUMN: STATUS & QUICK ACTIONS -->
            <div class="xl:col-span-4 space-y-8">

                <!-- QUICK ACTIONS (NON-DEV FRIENDLY) -->
                <section class="bird-gradient rounded-[40px] p-8 text-white stomp-shadow">
                    <h3 class="text-xl font-display font-bold mb-4">Evolution Commands</h3>
                    <p class="text-blue-100 text-sm mb-8">Force Agenticana to self-improve based on identified market gaps.</p>

                    <div class="space-y-3">
                        <button id="btn-intel" class="w-full bg-white text-bird-deep font-bold py-4 rounded-2xl hover:bg-bird-accent hover:text-white transition-all transform hover:scale-[1.02]">
                            🔍 Scan Competitors
                        </button>
                        <button id="btn-evolve" class="w-full bg-white/10 text-white border border-white/20 font-bold py-4 rounded-2xl hover:bg-white/20 transition-all">
                            🚀 Self-Evolve (P25)
                        </button>
                        <button id="btn-audit" class="w-full bg-white/10 text-white border border-white/20 font-bold py-4 rounded-2xl hover:bg-white/20 transition-all">
                            🛡️ Health Audit
                        </button>
                    </div>
                </section>

                <!-- SYSTEM STATS -->
                <section class="glass rounded-[40px] p-8 border-white/5">
                    <h3 class="text-lg font-display font-bold mb-6">Sovereign Stats</h3>
                    <div class="space-y-6">
                        <div class="flex justify-between items-center">
                            <span class="text-slate-400 text-sm">Soul Memory</span>
                            <span class="font-display font-bold text-bird-accent text-xl" id="stat-memory">0</span>
                        </div>
                        <div class="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                            <div class="h-full bg-bird-accent w-[60%]"></div>
                        </div>

                        <div class="flex justify-between items-center">
                            <span class="text-slate-400 text-sm">Agent Registry</span>
                            <span class="font-display font-bold text-bird-success text-xl" id="stat-registry">0</span>
                        </div>
                        <div class="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                            <div class="h-full bg-bird-success w-[85%]"></div>
                        </div>

                        <div class="flex justify-between items-center">
                            <span class="text-slate-400 text-sm">Market Snapshot</span>
                            <span class="font-display font-bold text-bird-gold text-xl" id="stat-intel">0</span>
                        </div>
                        <div class="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                            <div class="h-full bg-bird-gold w-[100%]"></div>
                        </div>
                    </div>
                </section>

                <!-- ACTIVE SWARM (LIVE FEED) -->
                <section class="glass rounded-[40px] p-8 border-bird-accent/5 overflow-hidden">
                    <h3 class="text-sm font-bold uppercase tracking-widest text-slate-500 mb-4">Shadow Swarm Feed</h3>
                    <div id="swarm-feed" class="space-y-2 max-h-[300px] overflow-y-auto pr-2 scrollbar-hide text-[10px] font-mono">
                        <!-- Swarm logs injected here -->
                        <p class="text-slate-600 italic">No active operations...</p>
                    </div>
                </section>
            </div>
        </div>
    </div>

    <!-- SCRIPTS -->
    <script>
        const AUTH_KEY = localStorage.getItem('agentica_auth') || new URLSearchParams(window.location.search).get('auth');

        if (!AUTH_KEY) {
            const key = prompt("Enter Agentica Auth Key:");
            if (key) {
                localStorage.setItem('agentica_auth', key);
                location.reload();
            }
        }

        async function runTask(task) {
            if (!AUTH_KEY) return;
            try {
                const response = await fetch('/api/run?task=' + task, {
                    headers: { 'X-Agentica-Auth': AUTH_KEY }
                });
                if (response.ok) {
                    console.log('Task ' + task + ' started');
                }
            } catch (err) {
                console.error("Failed to run task:", err);
            }
        }

        // Attach listeners after DOM load
        document.addEventListener('DOMContentLoaded', () => {
            const btnIntel = document.getElementById('btn-intel');
            if (btnIntel) btnIntel.addEventListener('click', () => runTask('intel'));

            const btnEvolve = document.getElementById('btn-evolve');
            if (btnEvolve) btnEvolve.addEventListener('click', () => runTask('evolve'));

            const btnAudit = document.getElementById('btn-audit');
            if (btnAudit) btnAudit.addEventListener('click', () => runTask('audit'));
        });

        async function updateDashboard() {
            if (!AUTH_KEY) return;
            try {
                const response = await fetch('/api/status', {
                    headers: { 'X-Agentica-Auth': AUTH_KEY }
                });

                if (response.status === 401) {
                    localStorage.removeItem('agentica_auth');
                    location.reload();
                    return;
                }

                const data = await response.json();

                // Update Stats
                const mem = document.getElementById('stat-memory');
                if (mem) mem.innerText = data.vector_memory || 0;

                const reg = document.getElementById('stat-registry');
                if (reg) reg.innerText = data.registry || 0;

                const intel = document.getElementById('stat-intel');
                if (intel) intel.innerText = data.intel ? data.intel.length : 0;

                const st = document.getElementById('status-text');
                if (st) st.innerText = "SYSTEM SYNCED";

                // Update Intel
                const intelGrid = document.getElementById('intel-grid');
                if (intelGrid && data.intel && data.intel.length > 0) {
                    intelGrid.innerHTML = '';
                    data.intel.forEach(repo => {
                        const card = document.createElement('div');
                        card.className = "glass p-5 rounded-3xl border-white/5 card-hover flex flex-col justify-between";
                        const gaps = repo.trending_requests || [];
                        card.innerHTML = '<div><h4 class="text-xs font-bold text-slate-400 uppercase mb-2 tracking-tighter">' + repo.name.split('/')[1] + '</h4><div class="space-y-2">' + (gaps.map(g => '<div class="bg-bird-accent/5 p-2 rounded-xl text-[10px] text-bird-accent font-semibold border border-bird-accent/10">↳ ' + g + '</div>').join('')) + '</div></div><div class="mt-4 flex justify-between items-center"><span class="text-[9px] text-slate-500 font-mono italic">Market Observation</span><span class="w-1.5 h-1.5 rounded-full bg-bird-accent"></span></div>';
                        intelGrid.appendChild(card);
                    });
                }

                // Update Simulacrum
                if (data.simulacrum) {
                    const status = document.getElementById('debate-status');
                    if (status) status.innerText = "VOTING COMPLETE";

                    const topic = document.getElementById('debate-topic');
                    if (topic) topic.innerText = data.simulacrum.topic;

                    const content = document.getElementById('debate-content');
                    if (content) {
                        let html = '<div class="space-y-4">';
                        data.simulacrum.transcript.slice(-4).forEach(entry => {
                            html += '<div class="flex gap-3"><div class="text-[10px] font-bold text-bird-accent w-24 shrink-0 uppercase">' + entry.speaker + '</div><div class="text-xs text-slate-300 italic">"' + entry.content.substring(0, 100) + '..."</div></div>';
                        });
                        html += '<div class="mt-6 pt-4 border-t border-white/5 text-sm font-bold text-bird-success">🏆 Winner: ' + data.simulacrum.winning_agent + '</div></div>';
                        content.innerHTML = html;
                    }
                }

                // Update Feed (Logs)
                if (data.logs && data.logs.length > 0) {
                    const feed = document.getElementById('swarm-feed');
                    if (feed) {
                        feed.innerHTML = '';
                        data.logs.forEach(line => {
                            const div = document.createElement('div');
                            div.className = "flex gap-2 py-0.5 border-l border-white/5 pl-2 truncate";
                            div.innerHTML = '<span class="text-slate-500">></span> <span class="text-slate-300">' + line.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</span>';
                            feed.appendChild(div);
                        });
                        feed.scrollTop = feed.scrollHeight;
                    }
                }

            } catch (err) {
                console.error("Dashboard Sync Failed:", err);
                const st = document.getElementById('status-text');
                if (st) st.innerText = "CONNECTION LOST";
            }
        }

        setInterval(updateDashboard, 3000);
        updateDashboard();
    </script>
</body>
</html>
"""
with open("dashboard/index.html", "w", encoding="utf-8") as f:
    f.write(content.strip())
