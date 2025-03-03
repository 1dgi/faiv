import React, { useState, useEffect } from "react";

const frames = [
  "◐ Processing...",
  "◓ Processing...",
  "◑ Processing...",
  "◒ Processing..."
];

const LoadingAnimation = () => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % frames.length);
    }, 200); // Rotate every 200ms
    return () => clearInterval(interval);
  }, []);

  return <div className="loading">{frames[index]}</div>;
};

export default LoadingAnimation;
