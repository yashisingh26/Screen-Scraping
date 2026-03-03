<h1 align="center">🖥 Screen-Scraping Monitor</h1>

<p align="center">
  <strong>Real-Time Screen Text Extraction | Multi-PC Monitoring | VPS Compatible</strong><br>
  Capture screen text on one machine and view it live on another using OCR + Flask backend.
</p>

<p align="center">
  <img src="https://github.com/yashisingh26/Screen-Scraping/blob/main/gui%20interface.png?raw=true" width="700">
</p>
<hr>

<h2>📌 Overview</h2>

Screen-Scraping Monitor is a distributed screen-text monitoring system that uses OCR (Optical Character Recognition) to extract visible screen text from one PC and stream it in real-time to another system via a lightweight Flask server.

It supports:

- LAN monitoring  
- VPS-based remote monitoring  
- Real-time viewer GUI  
- Search & time filtering  

<hr>

<h2>🏗 System Architecture</h2>

<pre>
 PC #1 (Target Machine)
 ┌────────────────────┐
 │   Reader Agent     │
 │  OCR + Timestamp   │
 └─────────┬──────────┘
           │  POST /upload
           ▼
     ┌────────────────┐
     │  Flask Server  │  (PC #2 / VPS)
     └────────┬───────┘
              │  GET /fetch
              ▼
   ┌────────────────────┐
   │   Receiver GUI     │
   │  Live Text Viewer  │
   └────────────────────┘
</pre>

<hr>

<h2>🌟 Core Components</h2>

<h3>🖥 Reader Agent (PC #1)</h3>
<ul>
  <li>Runs silently in background</li>
  <li>Captures screen using MSS</li>
  <li>Extracts text via EasyOCR</li>
  <li>Prevents duplicate messages</li>
  <li>Sends timestamped JSON data</li>
  <li>Optional Windows auto-start support</li>
</ul>

<h3>🌐 Flask Server</h3>
<ul>
  <li>Lightweight REST backend</li>
  <li>In-memory message storage</li>
  <li>Two API endpoints:
    <ul>
      <li><code>/upload</code> – Receive text from Reader</li>
      <li><code>/fetch</code> – Provide message history</li>
    </ul>
  </li>
</ul>

<h3>💻 Receiver GUI</h3>
<ul>
  <li>Real-time auto-refresh display</li>
  <li>Keyword search with highlight</li>
  <li>Time-based filtering:
    <ul>
      <li>All</li>
      <li>Today</li>
      <li>Yesterday</li>
      <li>Last 1 Hour</li>
      <li>Last 24 Hours</li>
    </ul>
  </li>
  <li>Clean scrollable interface</li>
</ul>

<hr>

<h2>📦 Installation</h2>

<h3>⚙ Requirements</h3>
<pre>Python 3.8+</pre>

<h3>📍 Install Reader Dependencies</h3>
<pre>
pip install easyocr mss numpy requests pystray pillow
</pre>

<h3>📍 Install Server Dependencies</h3>
<pre>
pip install flask
</pre>

<h3>📍 Install GUI Dependencies</h3>
<pre>
pip install requests
</pre>

<hr>

<h2>🚀 Setup Instructions</h2>

<h3>1️⃣ Start Server (PC #2 or VPS)</h3>

<pre>python server.py</pre>

Server runs at:

<pre>http://0.0.0.0:5000</pre>

---

<h3>2️⃣ Configure Reader (PC #1)</h3>

Inside <code>reader.py</code>:

<pre>
SERVER_URL = "http://SERVER_IP:5000/upload"
</pre>

Run:

<pre>python reader.py</pre>

---

<h3>3️⃣ Configure GUI (PC #2)</h3>

Inside <code>screen_receiver.py</code>:

<pre>
server_url = "http://SERVER_IP:5000/fetch"
</pre>

Run:

<pre>screen_receiver.py</pre>

<hr>

<h2>📡 VPS Deployment</h2>

To monitor globally:

<ul>
  <li>Deploy <code>server.py</code> on VPS</li>
  <li>Open port <code>5000</code> in firewall</li>
  <li>Set Reader to VPS public IP</li>
  <li>Set GUI to VPS public IP</li>
</ul>

<hr>

<h2>📤 Data Format</h2>

<h3>Reader → Server</h3>

<pre>
{
  "timestamp": "2025-11-23T16:20:10.510120",
  "messages": ["Hello", "Stock available?", "7 days sir"]
}
</pre>

<h3>Server → GUI</h3>

<pre>
[
  { "time": "2025-11-23T16:20:10.510120", "msg": "Hello" },
  { "time": "2025-11-23T16:20:12.121212", "msg": "Stock available?" }
]
</pre>

<hr>

<h2>📁 Project Structure</h2>

<pre>
Screen-Scraping/
│── reader.py
│── server.py
│── screen_receiver.py
│── requirements.txt
└── README.md
</pre>

<hr>

<h2>🔒 Security Notice</h2>

This project is intended strictly for:

- Educational use  
- Authorized monitoring  
- Research and testing  

Unauthorized surveillance or misuse may violate privacy and cybercrime laws.

<hr>

<h2>🛠 Future Improvements</h2>

<ul>
  <li>SQLite database storage</li>
  <li>Authentication system</li>
  <li>HTTPS support</li>
  <li>Docker deployment</li>
  <li>Web dashboard version</li>
</ul>

<hr>

<h2>📜 License</h2>

MIT License

<hr>

<h2 align="center">Developer : Yashi Singh</h2>
