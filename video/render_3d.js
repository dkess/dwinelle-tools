SHRINK=305;
X_OFFSET=0;
Y_OFFSET=-200;

Z_SCALE=0.002;

var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild(renderer.domElement);

camera.position.set(0, 0, 400);
camera.lookAt(new THREE.Vector3(0, 0, 0));

var scene = new THREE.Scene();

var material = new THREE.LineBasicMaterial({ color: 0xffffff });
var material_red = new THREE.LineBasicMaterial({ color: 0xff0000 });

for (var edge_str in el) {
    var s = edge_str.split(' ');
    var a = parseInt(s[0], 10);
    var b = parseInt(s[1], 10);

    var geometry = new THREE.Geometry();
    var ap = coords[a];
    var bp = coords[b];
    geometry.vertices.push(new THREE.Vector3(ap.x/SHRINK + X_OFFSET, ap.z * Z_SCALE, -(ap.y / SHRINK + Y_OFFSET)));
    geometry.vertices.push(new THREE.Vector3(bp.x/SHRINK + X_OFFSET, bp.z * Z_SCALE, -(bp.y / SHRINK + Y_OFFSET)));

    if (eh.hasOwnProperty(edge_str) && eh[edge_str].l < 0) {
	var m = material_red;
	console.log(edge_str);
    } else {
	var m = material;
    }
    var line = new THREE.Line(geometry, m);
    scene.add(line);
}
/*
var geometry = new THREE.Geometry();
geometry.vertices.push(new THREE.Vector3(-10, 0, 0));
geometry.vertices.push(new THREE.Vector3(10, 0, 0));
var line = new THREE.Line(geometry, material);

scene.add(line);
*/
controls = new THREE.OrbitControls(camera, renderer.domElement);


function animate() {
    requestAnimationFrame( animate );
    controls.update();
    render();
}

function render() {
    renderer.render(scene, camera);
}

animate();
