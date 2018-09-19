var _socket = io.connect("ws://"+window.location.hostname)
var _scene = new THREE.Scene();
var _renderer = new THREE.WebGLRenderer({
  alpha: true,
});
var _camera = new THREE.PerspectiveCamera(
  90, window.innerWidth / window.innerHeight, 0.1, 10000,
);
var _controls = new THREE.TrackballControls(_camera);

var trace = (voxels, opacity, offset) => {
  var geometry = new THREE.BoxGeometry(1, 1, 1);
  var result = GreedyMesh(voxels.voxels, voxels.dims)

  geometry.vertices.length = 0;
  geometry.faces.length = 0;

  for(var i=0; i<result.vertices.length; ++i) {
    var q = result.vertices[i];
    geometry.vertices.push(new THREE.Vector3(q[0], q[1], q[2]));
  }

  for(var i=0; i<result.faces.length; ++i) {
    var q = result.faces[i];
    if(q.length === 5) {
      var f1 = new THREE.Face3(q[0], q[1], q[2]);
      f1.color = new THREE.Color(q[4]);
      f1.vertexColors = [f1.color,f1.color,f1.color,f1.color];
      geometry.faces.push(f1);
      var f2 = new THREE.Face3(q[2], q[3], q[0]);
      f2.color = new THREE.Color(q[4]);
      f2.vertexColors = [f2.color,f2.color,f2.color,f2.color];
      geometry.faces.push(f2);
    } else if(q.length == 4) {
      var f = new THREE.Face3(q[0], q[1], q[2]);
      f.color = new THREE.Color(q[3]);
      f.vertexColors = [f.color,f.color,f.color];
      geometry.faces.push(f);
    }
  }

  geometry.computeFaceNormals();
  geometry.verticesNeedUpdate = true;
  geometry.elementsNeedUpdate = true;
  geometry.normalsNeedUpdate = true;
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  var bb = geometry.boundingBox;

  // Create surface mesh
  var material  = new THREE.MeshBasicMaterial({
    vertexColors: true, transparent: true
  });
  material.opacity = opacity;
  surfacemesh = new THREE.Mesh(geometry, material);
  surfacemesh.doubleSided = false;

  // Create wire mesh
  // var material = new THREE.MeshBasicMaterial({
  //   color : 0xffffff, wireframe : true, transparent: true,
  // });
  // material.opacity = 0.1;
  // wiremesh = new THREE.Mesh(geometry, material);
  // wiremesh.doubleSided = true;

  // wiremesh.position.x = surfacemesh.position.x = -200;
  // wiremesh.position.y = surfacemesh.position.y = -(bb.max.y + bb.min.y) / 2.0;
  // wiremesh.position.z = surfacemesh.position.z = -(bb.max.z + bb.min.z) / 2.0;

  surfacemesh.position.x = -400;
  surfacemesh.position.y = offset;
  // surfacemesh.position.y = -(bb.max.y + bb.min.y) / 2.0;
  // surfacemesh.position.z = -(bb.max.z + bb.min.z) / 2.0;

  _scene.add(surfacemesh);
  // _scene.add(wiremesh);
};

var render = () => {
  _controls.update();
  _renderer.render(_scene, _camera);
};

var animate = () => {
  requestAnimationFrame(animate);
  render();
};

var build_map = (map_data) => {
  COLOR_MAP = {
    0: '0x150026',
    1: '0x5e665d',
    2: '0xdb7011',
    3: '0x006600',
  }

  var voxels = voxel.generate([0,0,0], [2000,1,8*7], function(x,y,z) {
    l = Math.floor(z / 7)
    w = z % 7
    d = x
    return COLOR_MAP[map_data[l][d][6-w][0]]
  })

  trace(voxels, 0.5, -1.0)
};

var build_entity = (entity_data) => {
  COLOR_MAP = {
    1: '0xffffff',
    2: '0xaaaaaa',
    3: '0x006600',
    4: '0x660000',
    6: '0xdb7011',
  }

  occ_map = {}
  entity_data['occupation'].forEach((occ) => {
    occ_map[occ.join('_')] = entity_data['type']
  });

  var voxels = voxel.generate([0,0,0], [2000,10,8*7], function(x,y,z) {
    l = Math.floor(z / 7)
    w = z % 7
    d = x
    h = y
    key = l+'_'+d+'_'+(6-w)+'_'+h
    if(key in occ_map) {
      return COLOR_MAP[occ_map[key]]
    }
    return 0
  })

  trace(voxels, 1.0, 0.0)
};

(() => {
  _renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(_renderer.domElement);

  _camera.position.z = 0;
  _camera.position.y = +30;
  _camera.position.x = -40;

  animate();
})();

_socket.on('highway', (data) => {
  build_map(data['map']);
  data['entities'].forEach((e) => {
    build_entity(e);
  })
})
