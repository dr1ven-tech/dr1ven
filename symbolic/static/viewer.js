var _socket = io.connect(
  "ws://"+window.location.hostname+':'+window.location.port
)
var _scene = new THREE.Scene();
var _renderer = new THREE.WebGLRenderer({
  alpha: true,
});
var _camera = new THREE.PerspectiveCamera(
  90, window.innerWidth / window.innerHeight, 0.1, 10000,
);
var _controls = new THREE.TrackballControls(_camera);

var render = () => {
  _controls.update();
  _renderer.render(_scene, _camera);
};

var animate = () => {
  requestAnimationFrame(animate);
  render();

};

var trace = (map_specification, entities) => {
  MAP_COLORS = {
    0: 0x150026,
    1: 0x5e665d,
    2: 0xdb7011,
    3: 0x006600,
  };

  ENTITIES_COLORS = {
    1: 0xffffff,
    2: 0xaaaaaa,
    3: 0x006600,
    4: 0x660000,
    6: 0xff0000,
  };

  var geometry = new THREE.BoxGeometry(1, 1, 1);
  geometry.vertices.length = 0;
  geometry.faces.length = 0;


  for (var l = 0; l < map_specification.length; l++) {
    for (var s = 0; s < map_specification[l].length; s++) {
      segment = map_specification[l][s]
      for(var w = 0; w < segment[2].length; w++) {
        v0 = new THREE.Vector3(segment[0], (7-l) * 7 + w, 0);
        v1 = new THREE.Vector3(segment[1], (7-l) * 7 + w, 0);
        v2 = new THREE.Vector3(segment[0], (7-l) * 7 + w+1, 0);
        v3 = new THREE.Vector3(segment[1], (7-l) * 7 + w+1, 0);
        geometry.vertices.push(v0);
        geometry.vertices.push(v1);
        geometry.vertices.push(v2);
        geometry.vertices.push(v3);

        var f = new THREE.Face3(
          geometry.vertices.length-4,
          geometry.vertices.length-3,
          geometry.vertices.length-2,
          THREE.Vector3(0, 0, 1)
        );
        f.color = new THREE.Color(MAP_COLORS[segment[2][w]]);
        f.vertexColors = [f.color,f.color,f.color,f.color];
        geometry.faces.push(f);

        var f = new THREE.Face3(
          geometry.vertices.length-1,
          geometry.vertices.length-2,
          geometry.vertices.length-3,
          THREE.Vector3(0, 0, 1)
        );
        f.color = new THREE.Color(MAP_COLORS[segment[2][w]]);
        f.vertexColors = [f.color,f.color,f.color,f.color];
        geometry.faces.push(f);
      }
    }
  }

  for (var e = 0; e < entities.length; e++) {
    type = entities[e]['type']
    occupation = entities[e]['occupation']

    orientation = occupation[0]
    lane = occupation[1]
    position = occupation[2]
    width = occupation[3]
    height = occupation[4]

    // Forward orientation.
    var v0, v1, v2, v3;
    if (orientation == 1) {
      v0 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1], position[2]);
      v1 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1] + width, position[2]);
      v2 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1], position[2] + height);
      v3 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1] + width, position[2] + height);
    } else {
      v0 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1], position[2]);
      v1 = new THREE.Vector3(position[0] + width, (7-lane) * 7 + position[1], position[2]);
      v2 = new THREE.Vector3(position[0], (7-lane) * 7 + position[1], position[2] + height);
      v3 = new THREE.Vector3(position[0] + width, (7-lane) * 7 + position[1], position[2] + height);
    }

    geometry.vertices.push(v0);
    geometry.vertices.push(v1);
    geometry.vertices.push(v2);
    geometry.vertices.push(v3);

    var f = new THREE.Face3(
      geometry.vertices.length-4,
      geometry.vertices.length-3,
      geometry.vertices.length-2,
      THREE.Vector3(-1, 0, 0)
    );
    f.color = new THREE.Color(ENTITIES_COLORS[type]);
    f.vertexColors = [f.color,f.color,f.color,f.color];
    geometry.faces.push(f);

    var f = new THREE.Face3(
      geometry.vertices.length-1,
      geometry.vertices.length-2,
      geometry.vertices.length-3,
      THREE.Vector3(-1, 0, 0)
    );
    f.color = new THREE.Color(ENTITIES_COLORS[type]);
    f.vertexColors = [f.color,f.color,f.color,f.color];
    geometry.faces.push(f);
  }

  // geometry.computeFaceNormals();
  geometry.verticesNeedUpdate = true;
  geometry.elementsNeedUpdate = true;
  geometry.normalsNeedUpdate = true;
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  // Create surface mesh
  var material  = new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true
  });
  material.opacity = 0.8;
  material.side = THREE.DoubleSide;
  surface = new THREE.Mesh(geometry, material);
  surface.doubleSided = false;

  surface.position.x = -400;
  surface.position.y = 0;
  surface.position.z = 8*4;

  surface.rotation.x = -Math.PI/2
  surface.name = "all"

  return surface
};

(() => {
  _renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(_renderer.domElement);

  _camera.position.x = -40;
  _camera.position.y = +30;
  _camera.position.z = 0;

  animate();
})();

_socket.on('highway', (data) => {
  // console.log(data)
  var obj = _scene.getObjectByName("all");
  _scene.remove(obj);
  surface = trace(data['map'], data['entities']);
  _scene.add(surface);
})
