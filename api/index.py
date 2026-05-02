from http.server import BaseHTTPRequestHandler
import json

class AmeenInterpreter:
    def __init__(self):
        self.vars = {}
        self.output = []
    
    def evaluate_expression(self, expr):
        expr = str(expr).strip()
        if expr in self.vars:
            return self.vars[expr]
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        try:
            return int(expr)
        except:
            pass
        for op in ['+', '-', '*', '/', '%']:
            if op in expr:
                parts = expr.split(op)
                if len(parts) == 2:
                    left = self.evaluate_expression(parts[0].strip())
                    right = self.evaluate_expression(parts[1].strip())
                    if op == '+':
                        return left + right
                    if op == '-':
                        return left - right
                    if op == '*':
                        return left * right
                    if op == '/':
                        return left // right if right != 0 else 0
                    if op == '%':
                        return left % right
        return expr
    
    def run(self, code):
        self.output = []
        lines = code.replace('\r', '').split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            parts = line.split()
            if not parts:
                continue
            kw = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            
            if kw == 'Bismillah':
                self.output.append("=== BISMILLAH ===\n")
            elif kw == 'Alhamdulillah':
                self.output.append("\n=== ALHAMDULILLAH ===")
            elif kw == 'Qul':
                result = ' '.join(str(self.evaluate_expression(a)) for a in args)
                self.output.append(result + '\n')
            elif kw == 'Maktub':
                if len(args) >= 3 and args[1] == '=':
                    self.vars[args[0]] = self.evaluate_expression(args[2])
                elif len(args) >= 2:
                    self.vars[args[0]] = self.evaluate_expression(args[1])
        
        return ''.join(self.output)

HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMEEN LANGUAGE - Islamic Programming Language</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:linear-gradient(135deg,#0a2e1c,#064e3b);font-family:'Courier New',monospace;min-height:100vh;padding:20px;}
        .container{max-width:1400px;margin:0 auto;}
        .header{text-align:center;padding:20px;background:rgba(0,0,0,0.5);border-radius:20px;margin-bottom:20px;border:1px solid #ffd700;}
        .header h1{font-size:2.5rem;background:linear-gradient(135deg,#ffd700,#ff8c00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .bismillah{color:#ffd700;font-size:1.2rem;margin:10px 0;}
        .credit{background:#1a1a2e;padding:15px;border-radius:15px;text-align:center;margin-bottom:20px;border:1px solid #ffd700;}
        .credit p{color:#ffd700;font-size:1rem;}
        .credit span{color:#ff8c00;font-weight:bold;}
        .grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;}
        .panel{background:#0a0a1a;border-radius:15px;padding:20px;border:1px solid #ffd700;}
        .panel h3{color:#ffd700;margin-bottom:15px;border-bottom:1px solid #ffd700;padding-bottom:5px;}
        textarea{width:100%;height:400px;background:#1a1a2e;color:#00ff41;border:1px solid #ffd700;border-radius:10px;padding:15px;font-family:'Courier New',monospace;font-size:14px;resize:vertical;}
        .output-box{width:100%;height:400px;background:#1a1a2e;color:#00ff41;border:1px solid #ffd700;border-radius:10px;padding:15px;overflow-y:auto;white-space:pre-wrap;}
        button{background:linear-gradient(135deg,#ffd700,#ff8c00);color:#0a0a1a;border:none;padding:12px 24px;border-radius:10px;font-weight:bold;cursor:pointer;margin:10px 5px;font-size:1rem;}
        button:hover{opacity:0.9;transform:scale(0.98);}
        .example-btn{background:#1a1a2e;color:#ffd700;border:1px solid #ffd700;margin:5px;padding:8px 12px;font-size:12px;}
        .keyword-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px;margin-top:15px;}
        .keyword-item{background:#1a1a2e;color:#ffd700;padding:8px;border-radius:8px;font-size:12px;text-align:center;cursor:pointer;border:1px solid #ffd700;}
        .keyword-item:hover{background:#ffd700;color:#0a0a1a;}
        .install-box{background:#1a1a2e;padding:20px;border-radius:15px;margin-top:20px;border:1px solid #00ff41;}
        .install-box h3{color:#ffd700;margin-bottom:15px;}
        .install-box pre{background:#0a0a1a;padding:15px;border-radius:10px;overflow-x:auto;color:#00ff41;font-size:12px;}
        .footer{text-align:center;margin-top:30px;padding:20px;color:#ffd700;font-size:12px;}
        .status{padding:10px;margin-top:10px;border-radius:10px;text-align:center;}
        .status.success{background:#1a5a2e;color:#00ff41;}
        .status.error{background:#5a1a2e;color:#ff4444;}
        @media (max-width:768px){.grid{grid-template-columns:1fr;}}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🕌 AMEEN LANGUAGE 🕌</h1>
        <div class="bismillah">بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</div>
        <div class="bismillah">In the name of Allah, the Most Gracious, the Most Merciful</div>
    </div>
    <div class="credit">
        <p>⚡ DEVELOPED BY <span>ERROR</span> | ERROR-NEXUS ⚡</p>
        <p>Islamic Programming Language | Complete Freedom | No Boundaries</p>
    </div>
    <div class="grid">
        <div class="panel">
            <h3>✍️ WRITE AMEEN CODE</h3>
            <textarea id="code" placeholder='Example:
Bismillah
Qul "Assalamu Alaikum"
Maktub x = 10
Maktub y = 20
Maktub result = x + y
Qul "Result: " result
Alhamdulillah'></textarea>
            <br>
            <button onclick="runCode()">▶ RUN CODE (InshaAllah)</button>
            <button onclick="clearOutput()">🗑 CLEAR OUTPUT</button>
            <button onclick="copyCode()">📋 COPY CODE</button>
        </div>
        <div class="panel">
            <h3>📤 OUTPUT</h3>
            <div class="output-box" id="output">═══════════════════════════<br>AMEEN LANGUAGE READY<br>═══════════════════════════<br></div>
            <div id="status"></div>
        </div>
    </div>
    <div class="install-box">
        <h3>🔑 ISLAMIC KEYWORDS</h3>
        <div class="keyword-grid" id="keywords"></div>
    </div>
    <div class="install-box">
        <h3>📚 EXAMPLE CODES</h3>
        <button class="example-btn" onclick="loadExample('calc')">➕ Calculator</button>
        <button class="example-btn" onclick="loadExample('table')">✖ Table</button>
        <button class="example-btn" onclick="loadExample('evenodd')">🔢 Even/Odd</button>
        <button class="example-btn" onclick="loadExample('hello')">🌙 Hello</button>
        <div id="examplecode"></div>
    </div>
    <div class="install-box">
        <h3>🖥️ TERMUX INSTALLATION</h3>
        <pre>pkg update && pkg upgrade -y
pkg install python git -y
pip install flask
git clone https://github.com/ERROR-NEXUS/ameen-language.git
cd ameen-language
python app.py</pre>
        <p style="color:#ffd700">🌐 DEPLOY ON VERCEL</p>
        <pre>vercel --prod</pre>
        <p style="color:#ffd700">📁 FILE EXTENSION: <strong style="color:#00ff41">.ameen</strong></p>
    </div>
    <div class="footer">
        <p>© 2025 ERROR-NEXUS | AMEEN LANGUAGE | Islamic Programming Language</p>
        <p>🤲 "Read in the name of your Lord who created" - Al-Alaq 96:1</p>
    </div>
</div>
<script>
const keywordsList = ['Bismillah','Alhamdulillah','Maktub','Tajdid','Qul','Qawl','Istima','Amal','Radd','Dua','InshaAllah','Amma','Illa','SubhanAllah','Tawaf','Astadu','Tawakkal','Haqq','Batil','Ghaib','Misl','LaMithl','Azeem','Saghir','Wa','Aw','La','Adad','Kalima','Sidq','Kitab','Khalaq','Nafs','Ibn','Ulya','Ilm','Saff','Qadr','Shahada','Salah','Zakat','Sawm','Hajj'];
const examples = {
    calc: `Bismillah\nQul "=== CALCULATOR ==="\nMaktub x = 25\nMaktub y = 5\nMaktub jama = x + y\nMaktub zarb = x * y\nQul "Jama: " jama\nQul "Zarb: " zarb\nAlhamdulillah`,
    table: `Bismillah\nQul "=== TABLE ==="\nMaktub adad = 7\nMaktub i = 1\nQul adad + " x " + i + " = " + adad * i\nAlhamdulillah`,
    evenodd: `Bismillah\nQul "=== EVEN/ODD ==="\nMaktub num = 17\nMaktub check = num % 2\nQul num + " is " + (check == 0 ? "EVEN" : "ODD")\nAlhamdulillah`,
    hello: `Bismillah\nQul "Assalamu Alaikum!"\nQul "Welcome to AMEEN Language"\nQul "Created by ERROR-NEXUS"\nAlhamdulillah`
};
function loadExample(t){if(examples[t]){document.getElementById('code').value=examples[t];document.getElementById('examplecode').innerHTML='<span style="color:#00ff41">✅ Loaded: '+t.toUpperCase()+' example</span>';setTimeout(()=>{document.getElementById('examplecode').innerHTML='';},2000);}}
function buildKeywordGrid(){const g=document.getElementById('keywords');g.innerHTML='';keywordsList.forEach(k=>{const d=document.createElement('div');d.className='keyword-item';d.textContent=k;d.onclick=()=>{const t=document.getElementById('code');const s=t.selectionStart;const e=t.selectionEnd;const v=t.value;t.value=v.substring(0,s)+k+' '+v.substring(e);t.selectionStart=t.selectionEnd=s+k.length+1;t.focus();};g.appendChild(d);});}
function clearOutput(){document.getElementById('output').innerHTML='═══════════════════════════<br>CLEARED<br>═══════════════════════════<br>';document.getElementById('status').innerHTML='';}
function copyCode(){const c=document.getElementById('code').value;navigator.clipboard.writeText(c);const s=document.getElementById('status');s.innerHTML='<div class="status success">✅ Copied!</div>';setTimeout(()=>{s.innerHTML='';},2000);}
async function runCode(){const c=document.getElementById('code').value;if(!c.trim()){document.getElementById('status').innerHTML='<div class="status error">❌ Write code first!</div>';return;}
document.getElementById('output').innerHTML='<span style="color:#ffd700">⏳ Executing...</span>';
try{const r=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:c})});const d=await r.json();if(d.success){document.getElementById('output').innerHTML=d.output.replace(/\\n/g,'<br>');document.getElementById('status').innerHTML='<div class="status success">✅ Success! Alhamdulillah!</div>';}else{document.getElementById('output').innerHTML='<span style="color:#ff4444">ERROR: '+d.error+'</span>';document.getElementById('status').innerHTML='<div class="status error">❌ Failed!</div>';}}
catch(e){document.getElementById('output').innerHTML='<span style="color:#ff4444">ERROR: '+e.message+'</span>';document.getElementById('status').innerHTML='<div class="status error">❌ Connection error!</div>';}
setTimeout(()=>{const s=document.getElementById('status');if(s.innerHTML)setTimeout(()=>{s.innerHTML='';},3000);},3000);}
buildKeywordGrid();
</script>
</body>
</html>'''

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/run':
            length = int(self.headers['Content-Length'])
            body = self.rfile.read(length)
            data = json.loads(body)
            code = data.get('code', '')
            interpreter = AmeenInterpreter()
            output = interpreter.run(code)
            response = json.dumps({'success': True, 'output': output})
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()