// This file is part of dwinelle-tools.

// dwinelle-tools is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// dwinelle-tools is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with dwinelle-tools.  If not, see <http://www.gnu.org/licenses/>.

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
