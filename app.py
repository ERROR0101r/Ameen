from flask import Flask, request, jsonify, render_template_string
import subprocess
import sys
import os
import re

app = Flask(__name__)

AMEEN_KEYWORDS = {
    'Bismillah': 'START', 'Alhamdulillah': 'END', 'Maktub': 'VAR', 'Tajdid': 'SET',
    'Qul': 'PRINT', 'Qawl': 'PRINTLN', 'Istima': 'INPUT', 'Amal': 'FUNC',
    'Radd': 'RETURN', 'Dua': 'CALL', 'InshaAllah': 'IF', 'Amma': 'ELIF',
    'Illa': 'ELSE', 'SubhanAllah': 'WHILE', 'Tawaf': 'FOR', 'Astadu': 'BREAK',
    'Tawakkal': 'CONTINUE', 'Haqq': 'TRUE', 'Batil': 'FALSE', 'Ghaib': 'NULL',
    'Misl': 'EQ', 'LaMithl': 'NE', 'Azeem': 'GT', 'Saghir': 'LT',
    'Azeem_Ya_Misl': 'GE', 'Saghir_Ya_Misl': 'LE', 'Wa': 'AND', 'Aw': 'OR',
    'La': 'NOT', 'Adad': 'NUM', 'Kalima': 'STR', 'Sidq': 'BOOL', 'Kitab': 'CLASS',
    'Khalaq': 'NEW', 'Nafs': 'SELF', 'Ibn': 'EXTENDS', 'Ulya': 'SUPER',
    'Ilm': 'IMPORT', 'Saff': 'LIST', 'Qadr': 'RANDOM', 'Shahada': 'INIT',
    'Salah': 'RUN', 'Zakat': 'GIVE', 'Sawm': 'STOP', 'Hajj': 'MOVE',
    'Ar_Rahman': 'grace', 'Ar_Rahim': 'mercy', 'Al_Malik': 'owner', 'Al_Fattah': 'open'
}

class AmeenInterpreter:
    def __init__(self):
        self.vars = {}
        self.output = []
        self.input_queue = []
        self.waiting_input = False
        self.current_input_var = None
    
    def set_input(self, value):
        if self.waiting_input and self.current_input_var is not None:
            try:
                self.vars[self.current_input_var] = int(value)
            except:
                self.vars[self.current_input_var] = value
            self.waiting_input = False
            self.current_input_var = None
            return True
        return False
    
    def tokenize(self, code):
        lines = code.replace('\r', '').split('\n')
        tokens = []
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            parts = line.split()
            if parts and parts[0] in AMEEN_KEYWORDS:
                kw_type = AMEEN_KEYWORDS[parts[0]]
                args = parts[1:] if len(parts) > 1 else []
                tokens.append((kw_type, args, line_num))
            else:
                tokens.append(('UNKNOWN', [line], line_num))
        return tokens
    
    def evaluate_expression(self, expr):
        expr = str(expr).strip()
        if expr in self.vars:
            return self.vars[expr]
        try:
            if expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]
        except:
            pass
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
                    if op == '+': return left + right
                    if op == '-': return left - right
                    if op == '*': return left * right
                    if op == '/': return left // right if right != 0 else 0
                    if op == '%': return left % right
        return expr
    
    def run(self, code, input_callback=None):
        self.output = []
        tokens = self.tokenize(code)
        i = 0
        while i < len(tokens):
            tok_type, args, line_num = tokens[i]
            
            if tok_type == 'START':
                self.output.append("=== BISMILLAH ===\n")
            
            elif tok_type == 'END':
                self.output.append("\n=== ALHAMDULILLAH ===")
            
            elif tok_type == 'PRINT':
                result = ' '.join(str(self.evaluate_expression(a)) for a in args)
                self.output.append(result)
            
            elif tok_type == 'PRINTLN':
                result = ' '.join(str(self.evaluate_expression(a)) for a in args)
                self.output.append(result + '\n')
            
            elif tok_type == 'INPUT':
                if len(args) >= 2:
                    prompt = self.evaluate_expression(args[0])
                    var_name = args[1]
                    self.output.append(prompt)
                    if input_callback:
                        val = input_callback(prompt)
                        try:
                            self.vars[var_name] = int(val)
                        except:
                            self.vars[var_name] = val
                    else:
                        return {'waiting': True, 'var': var_name, 'prompt': prompt}
            
            elif tok_type == 'VAR':
                if len(args) >= 2:
                    var_name = args[0]
                    value = self.evaluate_expression(args[2]) if len(args) > 2 else 0
                    self.vars[var_name] = value
            
            elif tok_type == 'SET':
                if len(args) >= 2:
                    var_name = args[0]
                    value = self.evaluate_expression(args[2]) if len(args) > 2 else 0
                    self.vars[var_name] = value
            
            elif tok_type == 'IF':
                if len(args) >= 2:
                    cond = self.evaluate_expression(args[0] + ' ' + args[1] + ' ' + args[2]) if len(args) >= 3 else False
                    if cond:
                        pass
            
            elif tok_type == 'PRINTLN' or tok_type == 'PRINT':
                pass
            
            i += 1
        
        return {'output': ''.join(self.output), 'vars': self.vars}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMEEN LANGUAGE - Islamic Programming Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a2e1c, #064e3b);
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.5);
            border-radius: 20px;
            margin-bottom: 20px;
            border: 1px solid #ffd700;
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .bismillah { color: #ffd700; font-size: 1.2rem; margin: 10px 0; }
        .credit {
            background: #1a1a2e;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #ffd700;
        }
        .credit p { color: #ffd700; font-size: 1rem; }
        .credit span { color: #ff8c00; font-weight: bold; }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .editor-panel, .output-panel, .examples-panel, .keywords-panel {
            background: #0a0a1a;
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #ffd700;
        }
        .editor-panel h3, .output-panel h3, .examples-panel h3, .keywords-panel h3 {
            color: #ffd700;
            margin-bottom: 10px;
            border-bottom: 1px solid #ffd700;
            padding-bottom: 5px;
        }
        textarea {
            width: 100%;
            height: 400px;
            background: #1a1a2e;
            color: #00ff41;
            border: 1px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
        }
        .output-box {
            width: 100%;
            height: 400px;
            background: #1a1a2e;
            color: #00ff41;
            border: 1px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            overflow-y: auto;
            font-family: monospace;
            white-space: pre-wrap;
        }
        button {
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            color: #0a0a1a;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 1rem;
        }
        button:hover { opacity: 0.9; transform: scale(0.98); }
        .example-btn {
            background: #1a1a2e;
            color: #ffd700;
            border: 1px solid #ffd700;
            margin: 5px;
            padding: 8px 12px;
            font-size: 12px;
        }
        .keyword-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            max-height: 300px;
            overflow-y: auto;
        }
        .keyword-item {
            background: #1a1a2e;
            color: #ffd700;
            padding: 5px;
            border-radius: 5px;
            font-size: 12px;
            text-align: center;
            cursor: pointer;
            border: 1px solid #ffd700;
        }
        .keyword-item:hover { background: #ffd700; color: #0a0a1a; }
        .status {
            padding: 10px;
            margin-top: 10px;
            border-radius: 10px;
            text-align: center;
        }
        .status.success { background: #1a5a2e; color: #00ff41; }
        .status.error { background: #5a1a2e; color: #ff4444; }
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
            .keyword-grid { grid-template-columns: repeat(2, 1fr); }
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            color: #ffd700;
            font-size: 12px;
        }
        .install-box {
            background: #1a1a2e;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #00ff41;
        }
        .install-box pre {
            background: #0a0a1a;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            color: #00ff41;
        }
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
    
    <div class="main-grid">
        <div class="editor-panel">
            <h3>✍️ WRITE AMEEN CODE</h3>
            <textarea id="code" placeholder='Write Ameen language code here...
Example:
Bismillah
Qul "Hello World"
Maktub x 10
Qul x
Alhamdulillah'></textarea>
            <br>
            <button onclick="runCode()">▶ RUN CODE (InshaAllah)</button>
            <button onclick="clearOutput()">🗑 CLEAR OUTPUT</button>
            <button onclick="copyCode()">📋 COPY CODE</button>
        </div>
        
        <div class="output-panel">
            <h3>📤 OUTPUT</h3>
            <div class="output-box" id="output">
                <span style="color:#ffd700">═══════════════════════════</span><br>
                <span style="color:#ffd700">AMEEN LANGUAGE READY</span><br>
                <span style="color:#ffd700">═══════════════════════════</span><br>
                <span>Click RUN to execute code</span>
            </div>
            <div id="status"></div>
        </div>
    </div>
    
    <div class="main-grid" style="margin-top: 20px;">
        <div class="examples-panel">
            <h3>📚 EXAMPLE CODES</h3>
            <button class="example-btn" onclick="loadExample('calc')">➕ Calculator</button>
            <button class="example-btn" onclick="loadExample('table')">✖ Table</button>
            <button class="example-btn" onclick="loadExample('evenodd')">🔢 Even/Odd</button>
            <button class="example-btn" onclick="loadExample('hello')">🌙 Hello</button>
            <button class="example-btn" onclick="loadExample('vars')">📦 Variables</button>
            <button class="example-btn" onclick="loadExample('loop')">🔄 Loop</button>
            <div id="examplecode" style="margin-top: 10px;"></div>
        </div>
        
        <div class="keywords-panel">
            <h3>🔑 ISLAMIC KEYWORDS</h3>
            <div class="keyword-grid" id="keywords"></div>
        </div>
    </div>
    
    <div class="install-box">
        <h3 style="color:#ffd700">🖥️ TERMUX INSTALLATION (ONE TIME)</h3>
        <pre style="color:#00ff41">pkg update && pkg upgrade -y
pkg install python git -y
pip install flask
git clone https://github.com/ERROR-NEXUS/ameen-language.git
cd ameen-language
python app.py</pre>
        <p style="color:#ffd700; margin-top:10px">🌐 DEPLOY ON VERCEL / RAILWAY / HEROKU</p>
        <pre style="color:#00ff41"># Vercel Deployment
vercel --prod

# Railway Deployment
railway up

# Run Locally
python app.py
# Then open http://localhost:5000</pre>
        <p style="color:#ffd700; margin-top:10px">📁 FILE EXTENSION: <strong style="color:#00ff41">.ameen</strong></p>
        <p style="color:#00ff41">🎯 RUN COMMAND: python app.py</p>
    </div>
    
    <div class="footer">
        <p>© 2025 ERROR-NEXUS | AMEEN LANGUAGE | Islamic Programming Language</p>
        <p>🤲 "Read in the name of your Lord who created" - Al-Alaq 96:1</p>
    </div>
</div>

<script>
const keywordsList = [
    'Bismillah', 'Alhamdulillah', 'Maktub', 'Tajdid', 'Qul', 'Qawl', 'Istima',
    'Amal', 'Radd', 'Dua', 'InshaAllah', 'Amma', 'Illa', 'SubhanAllah', 'Tawaf',
    'Astadu', 'Tawakkal', 'Haqq', 'Batil', 'Ghaib', 'Misl', 'LaMithl', 'Azeem',
    'Saghir', 'Wa', 'Aw', 'La', 'Adad', 'Kalima', 'Sidq', 'Kitab', 'Khalaq',
    'Nafs', 'Ibn', 'Ulya', 'Ilm', 'Saff', 'Qadr', 'Shahada', 'Salah', 'Zakat', 'Sawm', 'Hajj'
];

const examples = {
    calc: `Bismillah
Qul "=== AMEEN CALCULATOR ==="
Qul ""
Maktub x 25
Maktub y 5
Maktub jama x + y
Maktub tafreeq x - y
Maktub zarb x * y
Maktub taqseem x / y
Qul "Jama (Addition): " jama
Qul "Tafreeq (Subtraction): " tafreeq
Qul "Zarb (Multiplication): " zarb
Qul "Taqseem (Division): " taqseem
Alhamdulillah`,
    
    table: `Bismillah
Qul "=== ZARB KA TABLE ==="
Maktub adad 7
Maktub i 1
SubhanAllah i < 11
    Maktub result adad * i
    Qul adad + " x " + i + " = " + result
    Tajdid i i + 1
Alhamdulillah`,
    
    evenodd: `Bismillah
Qul "=== EVEN/ODD CHECKER ==="
Maktub number 17
Maktub check number % 2
InshaAllah check Misl 0
    Qul number + " is EVEN (Juzwi)"
Illa
    Qul number + " is ODD (Taq)"
Alhamdulillah`,
    
    hello: `Bismillah
Qul "Assalamu Alaikum!"
Qul "Welcome to AMEEN Language"
Qul "Created by ERROR-NEXUS"
Qul ""
Qul "May Allah bless you!"
Alhamdulillah`,
    
    vars: `Bismillah
Maktub name "ERROR"
Maktub version 3.0
Maktub year 2025
Qul "Language: " + name
Qul "Version: " + version
Qul "Year: " + year
Alhamdulillah`,
    
    loop: `Bismillah
Maktub i 1
SubhanAllah i < 6
    Qul "Tawaf iteration: " + i
    Tajdid i i + 1
Alhamdulillah`
};

function loadExample(type) {
    const code = examples[type];
    if (code) {
        document.getElementById('code').value = code;
        document.getElementById('examplecode').innerHTML = '<span style="color:#00ff41">✅ Loaded: ' + type.toUpperCase() + ' example</span>';
        setTimeout(() => {
            document.getElementById('examplecode').innerHTML = '';
        }, 2000);
    }
}

function buildKeywordGrid() {
    const grid = document.getElementById('keywords');
    grid.innerHTML = '';
    keywordsList.forEach(kw => {
        const div = document.createElement('div');
        div.className = 'keyword-item';
        div.textContent = kw;
        div.onclick = () => insertKeyword(kw);
        grid.appendChild(div);
    });
}

function insertKeyword(kw) {
    const textarea = document.getElementById('code');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    const before = text.substring(0, start);
    const after = text.substring(end);
    textarea.value = before + kw + ' ' + after;
    textarea.selectionStart = textarea.selectionEnd = start + kw.length + 1;
    textarea.focus();
}

function clearOutput() {
    document.getElementById('output').innerHTML = '<span style="color:#ffd700">═══════════════════════════</span><br><span style="color:#ffd700">OUTPUT CLEARED</span><br><span style="color:#ffd700">═══════════════════════════</span><br>';
    document.getElementById('status').innerHTML = '';
}

function copyCode() {
    const code = document.getElementById('code').value;
    navigator.clipboard.writeText(code);
    const status = document.getElementById('status');
    status.innerHTML = '<div class="status success">✅ Code copied to clipboard!</div>';
    setTimeout(() => { status.innerHTML = ''; }, 2000);
}

async function runCode() {
    const code = document.getElementById('code').value;
    if (!code.trim()) {
        document.getElementById('status').innerHTML = '<div class="status error">❌ Please write some code first!</div>';
        return;
    }
    
    document.getElementById('output').innerHTML = '<span style="color:#ffd700">⏳ Executing code...</span>';
    
    try {
        const response = await fetch('/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('output').innerHTML = data.output.replace(/\\n/g, '<br>').replace(/\\n/g, '<br>');
            document.getElementById('status').innerHTML = '<div class="status success">✅ Execution successful! Alhamdulillah!</div>';
        } else {
            document.getElementById('output').innerHTML = '<span style="color:#ff4444">ERROR: ' + data.error + '</span>';
            document.getElementById('status').innerHTML = '<div class="status error">❌ Execution failed!</div>';
        }
    } catch (err) {
        document.getElementById('output').innerHTML = '<span style="color:#ff4444">ERROR: ' + err.message + '</span>';
        document.getElementById('status').innerHTML = '<div class="status error">❌ Connection error!</div>';
    }
    
    setTimeout(() => {
        const statusDiv = document.getElementById('status');
        if (statusDiv.innerHTML) {
            setTimeout(() => { statusDiv.innerHTML = ''; }, 3000);
        }
    }, 3000);
}

buildKeywordGrid();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        
        interpreter = AmeenInterpreter()
        
        def input_callback(prompt):
            return '0'
        
        result = interpreter.run(code, input_callback)
        
        if isinstance(result, dict) and 'output' in result:
            output = result['output']
        else:
            output = str(result)
        
        return jsonify({'success': True, 'output': output})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)