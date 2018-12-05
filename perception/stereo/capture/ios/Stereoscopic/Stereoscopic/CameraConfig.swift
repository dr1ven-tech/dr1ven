//
//  CameraConfig.swift
//  Stereoscopic
//
//  Created by Matthieu Rouif on 01/11/2018.
//  Copyright © 2018 Dr1ve. All rights reserved.
//

import Foundation
import AVFoundation

struct CameraConfig {
    let captureDevice: AVCaptureDevice.DeviceType
    let cameraPosition: AVCaptureDevice.Position
    
    static var teleCamera: CameraConfig {
        return CameraConfig(captureDevice: .builtInTelephotoCamera,
                            cameraPosition: .back)
    }
    static var dualCamera: CameraConfig {
        return CameraConfig(captureDevice: .builtInDualCamera,
            cameraPosition: .back)
    }    
}

