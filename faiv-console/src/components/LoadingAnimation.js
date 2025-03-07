// LoadingAnimation.js
import React, { useState, useEffect } from "react";

const frames = ["◐", "◓", "◑", "◒"];

const LoadingAnimation = () => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % frames.length);
    }, 200); // Rotate every 200ms
    return () => clearInterval(interval);
  }, []);

  return <span className="loading-animation">{frames[index]}</span>;
};

export default LoadingAnimation;
