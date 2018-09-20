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

// var trace = (voxels, opacity) => {
//   var geometry = new THREE.BoxGeometry(1, 1, 1);
//   var result = GreedyMesh(voxels.voxels, voxels.dims)
// 
//   geometry.vertices.length = 0;
//   geometry.faces.length = 0;
// 
//   for(var i=0; i<result.vertices.length; ++i) {
//     var q = result.vertices[i];
//     geometry.vertices.push(new THREE.Vector3(q[0], q[1], q[2]));
//   }
// 
//   for(var i=0; i<result.faces.length; ++i) {
//     var q = result.faces[i];
//     if(q.length === 5) {
//       var f1 = new THREE.Face3(q[0], q[1], q[2]);
//       f1.color = new THREE.Color(q[4]);
//       f1.vertexColors = [f1.color,f1.color,f1.color,f1.color];
//       geometry.faces.push(f1);
//       var f2 = new THREE.Face3(q[2], q[3], q[0]);
//       f2.color = new THREE.Color(q[4]);
//       f2.vertexColors = [f2.color,f2.color,f2.color,f2.color];
//       geometry.faces.push(f2);
//     } else if(q.length == 4) {
//       var f = new THREE.Face3(q[0], q[1], q[2]);
//       f.color = new THREE.Color(q[3]);
//       f.vertexColors = [f.color,f.color,f.color];
//       geometry.faces.push(f);
//     }
//   }
// 
//   geometry.computeFaceNormals();
//   geometry.verticesNeedUpdate = true;
//   geometry.elementsNeedUpdate = true;
//   geometry.normalsNeedUpdate = true;
//   geometry.computeBoundingBox();
//   geometry.computeBoundingSphere();
// 
//   var bb = geometry.boundingBox;
// 
//   // Create surface mesh
//   var material  = new THREE.MeshBasicMaterial({
//     vertexColors: true, transparent: true
//   });
//   material.opacity = opacity;
//   surfacemesh = new THREE.Mesh(geometry, material);
//   surfacemesh.doubleSided = false;
// 
//   // Create wire mesh
//   // var material = new THREE.MeshBasicMaterial({
//   //   color : 0xffffff, wireframe : true, transparent: true,
//   // });
//   // material.opacity = 0.1;
//   // wiremesh = new THREE.Mesh(geometry, material);
//   // wiremesh.doubleSided = true;
// 
//   // wiremesh.position.x = surfacemesh.position.x = -200;
//   // wiremesh.position.y = surfacemesh.position.y = -(bb.max.y + bb.min.y) / 2.0;
//   // wiremesh.position.z = surfacemesh.position.z = -(bb.max.z + bb.min.z) / 2.0;
// 
//   surfacemesh.position.x = -400;
//   surfacemesh.position.y = 0;
//   // surfacemesh.position.y = -(bb.max.y + bb.min.y) / 2.0;
//   // surfacemesh.position.z = -(bb.max.z + bb.min.z) / 2.0;
// 
//   _scene.add(surfacemesh);
//   // _scene.add(wiremesh);
// };

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
    1: '0xffffff',
    2: '0xaaaaaa',
    3: '0x006600',
    4: '0x660000',
    6: '0xff0000',
  };

  var geometry = new THREE.BoxGeometry(1, 1, 1);
  geometry.vertices.length = 0;
  geometry.faces.length = 0;


  for (var l = 0; l < map_specification.length; l++) {
    for (var s = 0; s < map_specification[l].length; s++) {
      segment = map_specification[l][s]
      for(var w = 0; w < segment[2].length; w++) {
        v0 = new THREE.Vector3(segment[0], (7-l) * 7 + w, 0)
        v1 = new THREE.Vector3(segment[1], (7-l) * 7 + w, 0)
        v2 = new THREE.Vector3(segment[0], (7-l) * 7 + w+1, 0)
        v3 = new THREE.Vector3(segment[1], (7-l) * 7 + w+1, 0)
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
  surfacemesh = new THREE.Mesh(geometry, material);
  surfacemesh.doubleSided = false;

  surfacemesh.position.x = -400;
  surfacemesh.position.y = 0;
  surfacemesh.position.z = 0;

  _scene.add(surfacemesh);

  // entities_occupation = {}
  // entities.forEach((entity) => {
  //   entity['occupation'].forEach((occ) => {
  //     entities_occupation[occ.join('_')] = entity['type']
  //   });
  // });

  //   var voxels = voxel.generate([0,0,0], [2000,11,8*7], function(x,y,z) {
  //     l = Math.floor(z / 7)
  //     w = z % 7
  //     d = x
  //     h = y-1
  //
  //     if (y == 0) {
  //       // Map
  //       if (l < map_specification.length) {
  //         for (var s = 0; s < map_specification[l].length; s++) {
  //           segment = map_specification[l][s]
  //           if(d >= segment[0] && d < segment[1]) {
  //             return MAP_COLORS[segment[2][6-w]];
  //           }
  //         }
  //       }
  //     } else {
  //       // Entties
  //       for (var e = 0; e < entities.length; e++) {
  //         type = entities[e]['type']
  //         occupation = entities[e]['occupation']
  //
  //         if(occupation[1] == l) {
  //         }
  //         if(occupation[0] == 1) {
  //           }
  //         }
  //       }
  //       key = l+'_'+d+'_'+(6-w)+'_'+h
  //       if(key in entities_occupation) {
  //         return ENTITIES_COLORS[entities_occupation[key]];
  //       }
  //     }
  //
  //     return 0
  //   })
};

(() => {
  _renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(_renderer.domElement);

  _camera.position.x = -40;
  _camera.position.y = 0;
  _camera.position.z = +30;

  animate();
})();

_socket.on('highway', (data) => {
  console.log(data)
  trace(data['map'], data['entities']);
})
