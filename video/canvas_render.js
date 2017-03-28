var startx;
var starty;
var drawingBox = false;

function getPointsInBox(x1, y1, x2, y2) {
	if (x1 > x2) {
		var t = x1;
		x1 = x2;
		x2 = t;
	}
	if (y1 > y2) {
		var t = y1;
		y1 = y2;
		y2 = t;
	}

	r = [];
	for (var n in coords) {
		if (coords[n].x < x2 && coords[n].x > x1
				&& coords[n].y > y1 && coords[n].y < y2) {
			r.push(n);
		}
	}

	return r;
}

window.onload = function() {
	var canvas = document.getElementById('canvas');

    var elemLeft = canvas.offsetLeft, elemTop = canvas.offsetTop;

	canvas.addEventListener('click', function(e) {
		var x = e.pageX - elemLeft,
			y = e.pageY - elemTop;

		if (drawingBox) {
			console.log(getPointsInBox(startx, starty, x, y));
		} else {
			startx = x;
			starty = y;
		}
		drawingBox = !drawingBox;
	});

	var ctx = canvas.getContext('2d');

	for (var edge_str in el) {
		var s = edge_str.split(' ');
		var a = parseInt(s[0], 10);
		var b = parseInt(s[1], 10);

		ctx.beginPath();
		var ap = coords[a];
		ctx.moveTo(ap.x, ap.y);

		var bp = coords[b];
		ctx.lineTo(bp.x, bp.y);
		ctx.closePath();
		ctx.stroke();
	}

	ctx.textBasline = 'bottom';
	ctx.strokeStyle = 'green';
	for (var n in coords) {
		ctx.strokeText(n, coords[n].x, coords[n].y-2);
	}
}
