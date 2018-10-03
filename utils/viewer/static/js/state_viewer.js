
class StateViewer {
  constructor(container) {
    this.scene = new THREE.Scene();
    this.renderer = new THREE.WebGLRenderer({
      alpha: true,
    });

    this.camera = new THREE.PerspectiveCamera(
      90, container.width() / container.height(), 0.1, 10000,
    );
    this.controls = new THREE.TrackballControls(this.camera);

    this.renderer.setSize(container.width(), container.height())
    container.append(this.renderer.domElement);

    this.camera.position.x = 0;
    this.camera.position.y = -20;
    this.camera.position.z = 10;

    var _this = this
    this.loop = () => {
      requestAnimationFrame(_this.loop);
      _this.controls.update();
      _this.renderer.render(_this.scene, _this.camera);
    }
  }

  animate() {
    this.loop()
  }

  update(state) {
    this.scene.remove(
      this.scene.getObjectByName("all")
    );

    var MAP_COLORS = {
      0: 0x150026,
      1: 0x5e665d,
      2: 0xdb7011,
      3: 0x006600,
    };

    var ENTITIES_COLORS = {
      1: 0xaaaaaa,
      2: 0x006600,
      3: 0x660000,
      4: 0xff0000,
    };

    var geometry = new THREE.BoxGeometry(1, 1, 1);
    geometry.vertices.length = 0;
    geometry.faces.length = 0;

    for (var l = 0; l < state['lanes'].length; l++) {
      for (var s = 0; s < state['lanes'][l]['sections'].length; s++) {
        var section = state['lanes'][l]['sections'][s]
        for(var w = 0; w < section['slice'].length; w++) {
          var v0 = new THREE.Vector3(7*l + w, section['start'], 0);
          var v1 = new THREE.Vector3(7*l + w, section['end'], 0);
          var v2 = new THREE.Vector3(7*l + w + 1, section['start'], 0);
          var v3 = new THREE.Vector3(7*l + w + 1, section['end'], 0);
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
          f.color = new THREE.Color(MAP_COLORS[section['slice'][w]]);
          f.vertexColors = [f.color,f.color,f.color,f.color];
          geometry.faces.push(f);

          var f = new THREE.Face3(
            geometry.vertices.length-1,
            geometry.vertices.length-2,
            geometry.vertices.length-3,
            THREE.Vector3(0, 0, 1)
          );
          f.color = new THREE.Color(MAP_COLORS[section['slice'][w]]);
          f.vertexColors = [f.color,f.color,f.color,f.color];
          geometry.faces.push(f);
        }
      }
    }

    var render_entity = (entity, is_ego) => {
      var type = entity['type']
      var occupation = entity['occupation']

      var orientation = occupation['orientation']
      var l = occupation['lane']
      var position = occupation['position']
      var width = occupation['width']
      var height = occupation['height']

      // Forward orientation.
      var v0, v1, v2, v3;
      if (orientation == 1) {
        v0 = new THREE.Vector3(7*l + position[0], position[1], position[2]);
        v1 = new THREE.Vector3(7*l + position[0] + width, position[1], position[2]);
        v2 = new THREE.Vector3(7*l + position[0], position[1], position[2] + height);
        v3 = new THREE.Vector3(7*l + position[0] + width, position[1], position[2] + height);
      } else {
        v0 = new THREE.Vector3(7*l + position[0], position[1], position[2]);
        v1 = new THREE.Vector3(7*l + position[0], position[1] + width, position[2]);
        v2 = new THREE.Vector3(7*l + position[0], position[1], position[2] + height);
        v3 = new THREE.Vector3(7*l + position[0], position[1] + width, position[2] + height);
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
    };

    for (var e = 0; e < state['entities'].length; e++) {
      render_entity(state['entities'][e], false)
    }
    render_entity(state['ego'], true)

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
    var surface = new THREE.Mesh(geometry, material);
    surface.doubleSided = false;

    surface.position.x = -10;
    surface.position.y = -600;
    surface.position.z = 0;

    surface.rotation.y = 0
    surface.name = "all"

    this.scene.add(surface)
  }
}

export { StateViewer }
