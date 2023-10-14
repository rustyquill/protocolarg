$(function() {
  $(".glitch-background").mgGlitch({
    destroy: false,
    glitch: true,
    scale: false,
    blend: true,
    blendModeType: "hue",
    glitch1TimeMin: 200,
    glitch1TimeMax: 400,
    glitch2TimeMin: 10,
    glitch2TimeMax: 100,
  });
});
