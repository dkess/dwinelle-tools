W = 300;
H = 300;

SHRINK=305;
X_OFFSET=0;
Y_OFFSET=-200;

Z_SCALE=0.002;
Z_OFFSET=-35;

//var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 5000);
var camera = new THREE.PerspectiveCamera(55, W/H, 0.1, 5000);
var renderer = new THREE.WebGLRenderer();
renderer.setSize(W, H);
document.getElementById('vis').appendChild(renderer.domElement);

camera.position.set(-300, 180, 180);
camera.lookAt(new THREE.Vector3(0, 0, 0));

var material = new THREE.LineBasicMaterial({color: 0x000000});
var hilight = new THREE.LineBasicMaterial({color: 0x0087C6});
var faded = new THREE.LineBasicMaterial({color: 0xbfbfbf});
var srcSphere = new THREE.MeshBasicMaterial({color: 0x157e2d});
var dstSphere = new THREE.MeshBasicMaterial({color: 0x7e1515});

function makeLine(ax, ay, az, bx, by, bz, m) {
    var geometry = new THREE.Geometry();
    geometry.vertices.push(new THREE.Vector3(ax/SHRINK + X_OFFSET, az * Z_SCALE + Z_OFFSET, -(ay / SHRINK + Y_OFFSET)));
    geometry.vertices.push(new THREE.Vector3(bx/SHRINK + X_OFFSET, bz * Z_SCALE + Z_OFFSET, -(by / SHRINK + Y_OFFSET)));

    return new THREE.Line(geometry, m);
}

function splitLine(scene, ap, bp, fraction, m1, m2) {
    var mx = ap.x + fraction * (bp.x - ap.x);
    var my = ap.y + fraction * (bp.y - ap.y);
    var mz = ap.z + fraction * (bp.z - ap.z);

    scene.add(makeLine(ap.x, ap.y, ap.z, mx, my, mz, m1));
    scene.add(makeLine(mx, my, mz, bp.x, bp.y, bp.z, m2));
}

// needed when the source and destination are on the same edge
function tripleSplit(scene, ap, bp, f1, f2, m1, m2) {
    if (f1 > f2) {
	var t = f1;
	f1 = f2;
	f2 = t;
    }
    var m1x = ap.x + f1 * (bp.x - ap.x);
    var m1y = ap.y + f1 * (bp.y - ap.y);
    var m1z = ap.z + f1 * (bp.z - ap.z);

    var m2x = ap.x + f2 * (bp.x - ap.x);
    var m2y = ap.y + f2 * (bp.y - ap.y);
    var m2z = ap.z + f2 * (bp.z - ap.z);

    scene.add(makeLine(ap.x, ap.y, ap.z, m1x, m1y, m1z, m1));
    scene.add(makeLine(m1x, m1y, m1z, m2x, m2y, m2z, m2));
    scene.add(makeLine(m2x, m2y, m2z, bp.x, bp.y, bp.z, m1));
}

function endSphere(ap, bp, fraction, m) {
    var mx = ap.x + fraction * (bp.x - ap.x);
    var my = ap.y + fraction * (bp.y - ap.y);
    var mz = ap.z + fraction * (bp.z - ap.z);

    var geometry = new THREE.SphereGeometry(2);
    var sphere = new THREE.Mesh(geometry, m);
    sphere.position.set(mx/SHRINK + X_OFFSET, mz * Z_SCALE + Z_OFFSET, -(my / SHRINK + Y_OFFSET));
    return sphere;
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
	    if (path.length === 2) {
		var sf = (bi === 0) ? 1 - startFrac : startFrac;
		var ef = (bi === 1) ? 1 - endFrac : endFrac;
		tripleSplit(scene, ap, bp, sf, ef, faded, hilight);
		scene.add(endSphere(ap, bp, sf, srcSphere));
		scene.add(endSphere(ap, bp, ef, dstSphere));
	    } else if (ai === 0) {
		splitLine(scene, ap, bp, startFrac, faded, hilight);
		scene.add(endSphere(ap, bp, startFrac, srcSphere));
	    } else if (ai === path.length - 1) {
		splitLine(scene, ap, bp, endFrac, faded, hilight);
		scene.add(endSphere(ap, bp, endFrac, dstSphere));
	    } else if (bi === 0) {
		splitLine(scene, ap, bp, 1 - startFrac, hilight, faded);
		scene.add(endSphere(ap, bp, 1 - startFrac, srcSphere));
	    } else if (bi === path.length - 1) {
		splitLine(scene, ap, bp, 1 - endFrac, hilight, faded);
		scene.add(endSphere(ap, bp, 1 - endFrac, dstSphere));
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

function onWindowResize() {
    var container = document.getElementById('vis');
    var width = container.clientWidth;
    var height = container.clientHeight;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
}

window.addEventListener('resize', onWindowResize, false);
onWindowResize();
