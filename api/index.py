from flask import Flask, request, jsonify
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
    'Wa': 'AND', 'Aw': 'OR', 'La': 'NOT', 'Adad': 'NUM', 'Kalima': 'STR'
}

class AmeenInterpreter:
    def __init__(self):
        self.vars = {}
        self.output = []
    
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
        for op in ['+', '-', '*', '/']:
            if op in expr and len(expr.split(op)) == 2:
                parts = expr.split(op)
                left = self.evaluate_expression(parts[0].strip())
                right = self.evaluate_expression(parts[1].strip())
                if op == '+': return left + right
                if op == '-': return left - right
                if op == '*': return left * right
                if op == '/': return left // right if right != 0 else 0
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
                self.output.append(result)
            elif kw == 'Qawl':
                result = ' '.join(str(self.evaluate_expression(a)) for a in args)
                self.output.append(result + '\n')
            elif kw == 'Maktub' or kw == 'Tajdid':
                if len(args) >= 2:
                    var_name = args[0]
                    value = self.evaluate_expression(args[2]) if len(args) > 2 else 0
                    self.vars[var_name] = value
        
        return ''.join(self.output)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AMEEN LANGUAGE - Islamic Programming Language</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a2e1c, #064e3b);
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 20px;
            background: rgba(0,0,0,0.5);
            border-radius: 20px;
            margin-bottom: 20px;
            border: 1px solid #ffd700;
        }
        .header h1 {
            font-size: 2rem;
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .bismillah { color: #ffd700; font-size: 1rem; margin: 10px 0; }
        .credit {
            background: #1a1a2e;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            border: 1px solid #ffd700;
        }
        .credit p { color: #ffd700; }
        .credit span { color: #ff8c00; font-weight: bold; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: #0a0a1a;
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #ffd700;
        }
        .panel h3 { color: #ffd700; margin-bottom: 10px; }
        textarea {
            width: 100%;
            height: 400px;
            background: #1a1a2e;
            color: #00ff41;
            border: 1px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            font-family: monospace;
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
        }
        .example-btn {
            background: #1a1a2e;
            color: #ffd700;
            border: 1px solid #ffd700;
            margin: 5px;
            padding: 8px 12px;
            font-size: 12px;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            color: #ffd700;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🕌 AMEEN LANGUAGE 🕌</h1>
        <div class="bismillah">بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</div>
    </div>
    <div class="credit">
        <p>⚡ DEVELOPED BY <span>ERROR</span> | ERROR-NEXUS ⚡</p>
    </div>
    <div class="grid">
        <div class="panel">
            <h3>✍️ WRITE CODE</h3>
            <textarea id="code" placeholder='Bismillah
Qul "Assalamu Alaikum"
Maktub x 10
Qul x
Alhamdulillah'></textarea>
            <br>
            <button onclick="runCode()">▶ RUN</button>
            <button onclick="clearOutput()">🗑 CLEAR</button>
            <button class="example-btn" onclick="loadExample('calc')">📱 Calculator</button>
            <button class="example-btn" onclick="loadExample('hello')">🌙 Hello</button>
        </div>
        <div class="panel">
            <h3>📤 OUTPUT</h3>
            <div class="output-box" id="output">Ready... Click RUN</div>
        </div>
    </div>
    <div class="footer">
        <p>© 2025 ERROR-NEXUS | AMEEN LANGUAGE</p>
    </div>
</div>
<script>
function loadExample(type) {
    if(type === 'calc') {
        document.getElementById('code').value = `Bismillah
Qul "=== CALCULATOR ==="
Maktub x 25
Maktub y 5
Maktub jama x + y
Maktub zarb x * y
Qul "Jama: " jama
Qul "Zarb: " zarb
Alhamdulillah`;
    } else {
        document.getElementById('code').value = `Bismillah
Qul "Assalamu Alaikum!"
Qul "Welcome to Ameen Language"
Alhamdulillah`;
    }
}
function clearOutput() {
    document.getElementById('output').innerHTML = 'Cleared...';
}
async function runCode() {
    const code = document.getElementById('code').value;
    document.getElementById('output').innerHTML = 'Running...';
    try {
        const res = await fetch('/run', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: code})
        });
        const data = await res.json();
        if(data.success) {
            document.getElementById('output').innerHTML = data.output.replace(/\\n/g, '<br>');
        } else {
            document.getElementById('output').innerHTML = 'Error: ' + data.error;
        }
    } catch(e) {
        document.getElementById('output').innerHTML = 'Error: ' + e.message;
    }
}
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')
        interpreter = AmeenInterpreter()
        output = interpreter.run(code)
        return jsonify({'success': True, 'output': output})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Vercel handler
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)