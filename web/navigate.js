var MR = "Men's Restroom";
var WR = "Women's Restroom";

var SPECIAL_ROOMS = [MR, WR, 'east entrance'];

var MULTICHOICES = [{
	value: MR,
	label: MR,
	selected: false,
	disabled: false},
	{
	value: WR,
	label: WR,
	selected: false,
	disabled: false}
];

// Slight modification of https://github.com/mourner/tinyqueue
function TinyQueue(data) {
    if (!(this instanceof TinyQueue)) return new TinyQueue(data);

    this.data = data || [];
    this.length = this.data.length;

    if (this.length > 0) {
        for (var i = (this.length >> 1); i >= 0; i--) this._down(i);
    }
}

TinyQueue.prototype = {
    push: function (item, priority) {
        this.data.push({i: item, p: priority});
        this.length++;
        this._up(this.length - 1);
    },

    pop: function () {
        if (this.length === 0) return undefined;

        var top = this.data[0];
        this.length--;

        if (this.length > 0) {
            this.data[0] = this.data[this.length];
            this._down(0);
        }
        this.data.pop();

        return top.i;
    },

    peek: function () {
        return this.data[0].i;
    },

	decrease: function(item, newPriority) {
		for (var i = 0; i < this.data.length; i++) {
			if (this.data[i].i === item) {
				this.data[i].p = newPriority;
				this._up(i);
			}
		}
	},

    _up: function (pos) {
        var data = this.data;
        var item = data[pos];

        while (pos > 0) {
            var parent = (pos - 1) >> 1;
            var current = data[parent];
            if (item.p >= current.p) break;
            data[pos] = current;
            pos = parent;
        }

        data[pos] = item;
    },

    _down: function (pos) {
        var data = this.data;
        var halfLength = this.length >> 1;
        var item = data[pos];

        while (pos < halfLength) {
            var left = (pos << 1) + 1;
            var right = left + 1;
            var best = data[left];

            if (right < this.length && data[right].p < best.p) {
                left = right;
                best = data[right];
            }
            if (best.p >= item.p) break;

            data[pos] = best;
            pos = left;
        }

        data[pos] = item;
    }
};

function lowerFirstCharCase(s) {
	return s[0].toLowerCase() + s.slice(1);
}

function append(obj, k, v) {
	if (obj.hasOwnProperty(k)) {
		obj[k].push(v);
	} else {
		obj[k] = [v];
	}
}

function unedge(edge_str) {
	var s = edge_str.split(' ');
	var a = parseInt(s[0], 10);
	var b = parseInt(s[1], 10);
	if (a > b) {
		var sorted_s = b + ' ' + a;
	} else {
		var sorted_s = a + ' ' + b;
	}
	var l = el[sorted_s];
	return {
		a: a,
		b: b,
	    s: edge_str,
		l: l};
}

function sortedEdge(a, b) {
	if (a < b) {
		return a + ' ' + b;
	} else {
		return b + ' ' + a;
	}
}

TURN_ENGLISH = ['Go straight', 'Turn right', 'Go backwards', 'Turn left'];

// get the direction one would take to turn when walking from
// edge (a, b) to edge (b, c)
function getTurnDir(a, b, c) {
	var d1 = DIRECTIONS[sortedEdge(a, b)];
	var d2 = DIRECTIONS[sortedEdge(b, c)];
	var final = d2 - d1 + 4;
	if (a > b != b > c) {
		final += 2;
	}
	return final % 4;
}

NODEGROUP = {};
for (var i = 0; i < GROUPS.length; i++) {
	var group = GROUPS[i];
	for (var j = 0; j < group.nodes.length; j++) {
		NODEGROUP[group.nodes[j]] = group;
	}
}

ROOMCHOICHES = [{value: '', label: '', selected: true, disabled: true}];
ROOMEDGE = {};
for (var k in EDGEROOMS) {
	if (EDGEROOMS.hasOwnProperty(k)) {

		var rooms = EDGEROOMS[k];
		var l = rooms.length;
		for (var i = 0; i < l; i++) {
			var name = rooms[i].n
			if (name === 'e') {
				// handle elevator
			} else if (name !== 'u' && name !== 'd') {
				e = unedge(k);
				e.t = rooms[i].t;
				if (name.search(/^mw?( |$)/) !== -1) {
					append(ROOMEDGE, MR, e);
					continue;
				}
				if (name.search(/^m?w( |$)/) !== -1) {
					append(ROOMEDGE, WR, e);
					continue;
				}
				
				ROOMCHOICHES.push({value: name,
					label: name,
					selected: false,
					disabled: false});
				append(ROOMEDGE, name, e);
			}
		}
	}
}

var srcChoice = null;
var dstChoice = null;

function findPath(startRoom, endRoom) {
	// Check if startRoom and endRoom are already on the same edge
	var start_edge = ROOMEDGE[startRoom][0];
	var sortedStart = sortedEdge(start_edge);
	var endRoomEdges = ROOMEDGE[endRoom];
	for (var i = 0; i < endRoomEdges.length; i++) {
		if (sortedStart === sortedEdge(endRoomEdges[i].a, endRoomEdges[i].b)) {
			return [];
		}
	}

	// node -1 represents starting room, and -2 and below represent goal rooms
	var specialNeighbors = {};
	specialNeighbors[-1] = [
		{n: start_edge.a, d: start_edge.t * start_edge.l},
		{n: start_edge.b, d: (1 - start_edge.t) * start_edge.l}];

	function addNeighbors(node, exclude, replace, length) {
		var neighbors = [{n: replace, d: length}];
		var graph = GRAPH[node];
		for (var i = 0; i < graph.length; i++) {
			if (graph[i] !== exclude) {
				neighbors.push({n: graph[i],
					d: el[sortedEdge(node, graph[i])]});
			}
		}
		specialNeighbors[node] = neighbors;
	}
	
	addNeighbors(start_edge.a, start_edge.b, -1, start_edge.t * start_edge.l);
	addNeighbors(start_edge.b, start_edge.a, -1,
		(1 - start_edge.t) * start_edge.l);

	for (var i = 0; i < endRoomEdges.length; i++) {
		addNeighbors(endRoomEdges[i].a, endRoomEdges[i].b, -2 - i,
			endRoomEdges[i].t * endRoomEdges[i].l);
		addNeighbors(endRoomEdges[i].b, endRoomEdges[i].a, -2 - i,
			(1 - endRoomEdges[i].t) * endRoomEdges[i].l);
		specialNeighbors[-2 - i] = [
			{n: endRoomEdges[i].a, d: endRoomEdges[i].t * endRoomEdges[i].l},
			{n: endRoomEdges[i].b,
				d: (1 - endRoomEdges[i].t) * endRoomEdges[i].l}];
	}

	// Returns a list of {n: int, d: float} objects where n is node id and d
	// is distance.
	function getNeighbors(node) {
		if (specialNeighbors.hasOwnProperty(node)) {
			return specialNeighbors[node];
		}

		var retval = [];
		var graph = GRAPH[node];
		for (var i = 0; i < graph.length; i++) {
			retval.push({n: graph[i], d: el[sortedEdge(node, graph[i])]});
		}
		return retval;
	}

	var prev = {};
	var dist = {};
	dist[-1] = 0;

	var pq = new TinyQueue();
	pq.push(-1, 0);
	while (pq.length > 0) {
		var u = pq.pop();
		if (u <= -2) {
			break;
		}
		var neighbors = getNeighbors(u);
		for (var i = 0; i < neighbors.length; i++) {
			var v = neighbors[i].n;
			var alt = dist[u] + neighbors[i].d;
			if (!dist.hasOwnProperty(v) || alt < dist[v]) {
				if (dist.hasOwnProperty(v)) {
					pq.decrease(v, alt);
				} else {
					pq.push(v, alt);
				}
				dist[v] = alt;
				prev[v] = u;
			}
		}
	}

	// return null if no path could be found
	if (u > -2) {
		return null;
	}

	var endEdge = endRoomEdges[-u - 2];

	var totalDist = dist[u];

	var path = [];
	
	for (var i = 0; i < 2; i++) {
		if (specialNeighbors[u][i].n !== prev[u]) {
			path.push(specialNeighbors[u][i].n);
		}
	}

	u = prev[u];
	while (u > -1) {
		path.push(u);
		u = prev[u];
	}

	var firstNode = path[path.length - 1];

	for (var i = 0; i < 2; i++) {
		if (specialNeighbors[-1][i].n !== firstNode) {
			path.push(specialNeighbors[-1][i].n);
		}
	}

	return {path: path.reverse(), totalDist: totalDist, endEdge: endEdge};
}

// skip groups?
// detect fork
function directionList(nodelist, startRoom, endRoom, endEdge) {
	directions = [];

	if (nodelist.length === 0) {
		// do something
	} else {
		var inGroup = null;
		if (NODEGROUP.hasOwnProperty(nodelist[0]) &&
				NODEGROUP[nodelist[0]].nodes.indexOf(nodelist[1]) > -1) {
			inGroup = NODEGROUP[nodelist[0]];
		} else {
			var start_edge = ROOMEDGE[startRoom][0];
			var d = 'left';
			if (start_edge.a === nodelist[0]) {
				d = 'right';
			}
			directions.push('Face away from ' + startRoom + ', and turn ' + d);
		}

		for (var i = 1; i < nodelist.length - 1; i++) {
			if (inGroup) {
				// check if we are leaving the node group at this point
				if (i < nodelist.length - 1 && inGroup.exits.hasOwnProperty(nodelist[i])
						&& inGroup.nodes.indexOf(nodelist[i+1]) < 0) {
					command = 'Go to ' + inGroup.exits[nodelist[i]];
					var turnDir = getTurnDir(nodelist[i-1], nodelist[i], nodelist[i+1]);
					command += ' and ' + lowerFirstCharCase(TURN_ENGLISH[turnDir]);
					directions.push(nodelist[i]+' '+command);
					inGroup = null;
				} 
				else {directions.push(nodelist[i]+' skip');}
			} else {
				var turnDir = getTurnDir(nodelist[i-1], nodelist[i], nodelist[i+1]);
				var command = TURN_ENGLISH[turnDir];

				if (i < nodelist.length - 1 && NODEGROUP.hasOwnProperty(nodelist[i])) {
					if (NODEGROUP[nodelist[i]].nodes.indexOf(nodelist[i+1]) > -1) {
						inGroup = NODEGROUP[nodelist[i]];
						command += ' into ' + inGroup.name;
					} else {
						command += ', passing ' + NODEGROUP[nodelist[i]].name;
					}
				} else {
					// check if this is a "fork"
					if (GRAPH[nodelist[i]].length === 4) {
						command += ' at the fork';
					} else if (GRAPH[nodelist[i]].length === 2) {
						command += ' at the end of the hallway';
					}
				}

				directions.push(nodelist[i]+' '+command);
			}
		}

		var d = 'left';
		if (endEdge.b === nodelist[nodelist.length - 1]) {
			var d = 'right';
		}
		directions.push('Enter ' + endRoom + ' on your ' + d);
	}
	return directions;
}

function onChoiceChange() {
	var src = srcChoice.getValue(true);
	var dst = dstChoice.getValue(true);
	
	if (!src || !dst) {
		return;
	}

	var foundPath = findPath(src, dst);
	console.log(directionList(foundPath.path, src, dst, foundPath.endEdge));
	console.log(foundPath.path);
}

// sort the choices list to include bathrooms/main entrances first
function sortChoices(a, b) {
	// makes sure the empty one goes on bottom
	if (!a.label) {
		return 1;
	}
	if (!b.label) {
		return -1;
	}

	var apos = SPECIAL_ROOMS.indexOf(a.label);
	var bpos = SPECIAL_ROOMS.indexOf(b.label);

	if (apos < 0 && bpos < 0) {
		return a.label.localeCompare(b.label);
	}

	if (apos < 0) {
		return 1;
	}
	if (bpos < 0) {
		return -1;
	}
	return bpos - apos;
}

window.onload = function() {
	var srcElem = document.getElementById('src');
	var dstElem = document.getElementById('dst');
	srcChoice = new Choices(srcElem, {
		choices: ROOMCHOICHES,
		sortFilter: sortChoices})
	dstChoice = new Choices(dstElem, {
		choices: ROOMCHOICHES.concat(MULTICHOICES),
		sortFilter: sortChoices})

	srcElem.addEventListener('change', onChoiceChange);
	dstElem.addEventListener('change', onChoiceChange);

	var src = 'east entrance';
	var dst = 'common grounds';
	var foundPath = findPath(src, dst);
	console.log(directionList(foundPath.path, src, dst, foundPath.endEdge));
	console.log(foundPath.path);

	var src = '105';
	var dst = '7207';
	var foundPath = findPath(src, dst);
	console.log(directionList(foundPath.path, src, dst, foundPath.endEdge));
	console.log(foundPath.path);
}
