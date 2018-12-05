//
//  SettingsViewDataSource.swift
//  Stereoscopic
//
//  Created by Matthieu Rouif on 01/11/2018.
//  Copyright © 2018 Dr1ve. All rights reserved.
//

import UIKit

class SettingsViewDataSource: NSObject, UITableViewDataSource {
    override init() {
        cameraConfig = .teleCamera
    }
    
    var cameraConfig: CameraConfig!
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return 1
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "configIdentifier", for: indexPath)
        return cell 
    }
}
