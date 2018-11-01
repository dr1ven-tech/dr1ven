//
//  Metadata.swift
//  Stereoscopic
//
//  Created by Matthieu Rouif on 01/11/2018.
//  Copyright © 2018 Dr1ve. All rights reserved.
//

import Foundation

struct VideoMetadata {
    let metadata: Metadata
    var cameraCalibrationData: [CameraCalibration]
    var GNSSData: [GNSS]
    var IMUData: [IMU]
}

struct Metadata {
    let model: String
    let captureDevice: String
    let averageFPS: Float?
}

struct CameraCalibration {
    let exif: Dictionary<String, Any>
    let cameraIntrinsicData: Data
    let cameraDistorsionMatrix: Data?
}

struct GNSS {
    let timestamp: Date
    let latitude: Float
    let longitude: Float
    let accuracy: Float
}

struct IMU {
    let timestamp: Date
    let x: Float
    let y: Float
    let z: Float
}
