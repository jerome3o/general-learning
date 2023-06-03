console.log("Worker started");

self.postMessage("hello from the worker");

importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js");

console.log("Pyodide downloaded");

let boilerplate = `
globals().clear()
from io import StringIO
import sys

`;

function prepPythonCode(python) {
  return `
_old_stdout = sys.stdout
sys.stdout = StringIO()

${python}

sys.stdout.seek(0)
output = sys.stdout.read()
sys.stdout = _old_stdout
output
`;
}

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  console.log("Pyodide loaded");
  await self.pyodide.loadPackage(["numpy", "pytz", "micropip", "ssl"]);
  console.log("Pyodide packages loaded");
  await self.pyodide.runPythonAsync(boilerplate);
  let results = await self.pyodide.runPythonAsync(`
import micropip
t1 = await micropip.install("fastapi")
t2 = await micropip.install("uvicorn")
print(t1, t2)
`);
  self.postMessage({ results, id: 0 });
}

let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async (event) => {
  // make sure loading is done
  await pyodideReadyPromise;
  // Don't bother yet with this line, suppose our API is built in such a way:
  let { id, python, ...context } = event.data;
  // The worker copies the context in its own "memory" (an object mapping name to values)
  for (const key of Object.keys(context)) {
    self[key] = context[key];
  }
  // Now is the easy part, the one that is similar to working in the main thread:
  try {
    python = prepPythonCode(python);
    await self.pyodide.loadPackagesFromImports(python);
    let results = await self.pyodide.runPythonAsync(python);
    self.postMessage({ results, id });
  } catch (error) {
    self.postMessage({ error: error.message, id });
  }
};

// self.postMessage({ data: "pyodide loaded" });
