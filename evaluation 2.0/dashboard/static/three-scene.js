/** Three.js particle network background */
(function () {
  const canvas = document.getElementById("three-bg") || document.getElementById("room-bg");
  if (!canvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 42;

  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const COUNT = 45;
  const positions = new Float32Array(COUNT * 3);
  for (let i = 0; i < COUNT * 3; i++) positions[i] = (Math.random() - 0.5) * 70;

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

  const isLight = () => document.documentElement.getAttribute("data-theme") === "light";

  const material = new THREE.PointsMaterial({
    size: 0.35,
    color: isLight() ? 0x6366f1 : 0x818cf8,
    transparent: true,
    opacity: 0.85,
    blending: THREE.AdditiveBlending,
  });

  const points = new THREE.Points(geometry, material);
  scene.add(points);

  const lineGeo = new THREE.BufferGeometry();
  const linePositions = new Float32Array(COUNT * COUNT * 6);
  lineGeo.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
  const lineMat = new THREE.LineBasicMaterial({
    color: isLight() ? 0x6366f1 : 0x818cf8,
    transparent: true,
    opacity: 0.12,
  });
  const lines = new THREE.LineSegments(lineGeo, lineMat);
  scene.add(lines);

  function updateThemeColors() {
    const c = isLight() ? 0x6366f1 : 0x818cf8;
    material.color.setHex(c);
    lineMat.color.setHex(c);
    lineMat.opacity = isLight() ? 0.08 : 0.12;
  }

  window.addEventListener("themechange", updateThemeColors);

  let mx = 0, my = 0;
  document.addEventListener("mousemove", (e) => {
    mx = (e.clientX / window.innerWidth - 0.5) * 8;
    my = (e.clientY / window.innerHeight - 0.5) * 8;
  });

  let frame = 0;
  function animate() {
    requestAnimationFrame(animate);
    frame++;
    points.rotation.y += 0.0006;
    points.rotation.x += 0.0002;
    camera.position.x += (mx - camera.position.x) * 0.02;
    camera.position.y += (-my - camera.position.y) * 0.02;
    camera.lookAt(0, 0, 0);

    if (frame % 2 === 0) {
      const pos = geometry.attributes.position.array;
      const lp = lineGeo.attributes.position.array;
      let idx = 0;
      const maxDist = 14;
      for (let i = 0; i < COUNT; i++) {
        for (let j = i + 1; j < COUNT; j++) {
          const dx = pos[i * 3] - pos[j * 3];
          const dy = pos[i * 3 + 1] - pos[j * 3 + 1];
          const dz = pos[i * 3 + 2] - pos[j * 3 + 2];
          if (dx * dx + dy * dy + dz * dz < maxDist * maxDist) {
            lp[idx++] = pos[i * 3]; lp[idx++] = pos[i * 3 + 1]; lp[idx++] = pos[i * 3 + 2];
            lp[idx++] = pos[j * 3]; lp[idx++] = pos[j * 3 + 1]; lp[idx++] = pos[j * 3 + 2];
          }
        }
      }
      lineGeo.setDrawRange(0, idx / 3);
      lineGeo.attributes.position.needsUpdate = true;
    }

    renderer.render(scene, camera);
  }

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  animate();
})();
