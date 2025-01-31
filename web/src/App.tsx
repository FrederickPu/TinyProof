import React, { useState, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import * as monaco from 'monaco-editor';

monaco.languages.register({ id: 'lean4' });
monaco.languages.setMonarchTokensProvider('lean4', {
  tokenizer: {
    root: [
      // Comments
      [/(--.*$)/, 'comment'],
      // Multi-line comments
      [/\(\*/, { token: 'comment', next: '@comment' }],
      // Keywords
      [/\b(def|theorem|example|lemma|inductive|namespace|open|import|variable|axiom|universe)\b/, 'keyword'],
      // Strings
      [/"([^"\\]|\\.)*$/, 'string.invalid'],  // non-terminated string
      [/"/, { token: 'string.quote', bracket: '@open', next: '@string' }],
      // Operators or punctuation
      [/[{}()\[\]]/, '@brackets'],
      [/[=+\-*/<>!?:|_]/, 'operator'],
      // Identifiers
      [/\b[A-Za-z_]\w*\b/, 'identifier'],
    ],
    comment: [
      [/[^\*]+/, 'comment'],
      [/\*\)/, { token: 'comment', next: '@pop' }],
      [/\*/, 'comment'],
    ],
    string: [
      [/[^\\"]+/, 'string'],
      [/\\./, 'string.escape'],
      [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
    ]
  }
});

function App() {
  const [code, setCode] = useState<string>(`-- Try a small Lean snippet
def hello := "Hello Lean!"
example : 1 = 2 := rfl
`);
  const [errors, setErrors] = useState<any[]>([]);

  // Debounced call to /check endpoint
  useEffect(() => {
    const timer = setTimeout(() => {
      checkLeanCode(code);
    }, 500);
    return () => clearTimeout(timer);
  }, [code]);

  async function checkLeanCode(newCode: string) {
    try {
      const response = await fetch('http://127.0.0.1:8000/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: newCode })
      });
      if (response.ok) {
        const data = await response.json();
        // Data shape: { errors: [ {message, line, column}, ... ] }
        setErrors(data.errors);
      } else {
        console.error('Server error:', response.statusText);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <div style={{ flex: 1 }}>
        <Editor
          height="100%"
          defaultLanguage="lean4"
          value={code}
          onChange={(value) => setCode(value || '')}
        />
      </div>
      <div style={{ width: '300px', borderLeft: '1px solid #ccc', padding: '1rem' }}>
        <h3>Lean Errors</h3>
        {errors.length === 0 ? (
          <p>No errors</p>
        ) : (
          errors.map((err, idx) => (
            <div key={idx} style={{ marginBottom: '1rem' }}>
              <div style={{ color: 'red', fontWeight: 'bold' }}>
                Line {err.line}, Col {err.column}
              </div>
              <div>{err.message}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;