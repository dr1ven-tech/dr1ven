var scene = new THREE.Scene();
var renderer = new THREE.WebGLRenderer({ alpha: true });
var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
var cameraControls = new THREE.TrackballControls(camera);

function render() {
  var PIseconds = Date.now() * Math.PI;
  cameraControls.update();
  renderer.render(scene, camera);
}

function animate() {
  requestAnimationFrame(animate);
  render();
}

function setup() {
  var geometry = new THREE.BoxGeometry(1, 1, 1);
  var material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });

  var data = voxel.generate([0,0,0], [2000,8*7,10], function(x,y,z) {
    if(x*x+y*y+z*z <= 4*4) {
      return '0xff0000'
    }
    if(x*x+y*y+z*z <= 16*16) {
      return '0x00ff00'
    }
    return 0
  })

  var result = GreedyMesh(data.voxels, data.dims)

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

      var f2 = new THREE.Face3(q[2], q[3], q[0]);
      f2.color = new THREE.Color(q[4]);
      f2.vertexColors = [f2.color,f2.color,f2.color,f2.color];

      geometry.faces.push(f1);
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

  //Create surface mesh
  var material  = new THREE.MeshBasicMaterial({
    vertexColors: true
  });
  surfacemesh = new THREE.Mesh( geometry, material );
  surfacemesh.doubleSided = false;

  var wirematerial = new THREE.MeshBasicMaterial({
    color : 0xffffff
    , wireframe : true
  });
  wiremesh = new THREE.Mesh(geometry, wirematerial);
  wiremesh.doubleSided = true;

  wiremesh.position.x = surfacemesh.position.x = -(bb.max.x + bb.min.x) / 2.0;
  wiremesh.position.y = surfacemesh.position.y = -(bb.max.y + bb.min.y) / 2.0;
  wiremesh.position.z = surfacemesh.position.z = -(bb.max.z + bb.min.z) / 2.0;

  scene.add(surfacemesh);
  scene.add(wiremesh);

  camera.position.z = 0;
  camera.position.y = 0;
  camera.position.x = -20;

  animate();
}

(function() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  setup()
})()

