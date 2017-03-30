W = 300;
H = 300;

SHRINK=305;
X_OFFSET=0;
Y_OFFSET=-200;

Z_SCALE=0.002;

//var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
var camera = new THREE.PerspectiveCamera(75, W/H, 0.1, 5000);
var renderer = new THREE.WebGLRenderer();
renderer.setSize(W, H);
document.getElementById('vis').appendChild(renderer.domElement);

camera.position.set(0, 0, 400);
camera.lookAt(new THREE.Vector3(0, 0, 0));

var material = new THREE.LineBasicMaterial({color: 0x000000});
var hilight = new THREE.LineBasicMaterial({color: 0x0000ff});
var faded = new THREE.LineBasicMaterial({color: 0xbfbfbf});

function makeLine(ax, ay, az, bx, by, bz, m) {
    var geometry = new THREE.Geometry();
    geometry.vertices.push(new THREE.Vector3(ax/SHRINK + X_OFFSET, az * Z_SCALE, -(ay / SHRINK + Y_OFFSET)));
    geometry.vertices.push(new THREE.Vector3(bx/SHRINK + X_OFFSET, bz * Z_SCALE, -(by / SHRINK + Y_OFFSET)));

    return new THREE.Line(geometry, m);
}

function splitLine(scene, ap, bp, fraction, m1, m2) {
    var mx = ap.x + fraction * (bp.x - ap.x);
    var my = ap.y + fraction * (bp.y - ap.y);
    var mz = ap.z + fraction * (bp.z - ap.z);

    scene.add(makeLine(ap.x, ap.y, ap.z, mx, my, mz, m1));
    scene.add(makeLine(mx, my, mz, bp.x, bp.y, bp.z, m2));
}

var scene = null
function genScene(path, startFrac, endFrac) {
    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xffffff );

    for (var edge_str in el) {
	var s = edge_str.split(' ');
	var a = parseInt(s[0], 10);
	var b = parseInt(s[1], 10);

	var ap = coords[a];
	var bp = coords[b];

	var ai = path.indexOf(a);
	var bi = path.indexOf(b);

	if (ai >= 0 && bi >= 0 && Math.abs(ai - bi) === 1) {
	    if (ai === 0) {
		splitLine(scene, ap, bp, startFrac, faded, hilight);
	    } else if (ai === path.length - 1) {
		splitLine(scene, ap, bp, endFrac, faded, hilight);
	    } else if (bi === 0) {
		splitLine(scene, ap, bp, startFrac, hilight, faded);
	    } else if (bi === path.length - 1) {
		splitLine(scene, ap, bp, endFrac, hilight, faded);
	    } else {
		scene.add(makeLine(ap.x, ap.y, ap.z, bp.x, bp.y, bp.z, hilight));
	    }
	} else {
	    if (path.length === 0) {
		var m = material;
	    } else {
		var m = faded;
	    }
	    var line = makeLine(ap.x, ap.y, ap.z, bp.x, bp.y, bp.z, m);
	    scene.add(line);
	}
    }
}
genScene([], 0, 0);

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
