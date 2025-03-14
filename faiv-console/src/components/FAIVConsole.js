import React, { useState, useEffect } from "react";
import "./FAIVConsole.css";

/****************************************
 * 1) ASCII Loader Frames
 ****************************************/
const asciiFrames = [
  [
    "███████╗ █████╗ ██╗██╗   ██╗",
    "██╔════╝██╔══██╗██║██║   ██║",
    "█████╗  ███████║██║██║   ██║",
    "██╔══╝  ██╔══██║██║╚██╗ ██╔╝",
    "██║     ██║  ██║██║ ╚████╔╝ ",
    "╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  ",
  ],
  [
    " ██████╗ █████╗ ██╗██╗   ██╗",
    "██╔════╝██╔══██╗██║██║   ██║",
    "█████╗  ███████║██║██║   ██║",
    "██╔══╝  ██╔══██║██║╚██╗ ██╔╝",
    "██║     ██║  ██║██║ ╚████╔╝",
    "╚═╝     ██╔═╝  ╚═╝╚═╝  ╚═══╝ ",
  ],
  [
    "  ██████╗ █████╗ ██╗██╗   ██╗",
    " ██╔════╝██╔══██╗██║██║   ██║",
    " █████╗  ███████║██║██║   ██║",
    " ██╔══╝  ██╔══██║██║╚██╗ ██╔╝",
    " ██║     ██║  ██║██║ ╚████╔╝ ",
    " ╚═╝     ██╔═╝  ╚═╝╚═╝  ╚═══╝  ",
  ],
];

/****************************************
 * 2) Helper to parse final FAIV output
 ****************************************/
function extractFinalOutput(response) {
  if (!response || typeof response !== "string") {
    return "⚠ No valid response received.";
  }

  // 1) Clean up zero-width etc.
  const cleaned = response
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/\s*\n\s*/g, "\n")
    .trim();

  // 2) Split by newlines
  const lines = cleaned.split("\n");

  // 3) Minor helper to remove stray bracket/asterisk combos
  const cleanStr = (str) => str.replace(/\]*:?[*]+/g, "").trim();

  // 4) Return a <div> of parsed lines
  return (
    <div className="output-block">
      {lines.map((rawLine, idx) => {
        const line = rawLine.trim();

        // CASE A: "Consensus:"
        if (/Consensus:/i.test(line)) {
          const [labelPart, afterLabel] = line.split(/Consensus:\s*/i);
          const labelClean = cleanStr(labelPart + "Consensus:");
          const content = cleanStr(afterLabel || "");
          return (
            <div key={idx} className="console-line">
              <b>
                <u>{labelClean}</u>
              </b>
              {": "}
              {content}
            </div>
          );
        }

        // CASE B: "Confidence Score:"
        if (line.startsWith("Confidence Score:")) {
          const val = cleanStr(line.replace(/^Confidence Score:/i, ""));
          return (
            <div key={idx} className="console-line">
              <b>
                <u>Confidence Score:</u>
              </b>{" "}
              {val}
            </div>
          );
        }

        // CASE C: "Justification:"
        if (line.startsWith("Justification:")) {
          const val = cleanStr(line.replace(/^Justification:/i, ""));
          return (
            <div key={idx} className="console-line">
              <b>
                <u>Justification:</u>
              </b>{" "}
              {val}
            </div>
          );
        }

        // CASE D: "Differing Opinion -"
        if (line.startsWith("Differing Opinion -")) {
          const val = cleanStr(line.replace(/^Differing Opinion -/i, ""));
          return (
            <div key={idx} className="console-line">
              <b>
                <u>Differing Opinion -</u>
              </b>{" "}
              {val}
            </div>
          );
        }

        // CASE E: "Reason:"
        if (line.startsWith("Reason:")) {
          const val = cleanStr(line.replace(/^Reason:/i, ""));
          return (
            <div key={idx} className="console-line">
              <b>
                <u>Reason:</u>
              </b>{" "}
              {val}
            </div>
          );
        }

        // Fallback
        return (
          <div key={idx} className="console-line">
            {cleanStr(line)}
          </div>
        );
      })}
    </div>
  );
}

/****************************************
 * 3) Main Component
 ****************************************/
export default function FAIVConsole() {
  // All sessions + selected session ID
  const [allSessions, setAllSessions] = useState({});
  const [activeSessionId, setActiveSessionId] = useState("");

  // Input + Loading
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  // ASCII wave frames
  const [asciiFrame, setAsciiFrame] = useState(0);
  const [progress, setProgress] = useState(0);

  // Pillar dropdown
  const [selectedPillar, setSelectedPillar] = useState("FAIV");
  const [pillarOpen, setPillarOpen] = useState(false);

  // Delete confirm modal
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [pendingDeleteSession, setPendingDeleteSession] = useState("");
  const [deleteConfirmInput, setDeleteConfirmInput] = useState("");

  // Account dropdown
  const [accountOpen, setAccountOpen] = useState(false);

  // Which page is selected in the account menu (default = "Counsole")
  const [selectedPage, setSelectedPage] = useState("Counsole");

  // 1) Switch the page + close account menu
  function handleSelectPage(pageName) {
    setSelectedPage(pageName);
    setAccountOpen(false);
  }

  // 2) On mount => load existing sessions from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("faiv_sessions");
    if (stored) {
      const parsed = JSON.parse(stored);
      setAllSessions(parsed);

      const lastActive = localStorage.getItem("faiv_session_id") || "";
      if (lastActive && parsed[lastActive]) {
        setActiveSessionId(lastActive);
      } else {
        // fallback
        const keys = Object.keys(parsed);
        if (keys.length > 0) {
          setActiveSessionId(keys[0]);
          localStorage.setItem("faiv_session_id", keys[0]);
        } else {
          handleNewChat();
        }
      }
    } else {
      // No sessions => create a new one
      handleNewChat();
    }
  }, []);

  // 3) Whenever sessions change => persist
  useEffect(() => {
    localStorage.setItem("faiv_sessions", JSON.stringify(allSessions));
  }, [allSessions]);

  // 4) Animate progress bar
  useEffect(() => {
    let interval;
    if (loading) {
      setProgress(0);
      const startTime = Date.now();
      interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const newVal = Math.min((elapsed / 8000) * 100, 99);
        setProgress(newVal);
      }, 500);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // 5) Animate ASCII frames
  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setAsciiFrame((prev) => (prev + 1) % asciiFrames.length);
      }, 400);
    } else {
      setAsciiFrame(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // 6) Helpers
  const currentSession = allSessions[activeSessionId];
  const currentMessages = currentSession ? currentSession.messages : [];

  function updateSessionMessages(sessionId, newMessages) {
    setAllSessions((prev) => ({
      ...prev,
      [sessionId]: {
        ...prev[sessionId],
        messages: newMessages,
      },
    }));
  }

  function handleNewChat() {
    const newId = crypto.randomUUID();
    const newTitle = "Untitled";
    const newSession = { title: newTitle, messages: [] };
    setAllSessions((prev) => ({ ...prev, [newId]: newSession }));
    setActiveSessionId(newId);
    localStorage.setItem("faiv_session_id", newId);
  }

  function ensureAtLeastOneSession() {
    const keys = Object.keys(allSessions);
    if (keys.length === 0) {
      handleNewChat();
    }
  }

  function handleDeleteChat(sessionId) {
    setPendingDeleteSession(sessionId);
    setDeleteConfirmInput("");
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    if (deleteConfirmInput.toLowerCase().trim() !== "delete") return;
    setShowDeleteModal(false);

    const sessId = pendingDeleteSession;
    setAllSessions((prev) => {
      const copy = { ...prev };
      delete copy[sessId];
      return copy;
    });

    if (sessId === activeSessionId) {
      const remain = Object.keys(allSessions).filter((id) => id !== sessId);
      if (remain.length > 0) {
        setActiveSessionId(remain[0]);
        localStorage.setItem("faiv_session_id", remain[0]);
      } else {
        handleNewChat();
      }
    }
  }

  function handleSelectSession(sessId) {
    setActiveSessionId(sessId);
    localStorage.setItem("faiv_session_id", sessId);
  }

  // Submit input => call server
  async function handleSubmit(e) {
    e.preventDefault();

    ensureAtLeastOneSession();
    if (!input.trim() || !activeSessionId) return;

    // Make sure session actually exists
    if (!allSessions[activeSessionId]) {
      handleNewChat();
      return;
    }

    const title = allSessions[activeSessionId].title;
    let updated = [...allSessions[activeSessionId].messages];

    // Insert a separator if there's existing content
    if (updated.length > 0) updated.push("-----");
    updated.push(`> ${input}`);

    // If "Untitled," rename
    if (title === "Untitled") {
      let snippet = input.length > 30 ? input.slice(0, 30).trim() + "..." : input;
      snippet = `"${snippet}"`;
      setAllSessions((prev) => ({
        ...prev,
        [activeSessionId]: { ...prev[activeSessionId], title: snippet },
      }));
    }

    // Save
    updateSessionMessages(activeSessionId, updated);
    setInput("");
    setLoading(true);

    try {
      const resp = await fetch("http://127.0.0.1:8000/query/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          session_id: activeSessionId,
          input_text: input,
          pillar: selectedPillar,
        }),
      });
      if (!resp.ok) {
        throw new Error(`HTTP error! status: ${resp.status}`);
      }
      const data = await resp.json();

      updated.push(data.response);
      updateSessionMessages(activeSessionId, updated);
    } catch (err) {
      updated.push(`⚠ Error contacting FAIV API: ${err.message}`);
      updateSessionMessages(activeSessionId, updated);
    } finally {
      setLoading(false);
    }

    // Scroll
    setTimeout(() => {
      const consoleBody = document.querySelector(".right-console-body");
      if (consoleBody) consoleBody.scrollTop = consoleBody.scrollHeight;
    }, 100);
  }

  /****************************************
   * RENDER
   ****************************************/
  return (
    <div className="outer-container">
      <div className="windows-container">
        {/* LEFT WINDOW */}
        <div className="retro-window left-window">
          <div className="retro-title-bar left-title-bar">
            <span>History</span>
            <button
              className="new-chat-btn"
              onClick={handleNewChat}
              title="Start New Chat"
            >
              &gt;
            </button>
          </div>

          <div className="left-window-body">
            {Object.keys(allSessions).map((sessId) => {
              const info = allSessions[sessId];
              return (
                <div
                  key={sessId}
                  className={`chat-item ${sessId === activeSessionId ? "active" : ""}`}
                  onClick={() => handleSelectSession(sessId)}
                >
                  <span>{info.title || "Untitled"}</span>
                  <button
                    className="chat-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(sessId);
                    }}
                    title="Delete Chat"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="#00ff00">
                      <path d="M3 6h18M8 6v14c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V6" stroke="none" />
                      <path d="M10 9v8M14 9v8" stroke="black" strokeWidth="2" />
                    </svg>
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* RIGHT WINDOW */}
        <div className="retro-window right-window">
          <div className="retro-title-bar right-title-bar">
            {/* Pillar dropdown only if on Counsole */}
            {selectedPage === "Counsole" && (
              <>
                <div
                  className="pillar-dropdown-wrapper"
                  onClick={() => setPillarOpen(!pillarOpen)}
                >
                  <div className="pillar-dropdown-display">{selectedPillar}</div>
                  <div className="pillar-arrow">{pillarOpen ? "▲" : "▼"}</div>
                </div>

                <ul className={`pillar-menu ${pillarOpen ? "open" : ""}`}>
                  {["FAIV","Wisdom","Strategy","Expansion","Future","Integrity"].map(opt => (
                    <li
                      key={opt}
                      className={opt === selectedPillar ? "selected" : ""}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedPillar(opt);
                        setPillarOpen(false);
                      }}
                    >
                      {opt}
                    </li>
                  ))}
                </ul>
              </>
            )}

            {/* Page title => left or center style */}
            <div
              style={
                selectedPage === "Counsole"
                  ? { marginLeft: "10px", marginRight: "auto" }
                  : { marginLeft: "8px" }
              }
            >
              <span className="page-title">{selectedPage}</span>
            </div>

            {/* Account dropdown on far right */}
            <div
              className="account-dropdown-wrapper"
              onClick={() => setAccountOpen(!accountOpen)}
              style={{ marginLeft: "auto" }}
            >
              <div className="account-icon">&#x1F310;&#xFE0E;</div>
              <div className="account-arrow">{accountOpen ? "▲" : "▼"}</div>
            </div>

            <ul className={`account-menu ${accountOpen ? "open" : ""}`}>
              <li className="account-username">@User</li>

              {/* Show pages, highlight if selected */}
              {[
                "Counsole",
                "Profile",
                "Civilization",
                "Friends",
                "Messages",
                "Posts",
                "Replies",
                "Settings",
                "Logout",
              ].map((page) => (
                <li
                  key={page}
                  onClick={() => handleSelectPage(page)}
                  className={page === selectedPage ? "selected" : ""}
                >
                  {page}
                </li>
              ))}
            </ul>
          </div>

          {/* The main console area + loader */}
          <div className={`right-console-body ${loading ? "loading" : ""}`}>
            {loading ? (
              <div className="ascii-loader">
                {asciiFrames[asciiFrame].map((line, i) => (
                  <pre key={i} className="ascii-logo">
                    {line}
                  </pre>
                ))}
                <div className="progress-bar">
                  {"["}
                  {"█".repeat(Math.round(progress / 10))}
                  {"▒".repeat(10 - Math.round(progress / 10))}
                  {"]"}
                </div>
              </div>
            ) : (
              <div className="console-output">
                {currentMessages.map((msg, idx) => {
                  if (msg === "-----") {
                    return <div key={idx} className="separator-line" />;
                  }
                  if (
                    msg.includes("FAIV Consensus:") ||
                    msg.includes("Confidence Score:")
                  ) {
                    return (
                      <div key={idx} className="console-line">
                        {extractFinalOutput(msg)}
                      </div>
                    );
                  }
                  return (
                    <div key={idx} className="console-line">
                      {msg}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* If on Counsole => show input form */}
          {selectedPage === "Counsole" && (
            <form className="console-input" onSubmit={handleSubmit}>
              <input
                className="input-field"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="FAIV awaits your query..."
              />
              <button type="submit" className="submit-btn">
                Enter
              </button>
            </form>
          )}
        </div>
      </div>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="modal-backdrop">
          <div className="modal-box">
            <h3>Confirm Deletion</h3>
            <p>This will permanently delete the selected chat.</p>
            <p>
              Type <b>"delete"</b> to confirm:
            </p>
            <input
              type="text"
              value={deleteConfirmInput}
              onChange={(e) => setDeleteConfirmInput(e.target.value)}
            />
            <div className="modal-buttons">
              <button
                onClick={confirmDelete}
                disabled={deleteConfirmInput.toLowerCase().trim() !== "delete"}
              >
                Delete
              </button>
              <button onClick={() => setShowDeleteModal(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
