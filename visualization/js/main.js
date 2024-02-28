// Initialize Scene, Camera, and Renderer
let scene = new THREE.Scene();
let camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = .5;
camera.position.y = -3;

let renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Load the points from output.csv 
    const response = await fetch('../output.csv');
    const text = await response.text();
    const lines = text.split('\n');

    let parsedData = lines.map(line => {
        const columns = line.split(',');
        return columns.map(column => {
            const number = parseFloat(column.trim());
            if (isNaN(number)) {
                console.error('Invalid number conversion', column);
                return 0; // Provide a default value or handle appropriately
            }
            return number;
        });
    });

    // Filter out any invalid data points
    parsedData = parsedData.filter(item => item.length === 3 && !item.some(isNaN));

    if (parsedData.length === 0) {
        console.error("No valid data points found.");
        return;
    }

    console.log(parsedData);

    // Define points using parsedData
    const points = parsedData.map(item => new THREE.Vector3(...item));

    // Create a geometry from the points
    const geometry = new THREE.BufferGeometry().setFromPoints(points);

    // Create a material for the points
    const material = new THREE.PointsMaterial({ color: 0xff0000, size: 0.1 });

    // Create points using the geometry and material
    const pointCloud = new THREE.Points(geometry, material);

    // Add the points to the scene
    scene.add(pointCloud);

    // Render the scene
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

fetchDataAndCreatePoints();