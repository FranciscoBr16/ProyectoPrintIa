/**
 * STL Viewer — PrintIA Solutions
 * Visor 3D reutilizable basado en Three.js para archivos .STL
 * 
 * Uso:
 *   initSTLViewer({
 *     containerId: 'visor-3d',      // ID del div contenedor
 *     stlUrl: '/static/uploads/modelos/archivo.stl',
 *     color: 0xE64D85,              // (opcional) color del modelo
 *     bgColor: 0xE2F0F9,            // (opcional) color de fondo
 *     showGrid: true                // (opcional) mostrar grilla
 *   });
 */

function initSTLViewer(options) {
    const container = document.getElementById(options.containerId);
    if (!container) {
        console.error('STL Viewer: contenedor no encontrado:', options.containerId);
        return;
    }

    const stlUrl = options.stlUrl;
    const modelColor = options.color || 0xE64D85;
    const bgColor = options.bgColor || 0xE2F0F9;
    const showGrid = options.showGrid !== undefined ? options.showGrid : true;

    // Dimensiones del contenedor
    const width = container.clientWidth;
    const height = container.clientHeight;

    // --- Spinner de carga ---
    const spinner = document.createElement('div');
    spinner.className = 'stl-spinner';
    spinner.innerHTML = `
        <div class="stl-spinner__circle"></div>
        <span class="stl-spinner__text">Cargando modelo…</span>
    `;
    container.appendChild(spinner);

    // --- Escena ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(bgColor);

    // --- Cámara ---
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 10000);
    camera.position.set(50, 50, 50);

    // --- Renderer ---
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // --- Controles (Orbit) ---
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enablePan = true;
    controls.minDistance = 1;
    controls.maxDistance = 5000;

    // --- Iluminación ---
    // Luz ambiental suave
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    // Luz direccional principal (simula luz del sol)
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9);
    directionalLight.position.set(100, 200, 100);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    // Luz secundaria para suavizar sombras
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-100, 50, -100);
    scene.add(fillLight);

    // --- Grilla (opcional) ---
    if (showGrid) {
        const gridHelper = new THREE.GridHelper(200, 20, 0xc5d8e6, 0xd5e4ef);
        scene.add(gridHelper);
    }

    // --- Cargar STL ---
    const loader = new THREE.STLLoader();

    loader.load(
        stlUrl,
        function (geometry) {
            // Material con aspecto plástico/mate (como impresión 3D)
            const material = new THREE.MeshStandardMaterial({
                color: modelColor,
                roughness: 0.4,
                metalness: 0.1,
                flatShading: false
            });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            // Computar normales para mejor iluminación
            geometry.computeVertexNormals();

            // --- Auto-centrar y escalar el modelo ---
            geometry.computeBoundingBox();
            const boundingBox = geometry.boundingBox;
            const center = new THREE.Vector3();
            boundingBox.getCenter(center);
            
            // Centrar el modelo en el origen
            mesh.position.set(-center.x, -center.y, -center.z);

            // Calcular tamaño para ajustar la cámara
            const size = new THREE.Vector3();
            boundingBox.getSize(size);
            const maxDim = Math.max(size.x, size.y, size.z);

            // Agrupar en un grupo para facilitar rotación
            const group = new THREE.Group();
            group.add(mesh);
            
            // Elevar el modelo para que apoye sobre la grilla
            const yOffset = -boundingBox.min.y + center.y;
            mesh.position.y = -center.y + yOffset;
            
            scene.add(group);

            // Ajustar cámara según tamaño del modelo
            const distance = maxDim * 2.5;
            camera.position.set(distance * 0.7, distance * 0.5, distance * 0.7);
            camera.lookAt(0, size.y * 0.3, 0);
            controls.target.set(0, size.y * 0.3, 0);
            controls.update();

            // Ajustar grilla al tamaño del modelo
            if (showGrid) {
                scene.remove(scene.children.find(c => c instanceof THREE.GridHelper));
                const gridSize = maxDim * 3;
                const gridDivisions = 20;
                const newGrid = new THREE.GridHelper(gridSize, gridDivisions, 0xc5d8e6, 0xd5e4ef);
                scene.add(newGrid);
            }

            // Ocultar spinner
            spinner.style.display = 'none';
        },
        function (xhr) {
            // Progreso de carga
            if (xhr.lengthComputable) {
                const percent = Math.round((xhr.loaded / xhr.total) * 100);
                const textEl = spinner.querySelector('.stl-spinner__text');
                if (textEl) {
                    textEl.textContent = `Cargando modelo… ${percent}%`;
                }
            }
        },
        function (error) {
            console.error('Error cargando STL:', error);
            spinner.innerHTML = `
                <span class="stl-spinner__text" style="color: #e74c3c;">
                    Error al cargar el modelo
                </span>
            `;
        }
    );

    // --- Loop de animación ---
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // --- Responsive ---
    const resizeObserver = new ResizeObserver(function(entries) {
        for (let entry of entries) {
            const w = entry.contentRect.width;
            const h = entry.contentRect.height;
            if (w > 0 && h > 0) {
                camera.aspect = w / h;
                camera.updateProjectionMatrix();
                renderer.setSize(w, h);
            }
        }
    });
    resizeObserver.observe(container);
}
