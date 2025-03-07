import React, { useState, useEffect } from "react";
import "./FAIVConsole.css";
import LoadingAnimation from "./LoadingAnimation";

const FAIVConsole = () => {
  // ------------------------------
  // 0) ASCII Lines for the Logo + Wavy Effect
  // ------------------------------
  const asciiLines = [
    "███████╗ █████╗ ██╗██╗   ██╗",
    "██╔════╝██╔══██╗██║██║   ██║",
    "█████╗  ███████║██║██║   ██║",
    "██╔══╝  ██╔══██║██║╚██╗ ██╔╝",
    "██║     ██║  ██║██║ ╚████╔╝",
    "╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝"
  ];

  // Wave offset toggles between 0 and 1
  const [waveOffset, setWaveOffset] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setWaveOffset((prev) => (prev + 1) % 2);
    }, 300);
    return () => clearInterval(interval);
  }, []);

  // Returns ASCII lines with alternating leading space for wave effect
  function getWavyAsciiLines() {
    return asciiLines.map((line, idx) => {
      const needsSpace = ((idx + waveOffset) % 2) === 1;
      return (needsSpace ? " " : "") + line;
    });
  }

  // ------------------------------
  // 1) Loading & Progress States
  // ------------------------------
  const [input, setInput] = useState("");
  const [output, setOutput] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("FAIV Processing Started...");

  const progressPhases = [
    { percent: 5, message: "Initializing FAIV Deliberation..." },
    { percent: 20, message: "Councils Gathering Insights..." },
    { percent: 45, message: "Encoding Perspectives..." },
    { percent: 70, message: "Finalizing Consensus..." },
    { percent: 100, message: "Decision Ready!" }
  ];

  // ------------------------------
  // 2) Text Normalization Functions
  // ------------------------------

  // Remove emojis from text
  const removeEmojis = (text) => {
    const emojiPattern = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2702}-\u{27B0}\u{24C2}-\u{1F251}]/gu;
    return text.replace(emojiPattern, "");
  };

  // Upside-down mappings
  const upsideDownOriginal =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789?!.,;()[]{}";
  const upsideDownFlipped =
    "ɐqɔpǝɟƃɥᴉɾʞʅɯuodbɹsʇnʌʍxʎz∀ᗺƆᗡƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z0ƖᄅƐㄣϛ9ㄥ86¿¡˙‘؛)(][}{";

  const reverseUpsideDownMap = {};
  for (let i = 0; i < upsideDownFlipped.length; i++) {
    reverseUpsideDownMap[upsideDownFlipped[i]] = upsideDownOriginal[i];
  }
  // Placeholder mapping for any missing glyphs, if needed
  const placeholderMap = {
    "⟦1⟧": "B"
  };

  function normalizeUpsideDown(text) {
    return text
      .split("")
      .map((char) => placeholderMap[char] || reverseUpsideDownMap[char] || char)
      .join("");
  }

  // Fancy font to plain mapping
  const fontTransformations = {
    "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘶𝘷𝘄𝘹𝘺𝘇": "abcdefghijklmnopqrstuvwxyz",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗶𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻": "abcdefghijklmnopqrstuvwxyz",
    "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ᵃᵇᶜᵈᵉᶠᵍʰᶤʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ": "abcdefghijklmnopqrstuvwxyz",
    "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾᵟᴿˢᵀᵁⱽᵂˣʸᶻ": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  };

  // Master normalization: remove emojis, then convert fancy fonts, then normalize upside-down
  const normalizeText = (text) => {
    text = removeEmojis(text);
    for (const [fancy, plain] of Object.entries(fontTransformations)) {
      for (let i = 0; i < fancy.length; i++) {
        text = text.replaceAll(fancy[i], plain[i]);
      }
    }
    text = normalizeUpsideDown(text);
    return text;
  };

  // ------------------------------
  // 3) Fixed Progress Bar Component
  // ------------------------------
  function FixedProgressBar({ progress }) {
    const totalSquares = 10;
    const filledCount = Math.round(progress / 10);
    const filled = "█".repeat(filledCount);
    const empty = "▒".repeat(totalSquares - filledCount);
    const paddedProgress = String(progress).padStart(3, " ");
    return (
      <div className="progress-bar">
        [{filled}{empty}] {paddedProgress}%
      </div>
    );
  }

  // ------------------------------
  // 4) Minimal Final Output Extraction Function
  // ------------------------------
  // This function extracts final consensus, confidence, and justification
  // from the raw response text (which is expected to be minimal from a single API call).
  function extractFinalOutput(rawText) {
    const consensusMatch = rawText.match(/\*\*FAIV Consensus:\*\*\s*(.+)/);
    const confidenceMatch = rawText.match(/\*\*Confidence Score:\*\*\s*(\d+)%/);
    const justificationMatch = rawText.match(/\*\*Justification:\*\*\s*(.+)/);
    let out = "";
    if (consensusMatch) out += `**FAIV Consensus:** ${consensusMatch[1].trim()}\n`;
    if (confidenceMatch) out += `**Confidence Score:** ${confidenceMatch[1].trim()}%\n`;
    if (justificationMatch) out += `**Justification:** ${justificationMatch[1].trim()}\n`;
    return out.trim();
  }

  // ------------------------------
  // 5) Submit Handler
  // ------------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setOutput((prev) => [...prev, `> ${input}`]);
    setLoading(true);
    setProgress(0);
    setStatusMessage("FAIV Processing Started...");

    try {
      const response = await fetch("http://127.0.0.1:8000/query/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_text: input })
      });
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

      const data = await response.json();

      // Simulate progress phases
      let index = 0;
      const processPhase = () => {
        if (index < progressPhases.length) {
          setProgress(progressPhases[index].percent);
          setStatusMessage(progressPhases[index].message);
          setTimeout(processPhase, 1000);
          index++;
        } else {
          // Once loading is done, assume data.response is minimal final output.
          // Extract the final output with our function.
          const finalOutput = extractFinalOutput(data.response);
          setOutput((prev) => [...prev, finalOutput]);
          setLoading(false);
        }
      };
      processPhase();
    } catch (error) {
      setOutput((prev) => [...prev, `⚠ Error: ${error.message}`]);
      setLoading(false);
    } finally {
      setInput("");
    }
  };

  // ------------------------------
  // 6) Render
  // ------------------------------
  return (
    <div className="console-wrapper">
      <div className="console-window">
        {/* Title Bar */}
        <div className="console-title-bar">
          <span className="console-title">FAIV Console</span>
        </div>
        {/* Main Console Body */}
        <div className={`console-body ${loading ? "loading" : ""}`}>
          {loading ? (
            <div className="ascii-loader">
              {getWavyAsciiLines().map((row, i) => (
                <pre key={i} className="ascii-logo">{row}</pre>
              ))}
              <div className="progress-container">
                <div className="loading-animation-container">
                  <LoadingAnimation />
                  <FixedProgressBar progress={progress} />
                </div>
                <div className="loading-text">{statusMessage}</div>
              </div>
            </div>
          ) : (
            <div className="console-output">
              {output.map((line, index) => (
                <div key={index} className="console-line">{line}</div>
              ))}
            </div>
          )}
        </div>
        {/* Input Bar: hidden while loading to maintain fixed window size */}
        {!loading && (
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
        )}
      </div>
    </div>
  );
};

export default FAIVConsole;
