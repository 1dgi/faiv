import React, { useState, useEffect } from "react";
import "./FAIVConsole.css";

const loadingFrames = ["◐", "◓", "◑", "◒"];
const progressBars = ["[█▒▒▒▒▒▒▒▒▒] 10%", "[███▒▒▒▒▒▒▒] 30%", "[█████▒▒▒▒▒] 50%", "[███████▒▒▒] 70%", "[█████████] 100%"];

const FAIVConsole = () => {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingFrame, setLoadingFrame] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadingFrame((prev) => (prev + 1) % loadingFrames.length);
        setProgress((prev) => (prev + 1) % progressBars.length);
      }, 500);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setOutput((prev) => [...prev, `> ${input}`]);
    setLoading(true);

    try {
        console.log("📡 Sending request to FAIV API...");

        const response = await fetch("http://127.0.0.1:8000/query/", {
            method: "POST",
            mode: "cors",  // ✅ Ensures proper CORS handling
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify({ input_text: input }),
        });

        console.log("🟢 Response Status:", response.status);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("🔍 FAIV Response Data:", data);

        const formattedResponse = data.response.split("\n").map((line, index) => (
            <div key={index} className="console-line">{line}</div>
        ));

        setOutput((prev) => [...prev, ...formattedResponse]);

    } catch (error) {
        console.error("❌ Error contacting FAIV API:", error);
        setOutput((prev) => [...prev, `⚠ Error contacting FAIV API: ${error.message}`]);
    } finally {
        setLoading(false);
        setInput("");
    }
};


  return (
    <div className="console-wrapper">
      <div className="console-window">
        <div className="console-title-bar">
          <span className="console-title">FAIV Console</span>
        </div>

        <div className="console-body">
          {loading ? (
            <div className="ascii-loader">
              <pre>███████╗ █████╗ ██╗██╗   ██╗</pre>
              <pre>██╔════╝██╔══██╗██║██║   ██║</pre>
              <pre>█████╗  ███████║██║██║   ██║</pre>
              <pre>██╔══╝  ██╔══██║██║╚██╗ ██╔╝</pre>
              <pre>██║     ██║  ██║██║ ╚████╔╝ </pre>
              <pre>╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  </pre>
              <div className="progress-bar">{progressBars[progress]}</div>
              <div className="loading-animation">{loadingFrames[loadingFrame]} Processing...</div>
            </div>
          ) : (
            <div className="console-output">
              {output.map((line, index) => (
                <div key={index} className="console-line">{line}</div>
              ))}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="console-input">
          <input
            type="text"
            className="input-field"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter your query..."
            autoFocus
          />
          <button type="submit" className="submit-btn">Enter</button>
        </form>
      </div>
    </div>
  );
};

export default FAIVConsole;
