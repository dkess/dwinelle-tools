// @license magnet:?xt=urn:btih:1f739d935676111cfff4b4693e3816e664797050&dn=gpl-3.0.txt GPL-v3-or-Later
// This file is part of Dwinelle Navigator.

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// Dwinelle Navigator is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

var MR = "Men's restroom";
var WR = "Women's restroom";

var SPECIAL_ROOMS = [MR, WR, 'Main entrance'];

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

if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position){
      position = position || 0;
      return this.substr(position, searchString.length) === searchString;
  };
}

function removeChildren(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

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
    group.type = group.name.startsWith('Stair ');
    for (var j = 0; j < group.nodes.length; j++) {
        if (!NODEGROUP[group.nodes[j]]) {
            NODEGROUP[group.nodes[j]] = [];
        }
        NODEGROUP[group.nodes[j]].push(group);
    }
}

ROOMCHOICHES = [];
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
    var sortedStart = sortedEdge(start_edge.a, start_edge.b);
    var endRoomEdges = ROOMEDGE[endRoom];
    for (var i = 0; i < endRoomEdges.length; i++) {
        if (sortedStart === sortedEdge(endRoomEdges[i].a, endRoomEdges[i].b)) {
            var startT = start_edge.t;
            if (endRoomEdges[i].a === start_edge.a) {
                var endT = endRoomEdges[i].t;
            } else {
                var endT = 1 - endRoomEdges[i].t;
            }

            var totalDist = Math.abs(startT - endT) * start_edge.l;

            if (endT > startT) {
                var path = [start_edge.a, start_edge.b];
            } else {
                var path = [start_edge.b, start_edge.a];
            }

            return {path: path,
                totalDist: totalDist,
                startEdge: start_edge,
                endEdge: endRoomEdges[i]};
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

    return {path: path.reverse(),
        totalDist: totalDist,
        startEdge: start_edge,
        endEdge: endEdge};
}

function groupType(g) {
    return g.name.startsWith('Stair');
}

function directionList(nodelist, startRoom, endRoom, endEdge) {
    var onGroup = [];

   for (var i = 0; i < nodelist.length; i = onGroup.length) {
        var prev = onGroup[i-1];
        if (prev
                && ((prev.type && prev.nodes.indexOf(nodelist[i]) >= 0)
                    || (!prev.type && !prev.exits[nodelist[i]]))) {
            onGroup.push(onGroup[i-1]);
        } else {
            var groupA = NODEGROUP[nodelist[i]];
            var groupB = NODEGROUP[nodelist[i+1]];
            var toAdd = null;
            if (groupA && groupB) {
                var common = groupA.filter(function (x) {
                    return groupB.indexOf(x) !== -1;
                });
                if (common.length > 1) {
                    if (nodelist.length > i + 2) {
                        for (var i = 0; i < common.length; i++) {
                            if (common[i].nodes.indexOf(nodelist[i+2]) !== -1) {
                                toAdd = common[i];
                                break;
                            }
                        }
                    }
                } else if (common.length === 1) {
                    toAdd = common[0];
                }
            }

            if (toAdd && !toAdd.type && !prev) {
                onGroup.push(null);
            }
            onGroup.push(toAdd);
        }
    }

    directions = [];

    if (!onGroup[0]) {
        var start_edge = ROOMEDGE[startRoom][0];
        var d = 'left';
        if (start_edge.a === nodelist[0]) {
            d = 'right';
        }
        directions.push('Face away from ' + startRoom + ', and turn ' + d);
    }

    for (var i = 1; i < nodelist.length - 1; i++) {
        var turnDir = getTurnDir(nodelist[i-1], nodelist[i], nodelist[i+1]);
        if (onGroup[i] !== onGroup[i-1]) {
           if (onGroup[i]) {
                if (onGroup[i].type) {
                    if (!onGroup[i-1]) {
                        directions.push(TURN_ENGLISH[turnDir] + ' into '
                            + onGroup[i].name);
                    }
                } else {
                    directions.push('Enter ' + onGroup[i].name);
                }
            }
        }
        if (onGroup[i] && onGroup[i] !== onGroup[i+1]) {
            if (onGroup[i].type) {
                var command = 'Go to ' + onGroup[i].exits[nodelist[i]]
                    + ' and ' + lowerFirstCharCase(TURN_ENGLISH[turnDir]);
                directions.push(command);
            } else {
                directions.push(onGroup[i].exits[nodelist[i+1]]);
            }
        } else if (!onGroup[i]) {
            var command = TURN_ENGLISH[turnDir];

            var passing = null;
            var candidates = NODEGROUP[nodelist[i]];
            if (candidates) {
                for (var j = 0; j < candidates.length; j++) {
                    if (candidates[j].type) {
                        passing = candidates[j];
                        break;
                    }
                }
            }

            if (passing) {
                command += ', passing ' + passing.name;
            } else if (GRAPH[nodelist[i]].length === 4) {
                command += ' at the fork';
            } else if (GRAPH[nodelist[i]].length === 3) {
                var forkname = FORKS[nodelist[i]];
                if (forkname && turnDir === 0) {
                    for (var j = 0; j < 3; j++) {
                        var turnDir = getTurnDir(GRAPH[nodelist[i]][j]);
                        if (turnDir === 1 || turnDir === 3) {
                            break;
                        }
                    }
                    command += ', passing the ' + forkname + ' on your ';
                    if (turnDir === 1) {
                        command += 'left';
                    } else {
                        command += 'right';
                    }
                }
            } else if (GRAPH[nodelist[i]].length === 2) {
                command += ' at the end of the hallway';
            }

            directions.push(command);
        }
    }

    var d = 'left';
    if (endEdge.b === nodelist[nodelist.length - 1]) {
        var d = 'right';
    }
    directions.push('Enter ' + endRoom + ' on your ' + d);

    return directions;
}

function onChoiceChange() {
    var src = srcChoice.getValue(true);
    var dst = dstChoice.getValue(true);

    if (!src || !dst) {
        genScene([]);
        return;
    }

    window.location.hash = ('src=' + encodeURIComponent(src)
        + '&dst=' + encodeURIComponent(dst));

    var foundPath = findPath(src, dst);
    dlist = directionList(foundPath.path, src, dst, foundPath.endEdge);
    console.log(directionList(foundPath.path, src, dst, foundPath.endEdge));
    console.log(foundPath);
    putDirections(dlist, foundPath.totalDist / 1000);

    var startFrac = foundPath.startEdge.t;
    if (foundPath.startEdge.a !== foundPath.path[0]) {
        startFrac = 1 - startFrac;
    }

    var endFrac = foundPath.endEdge.t;
    if (foundPath.endEdge.a !== foundPath.path[foundPath.path.length - 1]) {
        endFrac = 1 - endFrac;
    }
    genScene(foundPath.path, startFrac, endFrac);
}

// sort the choices list to include bathrooms/main entrances first
function sortChoices(a, b) {
    // makes sure the empty one goes on bottom
    if (!a.value) {
        return 1;
    }
    if (!b.value) {
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

function findChoice(value) {
    return function(c) {
        return c.value === value;
    };
}

SRCDEFAULT = [{value: '', label: 'Select a starting point...', selected: true, disabled: true}];
DSTDEFAULT = [{value: '', label: 'Select a destination...', selected: true, disabled: true}];
window.onload = function() {
    var srcElem = document.getElementById('src');
    var dstElem = document.getElementById('dst');
    srcChoice = new Choices(srcElem, {
        choices: ROOMCHOICHES.concat(SRCDEFAULT),
        sortFilter: sortChoices})
    dstChoice = new Choices(dstElem, {
        choices: ROOMCHOICHES.concat(DSTDEFAULT).concat(MULTICHOICES),
        sortFilter: sortChoices})

    srcElem.addEventListener('change', onChoiceChange);
    dstElem.addEventListener('change', onChoiceChange);

    var hash = window.location.hash.substr(1);
    if (hash) {
        var chosenSrc = decodeURIComponent(hash.match(/(?:^|\&)src\=([^\&]+)/)[1]);
        if (chosenSrc) {
            srcChoice.setValueByChoice(chosenSrc);
        }

        var chosenDst = decodeURIComponent(hash.match(/(?:^|\&)dst\=([^\&]+)/)[1]);
        if (chosenDst) {
            dstChoice.setValueByChoice(chosenDst);
        }

        onChoiceChange();
    }

    // swap button
    document.getElementById('swapsvg').onclick = function() {
        var src = srcChoice.getValue(true);
        var dst = dstChoice.getValue(true);
        console.log(src, dst);

        if (dstChoice.presetChoices.some(findChoice(src))
                && srcChoice.presetChoices.some(findChoice(dst))) {
            srcChoice.setValueByChoice(dst);
            dstChoice.setValueByChoice(src);
            onChoiceChange();
        }
    };
}

function putDirections(dirList, eta) {
    var span_eta = document.getElementById('eta');
    removeChildren(span_eta);
    span_eta.appendChild(document.createTextNode(Math.round(eta)));

    var ol = document.getElementById('directions-ol');
    removeChildren(ol);

    for (var i = 0; i < dirList.length; i++) {
        var li = document.createElement('li');
        li.className = 'direction';
        li.appendChild(document.createTextNode(dirList[i]));

        ol.appendChild(li);
    }
    document.getElementById('directions').style.visibility = 'visible';
}
// @license-end
